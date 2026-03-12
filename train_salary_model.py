"""
Train and Save Salary Tier Model
This script trains the salary tier prediction model on the dataset
Run this once to create the pre-trained model
"""

import pandas as pd
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.salary_probability import SalaryTierPredictor
from modules.ml_models import MLModels

def train_salary_tier_model():
    """Train and save the salary tier model"""
    
    print("\n" + "="*70)
    print("TRAINING SALARY TIER PREDICTION MODEL".center(70))
    print("="*70)
    
    # Load dataset
    print("\n[STEP 1] Loading dataset...")
    try:
        # Use the 4000-student dataset which has actual salary data
        df = pd.read_csv('data/campus_placement_dataset_final_academic_4000.csv')
        print(f"[OK] Dataset loaded: {len(df)} students with salary data")
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        return False
    
    # Define features (MUST match placement model)
    feature_names = [
        "cgpa", "project_score", "dsa_score", "hackathon_wins",
        "aptitude_score", "hr_score", "resume_ats_score", "cs_fundamentals_score"
    ]
    
    print(f"[OK] Using {len(feature_names)} features for training")
    
    # Load placement models to get the scaler
    print("\n[STEP 2] Loading placement model scaler...")
    try:
        ml_models = MLModels()
        if ml_models.load_models():
            print("[OK] Placement models loaded successfully!")
            scaler = ml_models.scaler
        else:
            print("[!] Placement models not found. Training placement models first...")
            from train_models import train_all_models
            train_all_models()
            ml_models.load_models()
            scaler = ml_models.scaler
            print("[OK] Placement models trained and loaded!")
    except Exception as e:
        print(f"[ERROR] Failed to load placement models: {e}")
        return False
    
    # Train salary tier model
    print("\n[STEP 3] Training salary tier prediction model...")
    try:
        salary_predictor = SalaryTierPredictor()
        success = salary_predictor.train_salary_model(df, feature_names, scaler=scaler)
        
        if not success:
            print("[ERROR] Failed to train salary tier model")
            return False
        
        print("[OK] Salary tier model trained successfully!")
    except Exception as e:
        print(f"[ERROR] Error training salary model: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save the model
    print("\n[STEP 4] Saving salary tier model...")
    try:
        salary_predictor.save_model()
        print("[OK] Salary tier model saved successfully!")
        print(f"     Model: models/salary_tier_model.pkl")
        print(f"     Scaler: models/salary_tier_scaler.pkl")
    except Exception as e:
        print(f"[ERROR] Failed to save model: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ SALARY TIER MODEL TRAINING COMPLETE".center(70))
    print("="*70)
    print("\nThe salary tier model is now ready to use!")
    print("It will be automatically loaded when you run predictions.")
    print("\n" + "="*70)
    
    return True

if __name__ == "__main__":
    success = train_salary_tier_model()
    sys.exit(0 if success else 1)
