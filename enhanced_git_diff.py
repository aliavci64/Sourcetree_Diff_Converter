#!/usr/bin/env python3
"""
Enhanced Git Diff to HTML Converter for SourceTree
Creates beautiful HTML reports of git diffs using diff2html library
Supports both single commit and commit comparison modes
"""

import os
import subprocess
import sys
import json
import html
import re
import platform
from datetime import datetime
from pathlib import Path
import argparse

class GitDiffAnalyzer:

    SUPPORTED_EXTENSIONS = ['.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.py', '.js', '.java']

    def __init__(self, repo_path, context_lines=3):
        self.repo_path = Path(repo_path).resolve()
        self.context_lines = context_lines
        
    def get_git_diff(self, commit1, commit2=None, file_path=None):
        """Get git diff output between commits - for .c files only"""
        cmd = ['git', '-C', str(self.repo_path), 'diff']
        
        if commit2:
            cmd.extend([commit1, commit2])
        else:
            cmd.extend([f'{commit1}^', commit1])
            
        cmd.extend([f'-U{self.context_lines}'])
        
        if file_path:
            # Sadece .c dosyası ise diff al
            if any(file_path.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                cmd.extend(['--', file_path])
            else:
                return ""
        else:
            # Tüm .c dosyaları için diff al
            for ext in self.SUPPORTED_EXTENSIONS:
                cmd.extend(['--', f'*{ext}'])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            return result.stdout
        except Exception as e:
            print(f"Error running git diff: {e}")
            return ""
    
    def get_changed_files(self, commit1, commit2=None):
        """Get list of changed files with their status - filtered for .c files only"""
        if commit2:
            cmd = ['git', '-C', str(self.repo_path), 'diff', '--name-status', commit1, commit2]
        else:
            cmd = ['git', '-C', str(self.repo_path), 'diff-tree', '--no-commit-id', '--name-status', '-r', commit1]
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, filename = parts
                        # Sadece .c uzantılı dosyaları ekle
                        if any(filename.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                            files.append({'status': status, 'filename': filename})
            return files
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def get_commit_info(self, commit):
        """Get commit information"""
        cmd = ['git', '-C', str(self.repo_path), 'show', '--no-patch', '--format=%H|%an|%ae|%ad|%s', commit]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            if result.stdout:
                parts = result.stdout.strip().split('|', 4)
                return {
                    'hash': parts[0][:8],
                    'author': parts[1],
                    'email': parts[2],
                    'date': parts[3],
                    'message': parts[4] if len(parts) > 4 else ''
                }
        except Exception as e:
            print(f"Error getting commit info: {e}")
        return None
    
    def get_file_stats(self, diff_content):
        """Extract file statistics from diff"""
        additions = len([line for line in diff_content.split('\n') if line.startswith('+')])
        deletions = len([line for line in diff_content.split('\n') if line.startswith('-')])
        return {'additions': additions, 'deletions': deletions}

class HTMLReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_html_report(self, diff_data, commit1_info, commit2_info=None, selected_files=None):
        """Create enhanced HTML report using diff2html"""
        
        # Generate unique output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.output_dir / f"git_diff_report_{timestamp}"
        report_dir.mkdir(exist_ok=True)
        
        html_file = report_dir / "diff_report.html"
        
        # Create the HTML content
        html_content = self._generate_html_content(diff_data, commit1_info, commit2_info, selected_files)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_file
    
    def _generate_html_content(self, diff_data, commit1_info, commit2_info=None, selected_files=None):
        """Generate the complete HTML content"""
        
        title = "Git Diff Report (.c files only)"
        if commit2_info:
            subtitle = f"Comparing {commit1_info['hash']} → {commit2_info['hash']} (C files only)"
        else:
            subtitle = f"Changes in {commit1_info['hash']} (C files only)"
            
        if selected_files:
            selected_count = len(selected_files)
            if selected_count == 1:
                subtitle += f" - {selected_count} file selected"
            else:
                subtitle += f" - {selected_count} files selected"
            
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/diff2html/bundles/css/diff2html.min.css" />
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/diff2html/bundles/js/diff2html-ui.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 2.5rem;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .commit-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .commit-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .commit-card h3 {{
            margin: 0 0 1rem 0;
            color: #333;
            font-size: 1.2rem;
        }}
        
        .commit-meta {{
            display: grid;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .commit-meta strong {{
            color: #333;
        }}
        
        .stats {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            text-align: center;
        }}
        
        .stat-item {{
            padding: 1rem;
            border-radius: 6px;
            background: #f8f9fa;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            display: block;
        }}
        
        .additions {{ color: #28a745; }}
        .deletions {{ color: #dc3545; }}
        .files {{ color: #6f42c1; }}
        
        .diff-container {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }}
        
        .controls {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 0.5rem;
            font-size: 0.9rem;
        }}
        
        .btn:hover {{
            background: #5a67d8;
        }}
        
        .file-filter {{
            margin-left: 1rem;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        @media (max-width: 768px) {{
            .commit-info {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    
    {self._generate_commit_info_html(commit1_info, commit2_info)}
    
    <div class="controls">
        <button class="btn" onclick="toggleFileView()">Toggle File View</button>
        <button class="btn" onclick="toggleWhitespace()">Toggle Whitespace</button>
        <button class="btn" onclick="toggleSideBySide()">Side by Side</button>
        <input type="text" class="file-filter" placeholder="Filter files..." onkeyup="filterFiles(this.value)">
    </div>
    
    {self._generate_stats_html(diff_data)}
    
    <div class="diff-container">
        <div id="diff-content"></div>
    </div>
    
    <script>
        // Diff data
        const diffData = {json.dumps(diff_data, ensure_ascii=False)};
        
        // Initialize diff2html
        document.addEventListener('DOMContentLoaded', function() {{
            const targetElement = document.getElementById('diff-content');
            const configuration = {{
                drawFileList: true,
                fileListToggle: true,
                fileListStartVisible: true,
                fileContentToggle: true,
                matching: 'lines',
                outputFormat: 'side-by-side',
                synchronisedScroll: true,
                highlight: true,
                renderNothingWhenEmpty: false,
            }};
            
            const diff2htmlUi = new Diff2HtmlUI(targetElement, diffData, configuration);
            diff2htmlUi.draw();
            
            // Store reference for controls
            window.diff2htmlUi = diff2htmlUi;
        }});
        
        // Control functions
        let currentView = 'side-by-side';
        let showWhitespace = false;
        
        function toggleSideBySide() {{
            currentView = currentView === 'side-by-side' ? 'line-by-line' : 'side-by-side';
            redrawDiff();
        }}
        
        function toggleWhitespace() {{
            showWhitespace = !showWhitespace;
            redrawDiff();
        }}
        
        function toggleFileView() {{
            const fileList = document.querySelector('.d2h-file-list');
            if (fileList) {{
                fileList.style.display = fileList.style.display === 'none' ? 'block' : 'none';
            }}
        }}
        
        function filterFiles(filterText) {{
            const files = document.querySelectorAll('.d2h-file-wrapper');
            files.forEach(file => {{
                const fileName = file.querySelector('.d2h-file-name');
                if (fileName) {{
                    const shouldShow = fileName.textContent.toLowerCase().includes(filterText.toLowerCase());
                    file.style.display = shouldShow ? 'block' : 'none';
                }}
            }});
        }}
        
        function redrawDiff() {{
            const targetElement = document.getElementById('diff-content');
            const configuration = {{
                drawFileList: true,
                fileListToggle: true,
                fileListStartVisible: true,
                fileContentToggle: true,
                matching: 'lines',
                outputFormat: currentView,
                synchronisedScroll: true,
                highlight: true,
                renderNothingWhenEmpty: false,
                diffMaxChanges: undefined,
                diffMaxLineLength: undefined,
                diffTooBigMessage: function(files) {{ return 'Diff too big to display'; }}
            }};
            
            targetElement.innerHTML = '';
            const diff2htmlUi = new Diff2HtmlUI(targetElement, diffData, configuration);
            diff2htmlUi.draw();
            window.diff2htmlUi = diff2htmlUi;
        }}
    </script>
</body>
</html>
        """
    
    def _generate_commit_info_html(self, commit1_info, commit2_info=None):
        """Generate HTML for commit information"""
        if commit2_info:
            return f"""
            <div class="commit-info">
                <div class="commit-card">
                    <h3>From Commit</h3>
                    <div class="commit-meta">
                        <div><strong>Hash:</strong> {commit1_info['hash']}</div>
                        <div><strong>Author:</strong> {html.escape(commit1_info['author'])}</div>
                        <div><strong>Date:</strong> {commit1_info['date']}</div>
                        <div><strong>Message:</strong> {html.escape(commit1_info['message'])}</div>
                    </div>
                </div>
                <div class="commit-card">
                    <h3>To Commit</h3>
                    <div class="commit-meta">
                        <div><strong>Hash:</strong> {commit2_info['hash']}</div>
                        <div><strong>Author:</strong> {html.escape(commit2_info['author'])}</div>
                        <div><strong>Date:</strong> {commit2_info['date']}</div>
                        <div><strong>Message:</strong> {html.escape(commit2_info['message'])}</div>
                    </div>
                </div>
            </div>
            """
        else:
            return f"""
            <div class="commit-info">
                <div class="commit-card" style="grid-column: 1 / -1; max-width: 600px; margin: 0 auto;">
                    <h3>Commit Information</h3>
                    <div class="commit-meta">
                        <div><strong>Hash:</strong> {commit1_info['hash']}</div>
                        <div><strong>Author:</strong> {html.escape(commit1_info['author'])}</div>
                        <div><strong>Date:</strong> {commit1_info['date']}</div>
                        <div><strong>Message:</strong> {html.escape(commit1_info['message'])}</div>
                    </div>
                </div>
            </div>
            """
    
    def _generate_stats_html(self, diff_data):
        """Generate HTML for diff statistics"""
        # Count total stats from diff data
        total_additions = 0
        total_deletions = 0
        total_files = len(diff_data.split('diff --git')) - 1 if diff_data else 0
        
        for line in diff_data.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                total_additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                total_deletions += 1
        
        return f"""
        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-number files">{total_files}</span>
                    <div>Files Changed</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number additions">+{total_additions}</span>
                    <div>Additions</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number deletions">-{total_deletions}</span>
                    <div>Deletions</div>
                </div>
            </div>
        </div>
        """

def show_file_selector(changed_files, commit1_info, commit2_info, output_dir):
    """Show interactive file selector and return selected files"""
    import tempfile
    import time
    import webbrowser
    
    # Create temporary directory for selector
    selector_dir = Path(output_dir) / "temp_selector"
    selector_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the selector HTML file
    selector_html_path = selector_dir / "file_selector.html"
    
    # Prepare data for the selector
    files_data = []
    for file_info in changed_files:
        files_data.append({
            'filename': file_info['filename'],
            'status': file_info['status'],
            'additions': 0,
            'deletions': 0
        })
    
    commit_data = {
        'commit1': {
            'hash': commit1_info['hash'],
            'message': commit1_info['message'],
            'author': commit1_info['author']
        }
    }
    
    if commit2_info:
        commit_data['commit2'] = {
            'hash': commit2_info['hash'], 
            'message': commit2_info['message'],
            'author': commit2_info['author']
        }
    
    # Create simplified HTML selector
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Files for Diff Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2rem; font-weight: 300; margin-bottom: 0.5rem; }}
        .header p {{ opacity: 0.9; font-size: 1.1rem; }}
        .controls {{ padding: 1.5rem; border-bottom: 1px solid #dee2e6; background: #f8f9fa; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }}
        .btn {{ background: #667eea; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s; }}
        .btn:hover {{ background: #5a67d8; transform: translateY(-2px); }}
        .btn-success {{ background: #28a745; }}
        .btn-success:hover {{ background: #218838; }}
        .selection-summary {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: 1rem 1.5rem; margin: 1rem 1.5rem; border-radius: 0 8px 8px 0; }}
        .file-list {{ max-height: 60vh; overflow-y: auto; }}
        .file-item {{ display: flex; align-items: center; padding: 1rem 1.5rem; border-bottom: 1px solid #f1f3f4; cursor: pointer; transition: background-color 0.2s; }}
        .file-item:hover {{ background: #f8f9fa; }}
        .file-item.selected {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
        .file-checkbox {{ margin-right: 1rem; width: 18px; height: 18px; cursor: pointer; }}
        .file-status {{ margin-right: 1rem; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; min-width: 60px; text-align: center; }}
        .status-A {{ background: #d4edda; color: #155724; }}
        .status-M {{ background: #fff3cd; color: #856404; }}
        .status-D {{ background: #f8d7da; color: #721c24; }}
        .file-path {{ flex: 1; font-family: 'Courier New', monospace; font-size: 0.9rem; color: #495057; }}
        .generate-section {{ padding: 2rem 1.5rem; text-align: center; background: #f8f9fa; }}
        .generate-btn {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); font-size: 1.1rem; padding: 1rem 2rem; border-radius: 10px; }}
        .generate-btn:disabled {{ background: #6c757d; cursor: not-allowed; }}
        .commit-info {{ padding: 1rem 1.5rem; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
        .commit-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
        .commit-hash {{ font-family: monospace; background: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.9rem; }}
        .commit-message {{ flex: 1; margin: 0 1rem; font-weight: 500; }}
        .commit-author {{ color: #6c757d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📂 Select Files for Diff Report</h1>
            <p>Choose which .c files to include in your comparison report</p>
        </div>
        
        <div class="commit-info">
            <div class="commit-row">
                <span class="commit-hash">{commit1_info['hash']}</span>
                <span class="commit-message">{commit1_info['message'][:50]}...</span>
                <span class="commit-author">{commit1_info['author']}</span>
            </div>
            {"<div class='commit-row'><span class='commit-hash'>" + commit2_info['hash'] + "</span><span class='commit-message'>" + commit2_info['message'][:50] + "...</span><span class='commit-author'>" + commit2_info['author'] + "</span></div>" if commit2_info else ""}
        </div>
        
        <div class="controls">
            <button class="btn" onclick="selectAll()">✅ Select All</button>
            <button class="btn" onclick="selectNone()">❌ Clear All</button>
        </div>
        
        <div class="selection-summary" id="selectionSummary">
            <strong>0 files selected</strong> - Select files to generate your diff report
        </div>
        
        <div class="file-list" id="fileList"></div>
        
        <div class="generate-section">
            <button class="btn generate-btn" id="generateBtn" onclick="generateReport()" disabled>
                🚀 Generate Report for Selected Files
            </button>
            <div style="margin-top: 1rem;">
                <small style="color: #6c757d;">Close this window after making your selection</small>
            </div>
        </div>
    </div>

    <script>
        const filesData = {json.dumps(files_data)};
        let selectedFiles = [];
        
        function renderFileList() {{
            const fileListDiv = document.getElementById('fileList');
            let html = '';
            
            filesData.forEach((file, index) => {{
                const statusClass = 'status-' + file.status;
                const statusText = {{'A': 'Added', 'M': 'Modified', 'D': 'Deleted'}}[file.status] || file.status;
                const isSelected = selectedFiles.includes(file.filename);
                
                html += `
                    <div class="file-item ${{isSelected ? 'selected' : ''}}" onclick="toggleFile('${{file.filename}}')">
                        <input type="checkbox" class="file-checkbox" ${{isSelected ? 'checked' : ''}} onclick="event.stopPropagation();">
                        <span class="file-status ${{statusClass}}">${{statusText}}</span>
                        <span class="file-path">${{file.filename}}</span>
                    </div>
                `;
            }});
            
            fileListDiv.innerHTML = html;
            updateSelectionSummary();
        }}
        
        function toggleFile(filename) {{
            const index = selectedFiles.indexOf(filename);
            if (index > -1) {{
                selectedFiles.splice(index, 1);
            }} else {{
                selectedFiles.push(filename);
            }}
            renderFileList();
        }}
        
        function selectAll() {{
            selectedFiles = filesData.map(f => f.filename);
            renderFileList();
        }}
        
        function selectNone() {{
            selectedFiles = [];
            renderFileList();
        }}
        
        function updateSelectionSummary() {{
            const summaryDiv = document.getElementById('selectionSummary');
            const generateBtn = document.getElementById('generateBtn');
            
            if (selectedFiles.length === 0) {{
                summaryDiv.innerHTML = '<strong>0 files selected</strong> - Select files to generate your diff report';
                generateBtn.disabled = true;
            }} else {{
                summaryDiv.innerHTML = `<strong>${{selectedFiles.length}} of ${{filesData.length}} files selected</strong> - Ready to generate report`;
                generateBtn.disabled = false;
            }}
        }}
        
        function generateReport() {{
            if (selectedFiles.length === 0) {{
                alert('Please select at least one file.');
                return;
            }}
            
            // Save selection to a file that Python can read
            const data = {{
                selectedFiles: selectedFiles,
                timestamp: new Date().toISOString()
            }};
            
            // Create download link for selection
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'selected_files.json';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            // Update UI
            const generateBtn = document.getElementById('generateBtn');
            generateBtn.innerHTML = '✅ Selection Saved - You can close this window';
            generateBtn.disabled = true;
            generateBtn.style.background = '#28a745';
            
            alert('File selection saved! Close this window and check your Downloads folder for selected_files.json');
        }}
        
        // Initialize
        renderFileList();
    </script>
</body>
</html>'''
    
    # Write HTML file
    with open(selector_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in browser
    print(f"🌐 Opening file selector in browser: {selector_html_path}")
    
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', str(selector_html_path)], check=False)
        else:
            webbrowser.open(f'file://{selector_html_path}')
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"Please manually open: {selector_html_path}")
    
    # Wait for user to make selection
    print("\n⏳ Please select files in the browser window and click 'Generate Report'")
    print("📂 After selection, check your Downloads folder for 'selected_files.json'")
    
    # Wait for selection file
    downloads_path = Path.home() / "Downloads" / "selected_files.json"
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if downloads_path.exists():
            try:
                with open(downloads_path, 'r') as f:
                    selection_data = json.load(f)
                
                selected_filenames = selection_data.get('selectedFiles', [])
                
                # Filter original files based on selection
                selected_files = [f for f in changed_files if f['filename'] in selected_filenames]
                
                # Clean up
                downloads_path.unlink()
                try:
                    selector_html_path.unlink()
                    selector_dir.rmdir()
                except:
                    pass
                
                return selected_files
                
            except Exception as e:
                print(f"Error reading selection file: {e}")
                break
        
        time.sleep(1)
    
    # Cleanup on timeout
    try:
        selector_html_path.unlink()
        selector_dir.rmdir()
    except:
        pass
    
    print("⚠️  Selection timeout. Using all files...")
    return changed_files

def main():
    parser = argparse.ArgumentParser(description='Enhanced Git Diff to HTML Converter for SourceTree')
    parser.add_argument('commit1', help='First commit hash')
    parser.add_argument('commit2', help='Second commit hash OR repository path (if only one commit)')
    parser.add_argument('repo_path', help='Repository path OR output directory')
    parser.add_argument('output_dir', nargs='?', help='Output directory (optional if 3 args provided)')
    parser.add_argument('--context', '-c', type=int, default=3, help='Number of context lines (default: 3)')
    
    args = parser.parse_args()
    
    # Parametre sayısına göre doğru sıralamayı belirle
    if args.output_dir is None:
        # 3 parametre: commit1, repo_path, output_dir
        actual_commit1 = args.commit1
        actual_commit2 = None
        actual_repo_path = args.commit2
        actual_output_dir = args.repo_path
    else:
        # 4 parametre: commit1, commit2, repo_path, output_dir
        actual_commit1 = args.commit1
        actual_commit2 = args.commit2
        actual_repo_path = args.repo_path
        actual_output_dir = args.output_dir
    
    # Debug output ve log dosyası oluşturma
    log_file = Path(actual_output_dir).parent / "git_diff_log.txt"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"🔍 Debug Info - {datetime.now()}\n")
            f.write(f"   Args received: {sys.argv}\n")
            f.write(f"   Commit1: {actual_commit1}\n")
            f.write(f"   Commit2: {actual_commit2}\n")  
            f.write(f"   Repo Path: {actual_repo_path}\n")
            f.write(f"   Output Dir: {actual_output_dir}\n")
            f.write(f"   Context: {args.context}\n")
            f.write(f"   Current Working Dir: {os.getcwd()}\n")
            f.write(f"   Repo Path Exists: {Path(actual_repo_path).exists()}\n")
    except:
        pass
        
    print(f"🔍 Debug Info:")
    print(f"   Raw args: {sys.argv}")
    print(f"   Commit1: {actual_commit1}")
    print(f"   Commit2: {actual_commit2}")  
    print(f"   Repo Path: {actual_repo_path}")
    print(f"   Output Dir: {actual_output_dir}")
    print(f"   Context: {args.context}")
    print(f"   Log dosyası: {log_file}")
    
    try:
        # Initialize analyzer
        analyzer = GitDiffAnalyzer(actual_repo_path, args.context)
        
        # Get diff data
        print("Generating diff data...")
        diff_data = analyzer.get_git_diff(actual_commit1, actual_commit2)
        
        if not diff_data.strip():
            print("No differences found between the specified commits.")
            return
        
        # Get commit information
        print("Getting commit information...")
        commit1_info = analyzer.get_commit_info(actual_commit1)
        commit2_info = analyzer.get_commit_info(actual_commit2) if actual_commit2 else None
        
        if not commit1_info:
            print(f"Could not retrieve information for commit {actual_commit1}")
            return
            
        if actual_commit2 and not commit2_info:
            print(f"Could not retrieve information for commit {actual_commit2}")
            return
        
        # Get changed .c files
        print("Getting changed .c files...")
        changed_files = analyzer.get_changed_files(actual_commit1, actual_commit2)
        
        if not changed_files:
            print("❌ No .c files found with changes between the specified commits.")
            print("   This script only processes files with .c extension.")
            return
        
        print(f"📁 Found {len(changed_files)} changed .c files:")
        for file_info in changed_files:
            status_desc = {"A": "Added", "D": "Deleted", "M": "Modified", "R": "Renamed"}
            status = status_desc.get(file_info['status'], file_info['status'])
            print(f"   [{status}] {file_info['filename']}")
        
        # Interactive file selection if more than 1 file
        selected_files = changed_files
        if len(changed_files) > 1:
            print("\n🎯 Multiple files found. Opening file selector...")
            selected_files = show_file_selector(changed_files, commit1_info, commit2_info, actual_output_dir)
            
            if not selected_files:
                print("❌ No files selected. Exiting...")
                return
                
            print(f"✅ Selected {len(selected_files)} files for report generation")
        
        # Generate diff only for selected files
        print("Generating diff data for selected files...")
        diff_data = ""
        for file_info in selected_files:
            file_diff = analyzer.get_git_diff(actual_commit1, actual_commit2, file_info['filename'])
            if file_diff.strip():
                diff_data += file_diff + "\n"
        
        if not diff_data.strip():
            print("❌ No diff data generated for selected files.")
            return
        
        # Generate HTML report
        print("Generating HTML report...")
        report_generator = HTMLReportGenerator(actual_output_dir)
        html_file = report_generator.create_html_report(diff_data, commit1_info, commit2_info, selected_files)
        
        print(f"✅ HTML report generated successfully!")
        print(f"📁 Report location: {html_file}")
        print(f"🌐 Open in browser: file://{html_file.absolute()}")
        
        # Try to open in default browser (optional)
        try:
            import webbrowser
            
            if platform.system() == 'Darwin':  # macOS
                # Use 'open' command on macOS for better compatibility
                subprocess.run(['open', str(html_file.absolute())], check=False)
                print("🚀 Report opened in default browser")
            else:
                webbrowser.open(f'file://{html_file.absolute()}')
                print("🚀 Report opened in default browser")
        except Exception as e:
            print(f"Could not auto-open browser: {e}")
            print(f"Please manually open: {html_file.absolute()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()