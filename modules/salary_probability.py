"""
Salary Tier Probability Predictor Module
Predicts salary tier distribution for placed students
New independent module - does not modify existing placement prediction system
"""

import pandas as pd
import numpy as np
import pickle
import os
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler


class SalaryTierPredictor:
    """
    Predicts salary tier probabilities for students.
    Multi-class XGBoost classifier with 7 salary tiers.
    """
    
    # Salary tier definitions
    SALARY_TIERS = {
        0: "0-5 LPA",
        1: "5-10 LPA",
        2: "10-15 LPA",
        3: "15-20 LPA",
        4: "20-30 LPA",
        5: "30-40 LPA",
        6: ">40 LPA"
    }
    
    TIER_BOUNDARIES = [0, 5, 10, 15, 20, 30, 40, float('inf')]
    
    MODEL_PATH = "models/salary_tier_model.pkl"
    SCALER_PATH = "models/salary_tier_scaler.pkl"
    FEATURES_PATH = "models/salary_tier_features.pkl"
    
    def __init__(self):
        """Initialize the salary tier predictor"""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.is_trained = False
    
    @staticmethod
    def salary_to_tier(salary):
        """
        Convert salary (LPA) to tier (0-6)
        
        Args:
            salary (float): Salary in LPA
            
        Returns:
            int: Tier 0-6
        """
        if pd.isna(salary) or salary is None:
            return None
        
        salary = float(salary)
        
        if salary < 5:
            return 0
        elif salary < 10:
            return 1
        elif salary < 15:
            return 2
        elif salary < 20:
            return 3
        elif salary < 30:
            return 4
        elif salary < 40:
            return 5
        else:
            return 6
    
    @staticmethod
    def tier_to_salary_range(tier):
        """
        Convert tier to salary range description
        
        Args:
            tier (int): Tier 0-6
            
        Returns:
            str: Salary range description
        """
        tier_map = {
            0: "0-5 LPA",
            1: "5-10 LPA",
            2: "10-15 LPA",
            3: "15-20 LPA",
            4: "20-30 LPA",
            5: "30-40 LPA",
            6: ">40 LPA"
        }
        return tier_map.get(tier, "Unknown")
    
    def train_salary_model(self, df, feature_names, scaler=None):
        """
        Train XGBoost multi-class salary tier predictor
        
        Args:
            df (DataFrame): Dataset with salary_lpa column
            feature_names (list): List of feature column names
            scaler (StandardScaler): Pre-fitted scaler from placement model
        """
        print("\n" + "="*60)
        print("🎓 TRAINING SALARY TIER PREDICTION MODEL")
        print("="*60)
        
        try:
            # Filter placed students only
            df = df.copy()
            placed_mask = (df.get("placement_status", "Not Placed") == "Placed") | \
                         (df.get("salary_lpa", df.get("expected_salary", pd.NA)).notna())
            df_placed = df[placed_mask].copy()
            
            if len(df_placed) < 10:
                print("⚠️  Insufficient placed students for training")
                print("   (Need at least 10 placed students)")
                self.is_trained = False
                return False
            
            print(f"📊 Using {len(df_placed)} placed students for training")
            
            # Get salary column (try multiple names)
            salary_col = None
            if "salary_lpa" in df_placed.columns:
                salary_col = "salary_lpa"
            elif "expected_salary" in df_placed.columns:
                salary_col = "expected_salary"
            else:
                print("❌ No salary column found in dataset")
                self.is_trained = False
                return False
            
            # Convert salary to tier labels
            df_placed["salary_tier"] = df_placed[salary_col].apply(self.salary_to_tier)
            
            # Remove rows with None tier
            df_placed = df_placed[df_placed["salary_tier"].notna()].copy()
            
            print(f"📈 Salary tier distribution:")
            for tier, label in self.SALARY_TIERS.items():
                count = (df_placed["salary_tier"] == tier).sum()
                pct = (count / len(df_placed)) * 100
                print(f"   {label:12} → {count:3} students ({pct:5.1f}%)")
            
            # Prepare features - include derived features
            # Create derived features if they don't exist
            if "technical_score" not in df_placed.columns:
                df_placed["technical_score"] = (
                    df_placed["dsa_score"] + df_placed["project_score"] + 
                    df_placed["cs_fundamentals_score"]
                ) / 3
            
            if "soft_skill_score" not in df_placed.columns:
                df_placed["soft_skill_score"] = (
                    df_placed["aptitude_score"] + df_placed["hr_score"]
                ) / 2
            
            # Now prepare features with base + derived
            all_features = [
                "cgpa", "project_score", "dsa_score", "hackathon_wins",
                "aptitude_score", "hr_score", "resume_ats_score", "cs_fundamentals_score",
                "technical_score", "soft_skill_score"
            ]
            
            X = df_placed[all_features].copy()
            y = df_placed["salary_tier"].astype(int)
            
            # Scale features (reuse existing scaler or create new one)
            if scaler is None:
                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)
                print("\n✅ Created new StandardScaler")
            else:
                self.scaler = scaler
                X_scaled = self.scaler.transform(X)
                print("\n✅ Using existing StandardScaler from placement model")
            
            self.feature_names = all_features
            
            # Train XGBoost multi-class classifier
            print("\n🚀 Training XGBoost Multi-Class Classifier...")
            self.model = XGBClassifier(
                objective="multi:softprob",
                num_class=7,
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.7,
                colsample_bytree=0.7,
                random_state=42,
                eval_metric='mlogloss'
            )
            
            self.model.fit(X_scaled, y, verbose=False)
            
            print("✅ Salary tier model trained successfully!")
            self.is_trained = True
            return True
            
        except Exception as e:
            print(f"❌ Error training salary model: {e}")
            self.is_trained = False
            return False
    
    def predict_salary_distribution(self, student_scores):
        """
        Predict salary tier probabilities for a student
        
        Args:
            student_scores (dict): Student features dictionary
                                  Must contain: dsa_score, project_score, 
                                             cs_fundamentals_score, aptitude_score, etc.
        
        Returns:
            dict: Formatted salary distribution with probabilities
        """
        if not self.is_trained or self.model is None:
            print("❌ Model not trained. Cannot make predictions.")
            return None
        
        try:
            # Create DataFrame from student scores
            student_df = pd.DataFrame([student_scores])
            
            # Create derived features if they don't exist
            if "technical_score" not in student_df.columns:
                student_df["technical_score"] = (
                    student_df["dsa_score"] + student_df["project_score"] + 
                    student_df["cs_fundamentals_score"]
                ) / 3
            
            if "soft_skill_score" not in student_df.columns:
                student_df["soft_skill_score"] = (
                    student_df["aptitude_score"] + student_df["hr_score"]
                ) / 2
            
            # Extract features in correct order
            X = student_df[self.feature_names].copy()
            
            # Scale using the same scaler
            X_scaled = self.scaler.transform(X)
            
            # Get probability predictions
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            # Format output
            result = self.format_salary_output(probabilities)
            return result
            
        except KeyError as e:
            print(f"❌ Missing required feature: {e}")
            print(f"   Required features: {self.feature_names}")
            return None
        except Exception as e:
            print(f"❌ Error predicting salary: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def format_salary_output(self, probabilities):
        """
        Format salary tier probabilities for display
        
        Args:
            probabilities (array): Raw probability array from model
        
        Returns:
            dict: Formatted salary distribution
        """
        result = {}
        
        # Convert to percentages
        for tier, label in self.SALARY_TIERS.items():
            prob_pct = probabilities[tier] * 100
            result[label] = round(prob_pct, 1)
        
        return result
    
    def calculate_derived_probabilities(self, salary_distribution):
        """
        Calculate cumulative probabilities for multiple salary thresholds
        using the tier distribution.
        
        Uses cumulative logic:
        - For boundary thresholds (5, 10, 15, 20, 30, 40): sum relevant tiers
        - For internal thresholds (2, 25, 35): use linear interpolation
        
        Args:
            salary_distribution (dict): Tier-based probability distribution
                                       e.g., {"0-5 LPA": 5.0, "5-10 LPA": 14.2, ...}
        
        Returns:
            dict: Derived probabilities for thresholds
                  {">2 LPA": value, ">5 LPA": value, ..., ">40 LPA": value}
        """
        if not salary_distribution:
            return None
        
        try:
            derived = {}
            
            # Extract individual tier probabilities
            p_0_5 = salary_distribution.get("0-5 LPA", 0)
            p_5_10 = salary_distribution.get("5-10 LPA", 0)
            p_10_15 = salary_distribution.get("10-15 LPA", 0)
            p_15_20 = salary_distribution.get("15-20 LPA", 0)
            p_20_30 = salary_distribution.get("20-30 LPA", 0)
            p_30_40 = salary_distribution.get("30-40 LPA", 0)
            p_above_40 = salary_distribution.get(">40 LPA", 0)
            
            # Threshold 1: >2 LPA
            # Includes: portion of 0-5 that's >2 + all above 5
            # Linear interpolation: (5-2)/(5-0) = 3/5 of the 0-5 tier
            p_above_2 = (3/5 * p_0_5) + p_5_10 + p_10_15 + p_15_20 + p_20_30 + p_30_40 + p_above_40
            derived[">2 LPA"] = round(p_above_2, 1)
            
            # Threshold 2: >5 LPA
            # Includes: all tiers from 5 onwards
            p_above_5 = p_5_10 + p_10_15 + p_15_20 + p_20_30 + p_30_40 + p_above_40
            derived[">5 LPA"] = round(p_above_5, 1)
            
            # Threshold 3: >10 LPA
            # Includes: all tiers from 10 onwards
            p_above_10 = p_10_15 + p_15_20 + p_20_30 + p_30_40 + p_above_40
            derived[">10 LPA"] = round(p_above_10, 1)
            
            # Threshold 4: >15 LPA
            # Includes: all tiers from 15 onwards
            p_above_15 = p_15_20 + p_20_30 + p_30_40 + p_above_40
            derived[">15 LPA"] = round(p_above_15, 1)
            
            # Threshold 5: >20 LPA
            # Includes: all tiers from 20 onwards
            p_above_20 = p_20_30 + p_30_40 + p_above_40
            derived[">20 LPA"] = round(p_above_20, 1)
            
            # Threshold 6: >25 LPA
            # Includes: portion of 20-30 that's >25 + tiers above 30
            # Linear interpolation: (30-25)/(30-20) = 5/10 = 0.5 of the 20-30 tier
            p_above_25 = (5/10 * p_20_30) + p_30_40 + p_above_40
            derived[">25 LPA"] = round(p_above_25, 1)
            
            # Threshold 7: >30 LPA
            # Includes: all tiers from 30 onwards
            p_above_30 = p_30_40 + p_above_40
            derived[">30 LPA"] = round(p_above_30, 1)
            
            # Threshold 8: >35 LPA
            # Includes: portion of 30-40 that's >35 + tiers above 40
            # Linear interpolation: (40-35)/(40-30) = 5/10 = 0.5 of the 30-40 tier
            p_above_35 = (5/10 * p_30_40) + p_above_40
            derived[">35 LPA"] = round(p_above_35, 1)
            
            # Threshold 9: >40 LPA
            # Includes: only the >40 tier
            p_above_40_final = p_above_40
            derived[">40 LPA"] = round(p_above_40_final, 1)
            
            return derived
            
        except Exception as e:
            print(f"❌ Error calculating derived probabilities: {e}")
            return None
    
    def save_model(self):
        """Save trained model and scaler to disk"""
        os.makedirs("models", exist_ok=True)
        
        try:
            if self.model is not None:
                with open(self.MODEL_PATH, "wb") as f:
                    pickle.dump(self.model, f)
                print(f"✅ Salary tier model saved: {self.MODEL_PATH}")
            
            if self.scaler is not None:
                with open(self.SCALER_PATH, "wb") as f:
                    pickle.dump(self.scaler, f)
                print(f"✅ Scaler saved: {self.SCALER_PATH}")
            
            if self.feature_names is not None:
                with open(self.FEATURES_PATH, "wb") as f:
                    pickle.dump(self.feature_names, f)
                print(f"✅ Feature names saved: {self.FEATURES_PATH}")
        except Exception as e:
            print(f"❌ Error saving models: {e}")
    
    def load_model(self):
        """Load pre-trained model and scaler from disk"""
        try:
            if os.path.exists(self.MODEL_PATH) and os.path.exists(self.SCALER_PATH) and os.path.exists(self.FEATURES_PATH):
                with open(self.MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                
                with open(self.SCALER_PATH, "rb") as f:
                    self.scaler = pickle.load(f)
                
                with open(self.FEATURES_PATH, "rb") as f:
                    self.feature_names = pickle.load(f)
                
                self.is_trained = True
                print("✅ Salary tier model loaded successfully!")
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def print_salary_distribution(self, probabilities):
        """
        Pretty print salary distribution with comprehensive derived probabilities
        
        Args:
            probabilities (dict): Formatted probability dictionary
        """
        if probabilities is None:
            print("No salary prediction available")
            return
        
        print("\n" + "="*60)
        print("💰 SALARY TIER PROBABILITY DISTRIBUTION")
        print("="*60)
        
        for tier_label, prob in probabilities.items():
            # Create a simple bar chart
            bar_length = int(prob / 5)
            bar = "█" * bar_length
            print(f"{tier_label:12} → {prob:6.1f}% {bar}")
        
        # Calculate comprehensive derived probabilities
        print("\n" + "="*60)
        print("📊 CUMULATIVE SALARY THRESHOLDS:")
        print("="*60)
        
        derived_probs = self.calculate_derived_probabilities(probabilities)
        
        if derived_probs:
            for threshold in [">2 LPA", ">5 LPA", ">10 LPA", ">15 LPA", ">20 LPA", 
                            ">25 LPA", ">30 LPA", ">35 LPA", ">40 LPA"]:
                prob = derived_probs.get(threshold, 0)
                bar_length = int(prob / 5)
                bar = "█" * bar_length
                print(f"   {threshold:8} → {prob:6.1f}% {bar}")
        
        # Find most likely salary tier
        most_likely_tier = max(probabilities, key=probabilities.get)
        most_likely_prob = probabilities[most_likely_tier]
        
        print("\n" + "="*60)
        print(f"🎯 MOST LIKELY SALARY RANGE:")
        print(f"   {most_likely_tier} with {most_likely_prob:.1f}% probability")
        print("="*60)

