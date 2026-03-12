"""
ML Models Module
Contains machine learning models for predictions
"""

import pickle
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.neighbors import NearestNeighbors
from xgboost import XGBClassifier, XGBRegressor


class MLModels:
    """Class for managing ML models"""
    
    MODELS_DIR = "models"
    
    def __init__(self):
        self.placement_model = None
        self.salary_model = None
        self.jobrole_model = None
        self.role_encoder = None
        self.scaler = StandardScaler()
        self.knn_companies = None
        self.knn_X = None
        self.companies_list = None
        self.feature_names = None
    
    def train_models(self, df, feature_names):
        """Train all models"""
        self.feature_names = feature_names
        
        print("\n" + "="*50)
        print("🤖 TRAINING ML MODELS")
        print("="*50)
        
        # Prepare features
        df = df.copy()
        df["technical_score"] = (
            df["dsa_score"] + df["project_score"] + df["cs_fundamentals_score"]
        ) / 3
        df["soft_skill_score"] = (
            df["aptitude_score"] + df["hr_score"]
        ) / 2
        
        X = df[feature_names]
        X_scaled = self.scaler.fit_transform(X)
        
        # Create target variable
        df["placed"] = (df.get("placement_status", "Not Placed") == "Placed").astype(int)
        y = df["placed"]
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train Placement Model
        print("\n📍 Training Placement Model...")
        base_model = XGBClassifier(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.7,
            colsample_bytree=0.7,
            reg_lambda=1.5,
            reg_alpha=0.5,
            random_state=42
        )
        base_model.fit(X_train, y_train)
        
        self.placement_model = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
        self.placement_model.fit(X_train, y_train)
        
        y_pred = self.placement_model.predict(X_test)
        y_prob = self.placement_model.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        print(f"✅ Placement Model - Accuracy: {acc:.4f}, ROC-AUC: {auc:.4f}")
        
        # Train Salary Model
        print("\n💰 Training Salary Model...")
        placed_df = df[df["placed"] == 1].copy()
        
        if len(placed_df) > 10:
            Xp = placed_df[feature_names]
            Xp_scaled = self.scaler.transform(Xp)
            yp = placed_df.get("salary_lpa", placed_df.get("expected_salary", [50] * len(Xp)))
            
            if isinstance(yp, pd.Series):
                yp = yp.values
            
            self.salary_model = XGBRegressor(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.05,
                random_state=42
            )
            self.salary_model.fit(Xp_scaled, yp)
            print("✅ Salary Model trained")
        else:
            print("⚠️  Insufficient placed students for salary model")
            self.salary_model = XGBRegressor(n_estimators=10)
        
        # Train Job Role Model
        print("\n🎯 Training Job Role Model...")
        if len(placed_df) > 10 and "job_role" in placed_df.columns:
            self.role_encoder = LabelEncoder()
            placed_df["job_role_encoded"] = self.role_encoder.fit_transform(placed_df["job_role"])
            
            X_role = self.scaler.transform(placed_df[feature_names])
            y_role = placed_df["job_role_encoded"]
            
            self.jobrole_model = XGBClassifier(n_estimators=120, max_depth=4, random_state=42)
            self.jobrole_model.fit(X_role, y_role)
            print("✅ Job Role Model trained")
        else:
            print("⚠️  Insufficient data for job role model")
            self.jobrole_model = XGBClassifier(n_estimators=10)
        
        # Train KNN for Companies
        print("\n🏢 Training Company Recommendation Model...")
        if len(placed_df) > 10 and "company_name" in placed_df.columns:
            self.companies_list = placed_df["company_name"].values
            X_role = self.scaler.transform(placed_df[feature_names])
            
            self.knn_companies = NearestNeighbors(n_neighbors=min(40, len(placed_df)))
            self.knn_companies.fit(X_role)
            self.knn_X = X_role
            print("✅ Company Recommendation Model trained")
        else:
            print("⚠️  Insufficient data for company recommendation model")
        
        print("\n✅ All models trained successfully!")
    
    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.MODELS_DIR, exist_ok=True)
        
        try:
            with open(f"{self.MODELS_DIR}/placement_model.pkl", "wb") as f:
                pickle.dump(self.placement_model, f)
            
            with open(f"{self.MODELS_DIR}/salary_model.pkl", "wb") as f:
                pickle.dump(self.salary_model, f)
            
            with open(f"{self.MODELS_DIR}/jobrole_model.pkl", "wb") as f:
                pickle.dump(self.jobrole_model, f)
            
            with open(f"{self.MODELS_DIR}/scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
            
            if self.role_encoder:
                with open(f"{self.MODELS_DIR}/role_encoder.pkl", "wb") as f:
                    pickle.dump(self.role_encoder, f)
            
            if self.knn_companies:
                with open(f"{self.MODELS_DIR}/knn_companies.pkl", "wb") as f:
                    pickle.dump(self.knn_companies, f)
                with open(f"{self.MODELS_DIR}/companies_list.pkl", "wb") as f:
                    pickle.dump(self.companies_list, f)
            
            print(f"✅ Models saved to {self.MODELS_DIR}/")
        except Exception as e:
            print(f"❌ Error saving models: {e}")
    
    def load_models(self):
        """Load pre-trained models from disk"""
        try:
            with open(f"{self.MODELS_DIR}/placement_model.pkl", "rb") as f:
                self.placement_model = pickle.load(f)
            
            with open(f"{self.MODELS_DIR}/salary_model.pkl", "rb") as f:
                self.salary_model = pickle.load(f)
            
            with open(f"{self.MODELS_DIR}/jobrole_model.pkl", "rb") as f:
                self.jobrole_model = pickle.load(f)
            
            with open(f"{self.MODELS_DIR}/scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            
            try:
                with open(f"{self.MODELS_DIR}/role_encoder.pkl", "rb") as f:
                    self.role_encoder = pickle.load(f)
            except:
                pass
            
            try:
                with open(f"{self.MODELS_DIR}/knn_companies.pkl", "rb") as f:
                    self.knn_companies = pickle.load(f)
                with open(f"{self.MODELS_DIR}/companies_list.pkl", "rb") as f:
                    self.companies_list = pickle.load(f)
            except:
                pass

            print("[OK] Models loaded successfully!")
            return True
        except Exception as e:
            print(f"[!] Could not load models: {e}")
            return False
