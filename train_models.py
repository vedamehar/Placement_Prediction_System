"""
Train Models Script
Trains machine learning models on placement dataset
"""

import pandas as pd
import os
from modules.ml_models import MLModels
from modules.feature_engineering import FeatureEngineering


def create_sample_training_data():
    """Create sample training data if not exists"""
    training_file = "data/placement_dataset_training.csv"
    
    if os.path.exists(training_file):
        return training_file
    
    print("Creating sample training data...")
    
    # Sample training data
    # data = {
    #     'cgpa': [3.5, 3.8, 2.9, 3.6, 3.2, 3.9, 3.1, 3.7, 3.3, 3.4],
    #     'dsa_score': [70, 85, 45, 80, 65, 90, 50, 82, 68, 75],
    #     'project_score': [60, 75, 40, 70, 55, 80, 45, 72, 60, 65],
    #     'hackathon_wins': [1, 3, 0, 2, 1, 3, 0, 2, 1, 1],
    #     'aptitude_score': [65, 70, 55, 75, 60, 72, 58, 68, 62, 67],
    #     'hr_score': [70, 75, 60, 80, 65, 78, 62, 76, 68, 72],
    #     'resume_ats_score': [60, 75, 45, 70, 55, 78, 50, 72, 58, 65],
    #     'cs_fundamentals_score': [65, 80, 50, 75, 60, 82, 55, 78, 62, 70],
    #     'placement_status': ['Placed', 'Placed', 'Not Placed', 'Placed', 'Placed', 
    #                         'Placed', 'Not Placed', 'Placed', 'Placed', 'Placed'],
    #     'salary_lpa': [50, 62, 0, 58, 52, 70, 0, 65, 55, 60],
    #     'job_role': ['SE', 'SDE', 'NA', 'SE', 'SE', 'SDE', 'NA', 'SDE', 'SE', 'SE'],
    #     'company_name': ['TCS', 'Amazon', 'NA', 'Infosys', 'TCS', 'Microsoft', 'NA', 'Amazon', 'Wipro', 'Infosys']
    # }
    
    df = pd.DataFrame(data)
    df.to_csv(training_file, index=False)
    print(f"✅ Sample training data created at {training_file}")
    
    return training_file


def load_training_data():
    """Load training data"""
    # First try large dataset
    large_dataset = "data/campus_placement_dataset_final_academic_4000.csv"
    if os.path.exists(large_dataset):
        print(f"\n📥 Loading training data from {large_dataset}...")
        df = pd.read_csv(large_dataset)
        print(f"📊 Training data loaded: {df.shape}")
        return df
    
    # Fallback to creating sample data
    training_file = create_sample_training_data()
    df = pd.read_csv(training_file)
    print(f"📊 Training data loaded: {df.shape}")
    return df


def train_all_models():
    """Train all ML models"""
    print("\n" + "="*50)
    print("🚀 PLACEMENT AI SYSTEM - MODEL TRAINING")
    print("="*50)
    
    # Load data
    print("\n📥 Loading training data...")
    df = load_training_data()
    
    # Initialize feature engineering
    print("\n⚙️  Initializing feature engineering...")
    fe = FeatureEngineering()
    feature_names = fe.BASE_FEATURES + fe.DERIVED_FEATURES
    
    # Initialize and train models
    print("\n🤖 Initializing ML models...")
    models = MLModels()
    
    print("\n🔧 Training models...")
    models.train_models(df, feature_names)
    
    # Save models
    print("\n💾 Saving trained models...")
    models.save_models()
    
    print("\n" + "="*50)
    print("✅ TRAINING COMPLETED!")
    print("="*50)
    print("\nModels saved to: models/")
    print("\nYou can now run: python main.py")
    print("="*50)


if __name__ == "__main__":
    train_all_models()

