#!/usr/bin/env python3
"""
Cross-Platform Setup and Configuration Tool
Automatically detects platform and generates SourceTree configurations
"""

import platform
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime 

def main():
    """Wrapper main function"""
    print("🔍 Starting setup...")
    try:
        detect_and_setup()
    except Exception as e:
        print(f"💥 Error in setup: {e}")
        import traceback
        traceback.print_exc()

def detect_and_setup():
    """Main setup function"""
    print("🚀 Enhanced Git Diff - Cross-Platform Setup")
    print("=" * 50)

def print_windows_instructions(python_path, script_path, output_dir):
    """Print Windows-specific instructions with generic paths"""
    
    # Generic paths for display
    generic_python = "python" if "python.exe" in str(python_path).lower() else "python3"
    generic_script = "C:\\path\\to\\your\\enhanced_git_diff.py"
    generic_output = "C:\\Users\\YourUsername\\Desktop\\GitDiffReports"
    
    print(f"""
🪟 WINDOWS SOURCETREE SETUP:

1. Open SourceTree → Tools → Options → Custom Actions
2. Click "Add" button
3. Fill in these details:

   Menu Caption: Enhanced Git Diff Report
   Script to run: {generic_python}
   Parameters: "{generic_script}" $SHA $REPO "{generic_output}" --context 5
   ☑️ Open in separate window
   ☑️ Show full output

4. For two-commit comparison, create another action:
   Menu Caption: Compare Two Commits  
   Parameters: "{generic_script}" $SHA1 $SHA2 $REPO "{generic_output}" --context 5

💡 YOUR SPECIFIC PATHS:
   Python: {python_path}
   Script: {script_path}
   Output: {output_dir}

🔧 Troubleshooting:
   - If Python not found, try: py -3 or full path to python.exe
   - Make sure Git is accessible from command line
   - Test manually: {generic_python} "{generic_script}" --help
""")

def print_mac_instructions(python_path, script_path, output_dir):
    """Print macOS-specific instructions with generic paths"""
    
    # Generic paths for display
    generic_python = "python3"
    generic_script = "/Users/YourUsername/path/to/enhanced_git_diff.py"
    generic_output = "/Users/YourUsername/Desktop/GitDiffReports"
    
    print(f"""
🍎 MACOS SOURCETREE SETUP:

1. Open SourceTree → Preferences → Custom Actions
2. Click "+" button  
3. Fill in these details:

   Menu Caption: Enhanced Git Diff Report
   Script to run: {generic_python}
   Parameters: "{generic_script}" $SHA $REPO "{generic_output}" --context 5
   ☑️ Open in separate window
   ☑️ Show full output

4. For two-commit comparison:
   Menu Caption: Compare Two Commits
   Parameters: "{generic_script}" $SHA1 $SHA2 $REPO "{generic_output}" --context 5

💡 YOUR SPECIFIC PATHS:
   Python: {python_path}
   Script: {script_path}  
   Output: {output_dir}

🔧 Troubleshooting:
   - If permission denied: chmod +x "{generic_script}"
   - Alternative Python: /usr/bin/python3 or /opt/homebrew/bin/python3
   - Test manually: {generic_python} "{generic_script}" --help
""")

def print_linux_instructions(python_path, script_path, output_dir):
    """Print Linux-specific instructions with generic paths"""
    
    # Generic paths for display
    generic_python = "python3"
    generic_script = "/home/yourusername/path/to/enhanced_git_diff.py"
    generic_output = "/home/yourusername/Desktop/GitDiffReports"
    
    print(f"""
🐧 LINUX SOURCETREE SETUP:

1. Open SourceTree → Tools → Options → Custom Actions  
2. Click "Add" button
3. Fill in these details:

   Menu Caption: Enhanced Git Diff Report
   Script to run: {generic_python}
   Parameters: "{generic_script}" $SHA $REPO "{generic_output}" --context 5
   ☑️ Open in separate window

4. For two-commit comparison:
   Menu Caption: Compare Two Commits
   Parameters: "{generic_script}" $SHA1 $SHA2 $REPO "{generic_output}" --context 5

💡 YOUR SPECIFIC PATHS:
   Python: {python_path}
   Script: {script_path}
   Output: {output_dir}

🔧 Troubleshooting:
   - Install Python 3: sudo apt install python3
   - Make executable: chmod +x "{generic_script}"
   - Test manually: {generic_python} "{generic_script}" --help
""")

def detect_and_setup():
    """Main setup function"""
    print("🚀 Enhanced Git Diff - Cross-Platform Setup")
    print("=" * 50)
    
    # Platform detection
    system = platform.system()
    print(f"🖥️  Detected platform: {system}")
    
    # Script location
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "enhanced_git_diff.py"
    
    if not main_script.exists():
        print("❌ enhanced_git_diff.py not found in the same directory!")
        return False
    
    print(f"📁 Script location: {main_script}")
    
    # Python detection
    python_path = find_best_python()
    print(f"🐍 Best Python: {python_path}")
    
    # Test the environment
    if test_environment(python_path, main_script):
        print("✅ Environment validation passed!")
    else:
        print("⚠️  Environment validation failed, but continuing...")
    
    # Generate SourceTree configuration
    generate_sourcetree_instructions(system, python_path, main_script)
    
    return True

def find_best_python():
    """Find the best Python executable"""
    candidates = [
        sys.executable,  # Current Python
        shutil.which('python3'),
        shutil.which('python'),
        shutil.which('py'),  # Windows py launcher
    ]
    
    for candidate in candidates:
        if candidate and test_python(candidate):
            return candidate
    
    # Fallback
    return sys.executable

def test_python(python_path):
    """Test if Python path works with required modules"""
    try:
        test_cmd = [
            python_path, '-c', 
            'import subprocess, pathlib, json, platform, argparse; print("✅ OK")'
        ]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and '✅ OK' in result.stdout
    except:
        return False

def test_environment(python_path, script_path):
    """Test the complete environment"""
    print("\n🧪 Testing environment...")
    
    # Test Python modules
    try:
        test_cmd = [python_path, str(script_path), '--help']
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Script execution: OK")
            return True
        else:
            print(f"❌ Script execution failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def generate_sourcetree_instructions(system, python_path, script_path):
    """Generate platform-specific SourceTree instructions"""
    
    # Default output directory
    if system == 'Windows':
        output_dir = str(Path.home() / "Desktop" / "GitDiffReports")
    else:
        output_dir = str(Path.home() / "Desktop" / "GitDiffReports")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"📂 Output directory created: {output_dir}")
    
    print("\n" + "=" * 60)
    print("📋 SOURCETREE CONFIGURATION")
    print("=" * 60)
    
    if system == 'Windows':
        print_windows_instructions(python_path, script_path, output_dir)
    elif system == 'Darwin':  # macOS
        print_mac_instructions(python_path, script_path, output_dir)
    else:  # Linux
        print_linux_instructions(python_path, script_path, output_dir)
    
    # Save configuration
    config = {
        'platform': system,
        'python_path': str(python_path),
        'script_path': str(script_path),
        'output_dir': output_dir,
        'tested': True,
        'setup_date': str(datetime.now())
    }
    
    config_file = script_path.parent / 'platform_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: {config_file}")
    
if __name__ == "__main__":
    main()  

    