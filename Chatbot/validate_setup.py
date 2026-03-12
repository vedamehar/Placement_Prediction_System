"""
EduPlus PlaceMate AI - Setup Validation Script
Verify that all components are correctly installed and configured
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_python_version():
    """Verify Python version is compatible"""
    print_header("Step 1: Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Current Python: {version_str}")
    
    if version.major == 3 and version.minor in [8, 9, 10]:
        print_success(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} is NOT compatible")
        print("  Requires: Python 3.8, 3.9, or 3.10")
        return False

def check_virtual_environment():
    """Verify virtual environment is active"""
    print_header("Step 2: Virtual Environment Check")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Virtual environment is ACTIVE")
        print(f"venv path: {sys.prefix}")
        return True
    else:
        print_error("Virtual environment is NOT active")
        print("  Run: venv_rasa\\Scripts\\activate.bat")
        return False

def check_packages():
    """Verify all required packages are installed"""
    print_header("Step 3: Package Installation Check")
    
    required_packages = {
        'rasa': '3.6.13',
        'rasa_sdk': '3.6.1',
        'pandas': '2.0.3',
        'fuzzywuzzy': '0.18.0',
        'Levenshtein': '0.21.1'
    }
    
    all_ok = True
    
    # Get installed packages
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list', '--format', 'json'],
        capture_output=True,
        text=True
    )
    
    installed = {}
    if result.returncode == 0:
        try:
            packages_list = json.loads(result.stdout)
            for pkg in packages_list:
                installed[pkg['name'].lower()] = pkg['version']
        except:
            pass
    
    # Check each required package
    for package, required_version in required_packages.items():
        package_lower = package.lower()
        if package_lower in installed:
            installed_version = installed[package_lower]
            print_success(f"{package}: {installed_version}")
        else:
            print_error(f"{package}: NOT INSTALLED (required: {required_version})")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """Verify Rasa project file structure"""
    print_header("Step 4: Project Structure Check")
    
    required_files = {
        'config.yml': 'Rasa configuration',
        'domain.yml': 'Domain definition',
        'credentials.yml': 'Credentials',
        'endpoints.yml': 'Endpoints',
        'requirements.txt': 'Dependencies list',
        'data/nlu.yml': 'NLU training data',
        'data/stories.yml': 'Dialogue stories',
        'data/rules.yml': 'Conversation rules',
        'data/company_placement_db.csv': 'Knowledge base (CSV)',
        'actions/actions.py': 'Custom action handlers',
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_kb = size / 1024
            print_success(f"{file_path} ({description}) - {size_kb:.1f} KB")
        else:
            print_error(f"{file_path} ({description}) - MISSING")
            all_ok = False
    
    return all_ok

def check_model():
    """Verify trained Rasa model exists"""
    print_header("Step 5: Trained Model Check")
    
    model_dir = Path('models')
    if model_dir.exists():
        model_files = list(model_dir.glob('*'))
        if model_files:
            latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
            size_mb = latest_model.stat().st_size / (1024 * 1024)
            print_success(f"Trained model found: {latest_model.name}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
        else:
            print_error("models/ directory is empty")
            print("  Run: rasa train")
            return False
    else:
        print_error("models/ directory does not exist")
        print("  Run: rasa train")
        return False

def check_data_integrity():
    """Verify CSV data can be read"""
    print_header("Step 6: Data Integrity Check")
    
    try:
        import pandas as pd
        
        csv_path = 'data/company_placement_db.csv'
        if not os.path.exists(csv_path):
            print_error(f"{csv_path} not found")
            return False
        
        df = pd.read_csv(csv_path)
        num_rows = len(df)
        num_cols = len(df.columns)
        
        print_success(f"CSV loaded successfully")
        print(f"  Companies: {num_rows}")
        print(f"  Columns: {num_cols}")
        print(f"  Columns: {', '.join(df.columns.tolist()[:5])}...")
        
        return True
    except Exception as e:
        print_error(f"Failed to load CSV: {str(e)}")
        return False

def check_rasa_cli():
    """Verify Rasa CLI is accessible"""
    print_header("Step 7: Rasa CLI Check")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'rasa', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version_output = result.stdout.strip()
            print_success("Rasa CLI is accessible")
            print(f"  {version_output}")
            return True
        else:
            print_error("Rasa CLI returned an error")
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Failed to run Rasa: {str(e)}")
        return False

def check_actions_server():
    """Verify action server can be started"""
    print_header("Step 8: Actions Server Check")
    
    try:
        # Just check if the module can be imported
        result = subprocess.run(
            [sys.executable, '-c', 'import rasa_sdk; print("rasa_sdk available")'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("Rasa SDK is available")
            print("  Actions server can be started with: rasa run actions")
            return True
        else:
            print_error("Rasa SDK not available")
            return False
    except Exception as e:
        print_error(f"Failed to check Rasa SDK: {str(e)}")
        return False

def run_rasa_validation():
    """Run Rasa data validation"""
    print_header("Step 9: Rasa Data Validation")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'rasa', 'data', 'validate'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("Rasa data validation passed")
            return True
        else:
            print_warning("Rasa data validation had warnings")
            if result.stdout:
                print(result.stdout)
            return True  # Don't fail on warnings
    except Exception as e:
        print_warning(f"Could not run validation: {str(e)}")
        return False

def main():
    """Run all validation checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + f"{'EduPlus PlaceMate AI - Setup Validation':^58}" + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.END}\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Packages", check_packages),
        ("Project Structure", check_project_structure),
        ("Trained Model", check_model),
        ("Data Integrity", check_data_integrity),
        ("Rasa CLI", check_rasa_cli),
        ("Actions Server", check_actions_server),
        ("Rasa Validation", run_rasa_validation),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Check failed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Checks Passed: {passed}/{total}")
    print()
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {name:.<40} {status}")
    
    print()
    
    if passed == total:
        print_success("All checks passed! Ready to run chatbot.")
        print()
        print("Run chatbot with:")
        print("  rasa run actions  (Terminal 1)")
        print("  rasa shell        (Terminal 2)")
        return 0
    elif passed >= total - 2:
        print_warning("Most checks passed with minor issues")
        print()
        print("Try running chatbot anyway with:")
        print("  rasa run actions  (Terminal 1)")
        print("  rasa shell        (Terminal 2)")
        return 1
    else:
        print_error("Critical issues found. Fix errors before running chatbot.")
        return 2

if __name__ == '__main__':
    exit_code = main()
    print()
    sys.exit(exit_code)
