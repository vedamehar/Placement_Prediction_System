"""
Feature Engineering Module
Handles feature extraction and engineering for ML models
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler


class FeatureEngineering:
    """Class for feature engineering and preprocessing"""
    
    BASE_FEATURES = [
        "cgpa", "project_score", "dsa_score", "hackathon_wins",
        "aptitude_score", "hr_score", "resume_ats_score", "cs_fundamentals_score"
    ]
    
    DERIVED_FEATURES = ["technical_score", "soft_skill_score"]
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.features = self.BASE_FEATURES + self.DERIVED_FEATURES
        self.fitted = False
    
    def create_derived_features(self, df):
        """Create derived features from base features"""
        df = df.copy()
        
        df["technical_score"] = (
            df["dsa_score"] + df["project_score"] + df["cs_fundamentals_score"]
        ) / 3
        
        df["soft_skill_score"] = (
            df["aptitude_score"] + df["hr_score"]
        ) / 2
        
        return df
    
    def prepare_features(self, df, fit=False):
        """Prepare and scale features"""
        df = self.create_derived_features(df)
        
        X = df[self.features].copy()
        
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            self.fitted = True
        else:
            if not self.fitted:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            X_scaled = self.scaler.transform(X)
        
        return X_scaled, self.features
    
    def prepare_student_input(self, student_dict):
        """Prepare single student input"""
        df = pd.DataFrame([student_dict])
        X_scaled, _ = self.prepare_features(df, fit=False)
        return X_scaled[0]
    
    def get_feature_names(self):
        """Get feature names"""
        return self.features
