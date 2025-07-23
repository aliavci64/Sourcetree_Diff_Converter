#!/usr/bin/env python3
"""
Environment Testing Tool
Tests the complete setup on current platform
"""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all environment tests"""
    print("🧪 Testing Enhanced Git Diff Environment")
    print("=" * 40)
    
    script_path = Path(__file__).parent / "enhanced_git_diff.py"
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Modules", test_modules),
        ("Script Syntax", lambda: test_script_syntax(script_path)),
        ("Git Access", test_git_access),
        ("File System", test_file_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your environment is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

def test_python_version():
    """Test Python version compatibility"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"   Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   Python {version.major}.{version.minor} - Need 3.6+")
        return False

def test_modules():
    """Test required module imports"""
    required_modules = [
        'subprocess', 'pathlib', 'json', 'platform', 
        'argparse', 'datetime', 'os', 'sys'
    ]
    
    failed_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            failed_modules.append(module)
    
    if failed_modules:
        print(f"   Missing: {', '.join(failed_modules)}")
        return False
    else:
        print(f"   All {len(required_modules)} modules available")
        return True

def test_script_syntax(script_path):
    """Test if main script has valid syntax"""
    if not script_path.exists():
        print(f"   Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', str(script_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Syntax validation passed")
            return True
        else:
            print(f"   Syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   Could not validate syntax: {e}")
        return False

def test_git_access():
    """Test Git command availability"""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   {result.stdout.strip()}")
            return True
        else:
            print("   Git not accessible")
            return False
    except:
        print("   Git not found in PATH")
        return False

def test_file_system():
    """Test file system permissions"""
    try:
        test_dir = Path.home() / "Desktop" / "GitDiffReports" / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        test_dir.rmdir()
        
        print("   File system access OK")
        return True
    except Exception as e:
        print(f"   File system error: {e}")
        return False

if __name__ == "__main__":
    run_tests()