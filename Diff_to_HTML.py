import os
import subprocess
import re
import sys
import html

oneArgument = False #Sourcetree üzerinde seçilen argüman sayısını kontrol eden boolean ifade

#bir git fonksiyonu olan diff fonksiyonunu kullanarak iki versiyon arasındaki farklılıkları tespit eder
def get_git_diff(commit1, commit2, repo_path, file_name):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'diff', '-U0', commit1, commit2, '--', file_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
        )
        return result.stdout
    except Exception as e:
        return str(e)

#Bir git fonksiyonu olan show fonksiyonu ile commit'teki dosyaların içeriğini alır
def get_file_content_at_commit(commit, repo_path, file_name):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'show', f'{commit}:{file_name}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
        )
        if result.stderr:
            print(f"Error getting file content for {file_name} at {commit}: {result.stderr}")
        return result.stdout
    except Exception as e:
        return str(e)

def extract_function_names(diff):
    function_names = set()
    pattern = re.compile(r'^@@.*@@\s*(def|function)\\s*([a-zA-Z_][a-zA-Z0-9_]*)')
    for line in diff.splitlines():
        match = pattern.match(line)
        if match:
            function_names.add(match.group(2))
    return function_names

#Farklılıkların yazdırıldığı fonksiyon
def write_diff_to_html(diffs, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('<html><head><style>')
            f.write('body { font-family: Courier, monospace; }')
            f.write('.line-num { display: inline-block; width: 40px; }')
            f.write('.added { background-color: #eaffea; color: green; }')
            f.write('.removed { background-color: #ffecec; color: red; }')
            f.write('table { width: 100%; border-collapse: collapse; }')
            f.write('td, th { border: 1px solid #ddd; padding: 8px; vertical-align: top; white-space: pre-wrap; }')
            f.write('th { background-color: #f2f2f2; }')
            f.write('</style></head><body>')

            for diff_data in diffs:
                diff = diff_data['diff']
                file_name = diff_data['file_name']
                file_status = diff_data['file_status']
                file_content = diff_data['file_content']

                f.write(f'<h2>{html.escape(file_name)} Dosyasındaki Farklılıklar:</h2>')

                if oneArgument: #Tek commit seçildiyse
                    if file_status == 'A': #Eğer dosya "Added File" olarak nitelendirilmiş ise
                        f.write(f'<p><b>File added: {html.escape(file_name)}</b></p>')
                        f.write('<table><tr><th>New Version</th></tr><tr><td class="added"><pre>')
                        for i, line in enumerate(file_content.splitlines(), 1):
                            f.write(f'<span class="line-num">{i}</span> + {html.escape(line.strip())}\n')
                        f.write('</pre></td></tr></table>')
                    elif file_status == 'D': #Eğer dosya "Deleted File" olarak nitelendirilmişse 
                        f.write(f'<p><b>File deleted: {html.escape(file_name)}</b></p>')
                        f.write('<table><tr><th>Old Version</th></tr><tr><td class="removed"><pre>')
                        for i, line in enumerate(file_content.splitlines(), 1):
                            f.write(f'<span class="line-num">{i}</span> - {html.escape(line.strip())}\n')
                        f.write('</pre></td></tr></table>')
                    else: #Dosya "Editted File" ise
                        lines = diff.splitlines()
                        lines = [line for line in lines if not (line.startswith('diff --git') or line.startswith('index ') or line.startswith('--- ') or line.startswith('+++ '))]
                        difference_count = sum(1 for line in lines if line.startswith('-') or line.startswith('+'))
                        function_names = extract_function_names(diff)

                        f.write(f'<p><b>Farklılık Sayısı: {difference_count}</b></p>')
                        f.write(f'<p><b>Farklılık Olan Fonksiyonlar: {", ".join(function_names)}</b></p>')

                        f.write('<table><tr><th>Old Version</th><th>New Version</th></tr>')

                        old_line_num = 0
                        new_line_num = 0

                        for line in lines:
                            if line.startswith('@@'):
                                parts = line.split(' ')
                                old_line_num = int(parts[1].split(',')[0][1:])
                                new_line_num = int(parts[2].split(',')[0][1:])
                                f.write('<tr><td colspan="2"><hr></td></tr>')
                            elif line.startswith('+'):
                                f.write(f'<tr><td class="removed"><pre><span class="line-num">{old_line_num}</span> - {html.escape(line[1:])}</pre></td><td></td></tr>')
                                old_line_num += 1
                            elif line.startswith('-'):
                                f.write(f'<tr><td></td><td class="added"><pre><span class="line-num">{new_line_num}</span> + {html.escape(line[1:])}</pre></td></tr>')
                                new_line_num += 1
                            else:
                                f.write(f'<tr><td><pre><span class="line-num">{old_line_num}</span> {html.escape(line)}</pre></td><td><pre><span class="line-num">{html.escape(new_line_num)}</span> {html.escape(line)}</pre></td></tr>')
                                old_line_num += 1
                                new_line_num += 1

                        f.write('</table>')

                else: #İki commit seçildiyse
                    if file_status == 'D':
                        f.write(f'<p><b>File added: {html.escape(file_name)}</b></p>')
                        f.write('<table><tr><th>New Version</th></tr><tr><td class="added"><pre>')
                        for i, line in enumerate(file_content.splitlines(), 1):
                            f.write(f'<span class="line-num">{i}</span> + {html.escape(line.strip())}\n')
                        f.write('</pre></td></tr></table>')
                    elif file_status == 'A':
                        f.write(f'<p><b>File deleted: {html.escape(file_name)}</b></p>')
                        f.write('<table><tr><th>Old Version</th></tr><tr><td class="removed"><pre>')
                        for i, line in enumerate(file_content.splitlines(), 1):
                            f.write(f'<span class="line-num">{i}</span> - {html.escape(line.strip())}\n')
                        f.write('</pre></td></tr></table>')
                    else:
                        lines = diff.splitlines()
                        lines = [line for line in lines if not (line.startswith('diff --git') or line.startswith('index ') or line.startswith('--- ') or line.startswith('+++ '))]
                        difference_count = sum(1 for line in lines if line.startswith('-') or line.startswith('+'))
                        function_names = extract_function_names(diff)

                        f.write(f'<p><b>Farklılık Sayısı: {difference_count}</b></p>')
                        f.write(f'<p><b>Farklılık Olan Fonksiyonlar: {", ".join(function_names)}</b></p>')

                        f.write('<table><tr><th>Old Version</th><th>New Version</th></tr>')

                        old_line_num = 0
                        new_line_num = 0

                        for line in lines:
                            if line.startswith('@@'):
                                parts = line.split(' ')
                                old_line_num = int(parts[1].split(',')[0][1:])
                                new_line_num = int(parts[2].split(',')[0][1:])
                                f.write('<tr><td colspan="2"><hr></td></tr>')
                            elif line.startswith('+'):
                                f.write(f'<tr><td class="removed"><pre><span class="line-num">{old_line_num}</span> - {html.escape(line[1:])}</pre></td><td></td></tr>')
                                old_line_num += 1
                            elif line.startswith('-'):
                                f.write(f'<tr><td></td><td class="added"><pre><span class="line-num">{new_line_num}</span> + {html.escape(line[1:])}</pre></td></tr>')
                                new_line_num += 1
                            else:
                                f.write(f'<tr><td><pre><span class="line-num">{old_line_num}</span> {html.escape(line)}</pre></td><td><pre><span class="line-num">{html.escape(new_line_num)}</span> {html.escape(line)}</pre></td></tr>')
                                old_line_num += 1
                                new_line_num += 1

                        f.write('</table>')

            f.write('</body></html>')
    except Exception as e:
        print(f"HTML dosyasına yazarken hata oluştu: {e}")

def get_changed_files(commit1, commit2, repo_path):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'diff', '--name-status', commit1, commit2],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
        )
        return result.stdout.splitlines()
    except Exception as e:
        return str(e)

