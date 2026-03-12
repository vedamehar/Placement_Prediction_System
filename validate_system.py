#!/usr/bin/env python3
"""
System Validation Script
Checks if all components are properly configured and ready to run
"""

import os
import sys
import pandas as pd
from pathlib import Path


def check_file_exists(filepath):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists


def check_directory_exists(dirpath):
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    status = "✅" if exists else "❌"
    print(f"{status} {dirpath}/")
    return exists


def check_csv_schema(filepath, expected_columns):
    """Check if CSV has correct schema"""
    try:
        df = pd.read_csv(filepath)
        actual_columns = set(df.columns)
        expected_set = set(expected_columns)
        
        if actual_columns == expected_set:
            print(f"✅ CSV schema correct: {len(expected_columns)} columns")
            return True
        else:
            missing = expected_set - actual_columns
            extra = actual_columns - expected_set
            
            if missing:
                print(f"❌ Missing columns: {missing}")
            if extra:
                print(f"⚠️  Extra columns: {extra}")
            return False
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False


def check_python_packages():
    """Check if required packages are installed"""
    packages = [
        'pandas',
        'xgboost',
        'scikit-learn',
        'requests',
        'language_tool_python',
        'textstat'
    ]
    
    print("\n📦 CHECKING PACKAGES:")
    all_installed = True
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def validate_system():
    """Main validation function"""
    print("\n" + "="*60)
    print("🔍 PLACEMENT AI SYSTEM VALIDATION")
    print("="*60)
    
    # Get root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    
    # Track validation status
    all_valid = True
    
    # 1. Check main file
    print("\n📄 MAIN APPLICATION FILE:")
    all_valid &= check_file_exists("main.py")
    
    # 2. Check modules
    print("\n📚 MODULE FILES:")
    modules = [
        "modules/student_profile.py",
        "modules/leetcode_dsa.py",
        "modules/github_project.py",
        "modules/aptitude_ats.py",
        "modules/hr_round.py",
        "modules/feature_engineering.py",
        "modules/ml_models.py",
        "modules/company_logic.py",
        "modules/prediction.py"
    ]
    
    for module in modules:
        all_valid &= check_file_exists(module)
    
    # 3. Check directories
    print("\n📁 DIRECTORIES:")
    all_valid &= check_directory_exists("data")
    all_valid &= check_directory_exists("models")
    all_valid &= check_directory_exists("modules")
    
    # 4. Check CSV schema
    print("\n📊 CSV DATABASE:")
    expected_columns = [
        'student_id', 'cgpa', 'os_score', 'dbms_score', 'cn_score', 
        'oop_score', 'system_design_score', 'cs_fundamentals_score',
        'dsa_score', 'project_score', 'aptitude_score', 'hr_score', 
        'resume_ats_score', 'hackathon_wins', 'placement_probability', 
        'expected_salary', 'predicted_job_role', 'service_company_prob', 
        'product_company_prob'
    ]
    
    if os.path.exists("data/student_profiles.csv"):
        check_csv_schema("data/student_profiles.csv", expected_columns)
    else:
        print("⚠️  data/student_profiles.csv not found (will be created on first run)")
    
    # 5. Check other data files
    print("\n📋 TRAINING DATA:")
    all_valid &= check_file_exists("data/campus_placement_dataset_final_academic_4000.csv")
    all_valid &= check_file_exists("data/company_profiles_with_difficulty.csv")
    
    # 6. Check documentation
    print("\n📖 DOCUMENTATION:")
    docs = [
        "README.md",
        "WORKFLOW_UPDATED.md",
        "SYSTEM_FIXED_COMPLETE.md",
        "SETUP_GUIDE.md",
        "QUICKSTART.md"
    ]
    
    for doc in docs:
        all_valid &= check_file_exists(doc)
    
    # 7. Check configuration files
    print("\n⚙️  CONFIGURATION:")
    all_valid &= check_file_exists("requirements.txt")
    all_valid &= check_file_exists("setup.py")
    
    # 8. Check packages
    packages_ok = check_python_packages()
    
    # 9. Check models (if they exist)
    print("\n🤖 ML MODELS:")
    models_exist = os.path.exists("models/placement_model.pkl")
    if models_exist:
        print("✅ Models directory contains trained models")
    else:
        print("⚠️  Models not trained yet (run train_models.py after first installation)")
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    if all_valid and packages_ok:
        print("✅ SYSTEM READY!")
        print("\n🚀 Next Steps:")
        print("1. Run: python train_models.py  (if models not yet trained)")
        print("2. Run: python main.py  (to start the application)")
        return 0
    else:
        print("⚠️  SOME ISSUES FOUND")
        print("\n🔧 Fix Issues:")
        if not packages_ok:
            print("• Install missing packages: pip install -r requirements.txt")
        print("• Check file paths and ensure all files are in place")
        return 1


if __name__ == "__main__":
    sys.exit(validate_system())
