"""
Setup Script for Placement AI System
Run this script to initialize the system
"""

import os
import sys

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required!")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "models",
        "modules",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory '{directory}' ready")

def check_requirements():
    """Check if requirements are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'pandas',
        'numpy',
        'sklearn',
        'xgboost',
        'requests'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        install = input("Install missing packages? (y/n): ").strip().lower()
        if install == 'y':
            os.system("pip install -r requirements.txt")
            print("✅ Installation complete!")
        else:
            print("⚠️  Please install manually: pip install -r requirements.txt")
    else:
        print("\n✅ All dependencies installed!")

def print_next_steps():
    """Print next steps"""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\n📖 Next Steps:")
    print("1. Train models (first time only):")
    print("   $ python train_models.py")
    print("\n2. Run the system:")
    print("   $ python main.py")
    print("\n📚 For more information, see README.md")
    print("="*60)

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🚀 PLACEMENT AI SYSTEM SETUP".center(60))
    print("="*60)
    
    check_python_version()
    create_directories()
    check_requirements()
    print_next_steps()

if __name__ == "__main__":
    main()