def get_commit_diff(commit, repo_path):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'diff-tree', '--no-commit-id', '--name-status', '-r', commit],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
        )
        return result.stdout.splitlines()
    except Exception as e:
        return str(e)

#
def convert_path(path):
    return path.replace('\\', '/')

def create_unique_output_dir(base_dir):
    counter = 1
    new_dir = base_dir
    while os.path.exists(new_dir):
        new_dir = f"{base_dir} ({counter})"
        counter += 1
    os.makedirs(new_dir)
    return new_dir

if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python diff_to_html.py <commit1> [<commit2>] <repo_path> <output_dir>")
        sys.exit(1)
    
    commit1 = sys.argv[1]
    if len(sys.argv) == 5:
        oneArgument = False
        commit2 = sys.argv[2]
        repo_path = convert_path(sys.argv[3])
        output_dir = convert_path(sys.argv[4])
    else:
        oneArgument = True
        commit2 = None
        repo_path = convert_path(sys.argv[2])
        output_dir = convert_path(sys.argv[3])

    print(f"Converted repo_path: {repo_path}")
    print(f"Converted output_dir: {output_dir}")

    differences_dir = create_unique_output_dir(os.path.join(repo_path, "Differences"))
    output_file = os.path.join(differences_dir, "combined_diff.html")

    if commit2:
        changed_files = get_changed_files(commit1, commit2, repo_path)
    else:
        changed_files = get_commit_diff(commit1, repo_path)

    diffs = []
    for line in changed_files:
        status, file_name = line.split(maxsplit=1)
        if file_name.endswith('.c') or file_name.endswith('.h') or file_name.endswith('.py'):
            if status == 'A':
                file_content = get_file_content_at_commit(commit2, repo_path, file_name)
                diffs.append({'diff': '', 'file_name': file_name, 'file_status': 'A', 'file_content': file_content})
            elif status == 'D':
                file_content = get_file_content_at_commit(commit1, repo_path, file_name)
                diffs.append({'diff': '', 'file_name': file_name, 'file_status': 'D', 'file_content': file_content})
            else:
                diff = get_git_diff(commit1, commit2 if commit2 else commit1 + '^', repo_path, file_name)
                diffs.append({'diff': diff, 'file_name': file_name, 'file_status': '', 'file_content': ''})

    write_diff_to_html(diffs, output_file)

    print(f"Farklılıklar {differences_dir} klasöründe combined_diff.html olarak yazıldı.")
