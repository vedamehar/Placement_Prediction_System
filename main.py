"""
Main Placement AI System - Redesigned
Fetches data from student_profiles_100.csv and company_profiles_with_difficulty.csv only
Calculates service/product company probabilities with correct formulas
"""

import pandas as pd
import os
import sys
import io

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.leetcode_dsa import LeetCodeDSA
from modules.github_project import GitHubProject
from modules.aptitude_ats import AptitudeATS
from modules.hr_round import HRRound
from modules.ml_models import MLModels
from modules.feature_engineering import FeatureEngineering
from modules.service_product_probability import ServiceProductProbability
from modules.salary_probability import SalaryTierPredictor


# File paths - ONLY TWO DATA SOURCES
STUDENT_CSV = os.path.join(os.path.dirname(__file__), 'data/student_profiles_100.csv')
COMPANY_CSV = os.path.join(os.path.dirname(__file__), 'data/company_profiles_with_difficulty.csv')
PREDICTIONS_CSV = os.path.join(os.path.dirname(__file__), 'data/Predicted_Data.csv')

# Define columns for Predicted_Data.csv
PREDICTION_COLUMNS = [
    'student_id',
    'overall_placement_probability',
    'predicted_salary_lpa',
    'salary_range_min_lpa',
    'salary_range_mid_lpa',
    'salary_range_max_lpa',
    'prob_salary_gt_2_lpa',
    'prob_salary_gt_5_lpa',
    'prob_salary_gt_10_lpa',
    'prob_salary_gt_15_lpa',
    'prob_salary_gt_20_lpa',
    'prob_salary_gt_25_lpa',
    'prob_salary_gt_30_lpa',
    'prob_salary_gt_35_lpa',
    'prob_salary_gt_40_lpa',
    'predicted_job_role',
    'recommended_companies'
]


def print_header():
    """Print system header"""
    print("\n" + "="*60)
    print("PLACEMENT AI PREDICTION SYSTEM".center(60))
    print("="*60)


def get_student_id():
    """Get student ID from user"""
    while True:
        try:
            student_id = int(input("\nEnter Student ID: "))
            return student_id
        except ValueError:
            print("Invalid input! Please enter a valid Student ID (number)")


def load_student_from_csv(student_id):
    """Load student profile from student_profiles_100.csv"""
    try:
        df = pd.read_csv(STUDENT_CSV)
        student_row = df[df['student_id'] == student_id]

        if student_row.empty:
            return None

        student_data = student_row.iloc[0].to_dict()

        # Add hackathon_wins if missing (required by feature engineering)
        if 'hackathon_wins' not in student_data or pd.isna(student_data.get('hackathon_wins')):
            student_data['hackathon_wins'] = 0

        return student_data
    except Exception as e:
        print(f"Error loading student data: {e}")
        return None


def save_student_to_csv(student_id, student_data):
    """Save/Update student profile in student_profiles_100.csv"""
    try:
        df = pd.read_csv(STUDENT_CSV)

        # Find if student exists
        student_idx = df[df['student_id'] == student_id].index

        if len(student_idx) > 0:
            # Update existing student
            for key, value in student_data.items():
                if key in df.columns:
                    df.at[student_idx[0], key] = value
        else:
            # This shouldn't happen as student_profiles_100 has fixed students
            print("Student ID not found in database")
            return False

        # Save back to CSV
        df.to_csv(STUDENT_CSV, index=False)
        return True
    except Exception as e:
        print(f"Error saving student data: {e}")
        return False


def save_predictions_to_csv(student_id, probabilities, salary_distribution):
    """
    Save prediction results to Predicted_Data.csv
    Updates existing row if student_id exists, otherwise appends new row
    """
    try:
        # Create data directory if not exists
        os.makedirs(os.path.dirname(PREDICTIONS_CSV), exist_ok=True)
        
        # Calculate derived probabilities from salary_distribution
        derived_probs = {}
        if salary_distribution:
            derived_probs[">2 LPA"] = round((3/5 * salary_distribution.get("0-5 LPA", 0)) + 
                                           salary_distribution.get("5-10 LPA", 0) + 
                                           salary_distribution.get("10-15 LPA", 0) + 
                                           salary_distribution.get("15-20 LPA", 0) + 
                                           salary_distribution.get("20-30 LPA", 0) + 
                                           salary_distribution.get("30-40 LPA", 0) + 
                                           salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">5 LPA"] = round(salary_distribution.get("5-10 LPA", 0) + 
                                           salary_distribution.get("10-15 LPA", 0) + 
                                           salary_distribution.get("15-20 LPA", 0) + 
                                           salary_distribution.get("20-30 LPA", 0) + 
                                           salary_distribution.get("30-40 LPA", 0) + 
                                           salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">10 LPA"] = round(salary_distribution.get("10-15 LPA", 0) + 
                                            salary_distribution.get("15-20 LPA", 0) + 
                                            salary_distribution.get("20-30 LPA", 0) + 
                                            salary_distribution.get("30-40 LPA", 0) + 
                                            salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">15 LPA"] = round(salary_distribution.get("15-20 LPA", 0) + 
                                            salary_distribution.get("20-30 LPA", 0) + 
                                            salary_distribution.get("30-40 LPA", 0) + 
                                            salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">20 LPA"] = round(salary_distribution.get("20-30 LPA", 0) + 
                                            salary_distribution.get("30-40 LPA", 0) + 
                                            salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">25 LPA"] = round((5/10 * salary_distribution.get("20-30 LPA", 0)) + 
                                            salary_distribution.get("30-40 LPA", 0) + 
                                            salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">30 LPA"] = round(salary_distribution.get("30-40 LPA", 0) + 
                                            salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">35 LPA"] = round((5/10 * salary_distribution.get("30-40 LPA", 0)) + 
                                            salary_distribution.get(">40 LPA", 0), 1)
            derived_probs[">40 LPA"] = round(salary_distribution.get(">40 LPA", 0), 1)
        
        # Calculate salary range (min, mid, max)
        salary_pred = probabilities.get('salary_prediction', 0)
        salary_min = max(0, salary_pred * 0.7) if salary_pred else 0
        salary_mid = salary_pred if salary_pred else 0
        salary_max = max(0, salary_pred * 1.3) if salary_pred else 0
        
        # Prepare row data
        row_data = {
            'student_id': student_id,
            'overall_placement_probability': round(probabilities.get('overall_placement_probability', 0), 2),
            'predicted_salary_lpa': round(salary_pred, 2) if salary_pred else 0,
            'salary_range_min_lpa': round(salary_min, 2),
            'salary_range_mid_lpa': round(salary_mid, 2),
            'salary_range_max_lpa': round(salary_max, 2),
            'prob_salary_gt_2_lpa': derived_probs.get(">2 LPA", 0),
            'prob_salary_gt_5_lpa': derived_probs.get(">5 LPA", 0),
            'prob_salary_gt_10_lpa': derived_probs.get(">10 LPA", 0),
            'prob_salary_gt_15_lpa': derived_probs.get(">15 LPA", 0),
            'prob_salary_gt_20_lpa': derived_probs.get(">20 LPA", 0),
            'prob_salary_gt_25_lpa': derived_probs.get(">25 LPA", 0),
            'prob_salary_gt_30_lpa': derived_probs.get(">30 LPA", 0),
            'prob_salary_gt_35_lpa': derived_probs.get(">35 LPA", 0),
            'prob_salary_gt_40_lpa': derived_probs.get(">40 LPA", 0),
            'predicted_job_role': probabilities.get('job_role_prediction', ''),
            'recommended_companies': ','.join(probabilities.get('recommended_companies', []))
        }
        
        # Read or create dataframe
        if os.path.exists(PREDICTIONS_CSV):
            df = pd.read_csv(PREDICTIONS_CSV)
            
            # Check if student_id already exists
            student_idx = df[df['student_id'] == student_id].index
            
            if len(student_idx) > 0:
                # Update existing row
                for key, value in row_data.items():
                    df.at[student_idx[0], key] = value
            else:
                # Append new row
                df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        else:
            # Create new dataframe with all columns
            df = pd.DataFrame(columns=PREDICTION_COLUMNS)
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        
        # Save to CSV
        df.to_csv(PREDICTIONS_CSV, index=False)
        return True
        
    except Exception as e:
        print(f"Error saving predictions to CSV: {e}")
        import traceback
        traceback.print_exc()
        return False


def collect_dsa_score():
    """Collect DSA score from LeetCode"""
    print("\n" + "="*60)
    print("1 - DSA SCORE (From LeetCode)")
    print("="*60)

    username = input("\nEnter your LeetCode username (or press Enter to skip): ").strip()

    if not username:
        print("Skipping LeetCode integration...")
        while True:
            try:
                score = float(input("Enter DSA Score manually (0-100): "))
                if 0 <= score <= 100:
                    return score
                else:
                    print("Please enter a score between 0 and 100")
            except ValueError:
                print("Invalid input!")

    try:
        dsa = LeetCodeDSA(username)
        data = dsa.fetch_leetcode_data()

        if data is None:
            print("Could not fetch LeetCode data.")
            while True:
                try:
                    score = float(input("Enter DSA Score manually (0-100): "))
                    if 0 <= score <= 100:
                        return score
                except ValueError:
                    print("Invalid input!")

        score = dsa.calculate_dsa_score()
        dsa.print_report()
        return score
    except:
        print("Error fetching LeetCode data. Enter manually.")
        while True:
            try:
                score = float(input("Enter DSA Score manually (0-100): "))
                if 0 <= score <= 100:
                    return score
            except ValueError:
                print("Invalid input!")


def collect_project_score():
    """Collect project score from GitHub"""
    print("\n" + "="*60)
    print("2 - PROJECT SCORE (From GitHub)")
    print("="*60)

    try:
        count = int(input("\nHow many GitHub repositories? (or 0 to skip): "))
    except ValueError:
        count = 0

    if count <= 0:
        print("Skipping GitHub...")
        while True:
            try:
                score = float(input("Enter Project Score manually (0-100): "))
                if 0 <= score <= 100:
                    return score
            except ValueError:
                print("Invalid input!")

    try:
        github = GitHubProject()
        repos = []

        for i in range(count):
            url = input(f"\nEnter GitHub repo URL {i+1}: ").strip()
            if url:
                repos.append(url)

        if repos:
            score = github.evaluate_multiple_projects(repos)
            github.print_report()
            return score
        else:
            while True:
                try:
                    score = float(input("Enter Project Score manually (0-100): "))
                    if 0 <= score <= 100:
                        return score
                except ValueError:
                    print("Invalid input!")
    except:
        print("Error processing GitHub data. Enter manually.")
        while True:
            try:
                score = float(input("Enter Project Score manually (0-100): "))
                if 0 <= score <= 100:
                    return score
            except ValueError:
                print("Invalid input!")


def collect_aptitude_ats_scores():
    """Collect aptitude and ATS scores"""
    print("\n" + "="*60)
    print("3 - APTITUDE & ATS SCORES")
    print("="*60)

    try:
        aptitude_ats = AptitudeATS()
        apt_score, ats_score = aptitude_ats.get_scores()
        return apt_score, ats_score
    except:
        print("Error getting aptitude/ATS scores. Enter manually.")
        while True:
            try:
                apt = float(input("Enter Aptitude Score (0-100): "))
                ats = float(input("Enter ATS Score (0-100): "))
                if 0 <= apt <= 100 and 0 <= ats <= 100:
                    return apt, ats
            except ValueError:
                print("Invalid input!")


def collect_hr_score():
    """Collect HR round score"""
    print("\n" + "="*60)
    print("4 - HR ROUND INTERVIEW")
    print("="*60)

    try:
        hr = HRRound()
        hr.conduct_interview()
        hr_score = hr.calculate_hr_score()
        hr.print_report()
        return hr_score
    except:
        print("Error in HR round. Enter manually.")
        while True:
            try:
                score = float(input("Enter HR Score (0-100): "))
                if 0 <= score <= 100:
                    return score
            except ValueError:
                print("Invalid input!")


def show_student_info(student_data):
    """Show student information"""
    print("\n" + "="*60)
    print("CURRENT STUDENT PROFILE")
    print("="*60)

    print(f"\nBasic Info:")
    print(f"  Student ID: {student_data.get('student_id', 'N/A')}")
    print(f"  Name: {student_data.get('name', 'N/A')}")
    print(f"  Branch: {student_data.get('branch', 'N/A')}")
    print(f"  CGPA: {student_data.get('cgpa', 'N/A')}")

    print(f"\nCS Fundamentals:")
    print(f"  OS Score: {student_data.get('os_score', 'N/A')}")
    print(f"  DBMS Score: {student_data.get('dbms_score', 'N/A')}")
    print(f"  CN Score: {student_data.get('cn_score', 'N/A')}")
    print(f"  OOP Score: {student_data.get('oop_score', 'N/A')}")
    print(f"  System Design: {student_data.get('system_design_score', 'N/A')}")
    print(f"  CS Fundamentals: {student_data.get('cs_fundamentals_score', 'N/A')}")

    print(f"\nSkill Scores:")
    dsa = student_data.get('dsa_score', 'NOT SET')
    project = student_data.get('project_score', 'NOT SET')
    aptitude = student_data.get('aptitude_score', 'NOT SET')
    hr = student_data.get('hr_score', 'NOT SET')
    ats = student_data.get('resume_ats_score', 'NOT SET')

    print(f"  DSA Score: {dsa}")
    print(f"  Project Score: {project}")
    print(f"  Aptitude Score: {aptitude}")
    print(f"  HR Score: {hr}")
    print(f"  Resume ATS Score: {ats}")


def check_has_all_scores(student_data):
    """Check if student has all required scores for probability calculation"""
    required_scores = ['dsa_score', 'project_score', 'cs_fundamentals_score', 'aptitude_score']

    for score_key in required_scores:
        value = student_data.get(score_key)
        # Check if value is NaN or None or empty
        if value is None or pd.isna(value) or value == '':
            return False
    return True


def calculate_placement_probabilities(student_data):
    """Calculate service, product, and company-wise probabilities"""

    # Check if student has required scores
    if not check_has_all_scores(student_data):
        print("\nWarning: Some required scores are missing!")
        return None

    # Prepare student scores
    student_scores = {
        'dsa_score': float(student_data.get('dsa_score', 50)),
        'project_score': float(student_data.get('project_score', 50)),
        'cs_fundamentals_score': float(student_data.get('cs_fundamentals_score', 50)),
        'aptitude_score': float(student_data.get('aptitude_score', 50))
    }

    # MAIN: Use ML model to get base placement probability
    print("\n[STEP 1] Loading ML Models for placement prediction...")
    try:
        models_obj = MLModels()

        # Try to load existing models
        if models_obj.load_models():
            print("[OK] ML Models loaded successfully!")
        else:
            print("[!] Models not found. Training new models...")
            from train_models import train_all_models
            train_all_models()
            if not models_obj.load_models():
                raise Exception("Failed to load models after training")
            print("[OK] Models trained and loaded!")

        # Feature engineering
        fe = FeatureEngineering()
        fe.fitted = True
        fe.scaler = models_obj.scaler

        # Prepare student features
        student_features = fe.prepare_student_input(student_data)

        # GET PLACEMENT PROBABILITY FROM ML MODEL
        print("[STEP 2] Predicting placement probability using ML model...")
        raw_prob = models_obj.placement_model.predict_proba([student_features])[0][1]
        print(f"[OK] ML Raw Probability: {raw_prob:.4f}")

        # Apply realistic probability adjustments (from original code)
        skill_avg = (student_scores['dsa_score'] + student_scores['project_score'] +
                    student_scores['cs_fundamentals_score']) / 3
        soft_avg = (student_scores['aptitude_score'] + student_data.get('hr_score', 50)) / 2

        p = raw_prob
        if skill_avg < 40:
            p *= 0.4
            print(f"[!] Skill average low ({skill_avg:.1f}), applying 0.4 penalty")
        if soft_avg < 40:
            p *= 0.6
            print(f"[!] Soft skills low ({soft_avg:.1f}), applying 0.6 penalty")
        if student_data.get('cgpa', 6) < 6:
            p *= 0.5
            print(f"[!] CGPA low, applying 0.5 penalty")

        # Smoothing - Clamp probability between 5% and 100%
        ml_placement_prob = max(0.05, min(1.0, p))
        print(f"[OK] Adjusted ML Probability: {ml_placement_prob:.4f} ({ml_placement_prob*100:.2f}%)")

    except Exception as e:
        print(f"[ERROR] Error with ML model: {e}")
        print("[!] Falling back to default probability...")
        import traceback
        traceback.print_exc()
        ml_placement_prob = 0.65

    # STEP 3: Calculate service/product probabilities using NEW MODULE
    print("\n[STEP 3] Calculating service/product company probabilities...")
    sp_calc = ServiceProductProbability()
    sp_result = sp_calc.get_company_type_probability(ml_placement_prob, student_scores)

    service_prob = sp_result['service_probability']
    product_prob = sp_result['product_probability']
    print(f"[OK] Service Probability: {service_prob:.2f}%")
    print(f"[OK] Product Probability: {product_prob:.2f}%")

    # STEP 4: Get salary prediction from ML model
    print("\n[STEP 4] Predicting salary for placed students...")
    salary_pred = None
    salary_distribution = None
    
    try:
        if models_obj.salary_model:
            salary_pred = models_obj.salary_model.predict([student_features])[0]
            print(f"[OK] Predicted Salary: {salary_pred:.2f} LPA")
        else:
            print("[!] Salary model not available")
    except Exception as e:
        print(f"[!] Error predicting salary: {e}")
    
    # STEP 4B: Get salary tier distribution
    print("\n[STEP 4B] Predicting salary tier distribution...")
    try:
        salary_predictor = SalaryTierPredictor()
        if salary_predictor.load_model():
            # Predict salary tier distribution
            salary_distribution = salary_predictor.predict_salary_distribution(student_data)
            if salary_distribution:
                print(f"[OK] Salary tier distribution calculated!")
                # Show top 3 predicted tiers
                sorted_tiers = sorted(salary_distribution.items(), key=lambda x: x[1], reverse=True)
                for tier, prob in sorted_tiers[:3]:
                    print(f"     {tier}: {prob:.1f}%")
            else:
                print("[!] Failed to calculate salary distribution")
        else:
            print("[!] Salary tier model not found. Train it using: python train_salary_model.py")
    except Exception as e:
        print(f"[!] Error with salary tier prediction: {e}")

    # STEP 5: Get job role prediction from ML model
    print("\n[STEP 5] Predicting job role...")
    try:
        if models_obj.jobrole_model and models_obj.role_encoder:
            role_pred = models_obj.jobrole_model.predict([student_features])[0]
            role_name = models_obj.role_encoder.inverse_transform([role_pred])[0]
            print(f"[OK] Predicted Job Role: {role_name}")
        else:
            role_name = None
            print("[!] Job role model not available")
    except Exception as e:
        print(f"[!] Error predicting job role: {e}")
        role_name = None

    # STEP 6: Get company recommendations from KNN model
    print("\n[STEP 6] Finding recommended companies...")
    try:
        if models_obj.knn_companies and models_obj.companies_list is not None:
            distances, indices = models_obj.knn_companies.kneighbors([student_features], n_neighbors=min(10, len(models_obj.companies_list)))
            recommended_companies = [models_obj.companies_list[idx] for idx in indices[0]]
            print(f"[OK] Top recommended companies: {', '.join(recommended_companies[:5])}")
        else:
            recommended_companies = []
            print("[!] Company recommendation model not available")
    except Exception as e:
        print(f"[!] Error getting recommendations: {e}")
        recommended_companies = []

    return {
        'overall_placement_probability': ml_placement_prob * 100,
        'service_company_probability': service_prob,
        'product_company_probability': product_prob,
        'salary_prediction': salary_pred,
        'salary_distribution': salary_distribution,
        'job_role_prediction': role_name,
        'recommended_companies': recommended_companies
    }


def display_results(student_data, probabilities):
    """Display all results"""

    print("\n" + "="*60)
    print("PLACEMENT PREDICTION RESULTS")
    print("="*60)

    print(f"\nStudent ID: {student_data.get('student_id')}")
    print(f"Name: {student_data.get('name')}")

    print("\n[PLACEMENT PROBABILITY]")
    print(f"Overall Placement Probability: {probabilities['overall_placement_probability']:.2f}%")

    print("\n[ML MODEL PREDICTIONS]")

    # Salary prediction
    if probabilities.get('salary_prediction') is not None:
        print(f"Predicted Salary: {probabilities['salary_prediction']:.2f} LPA")
    else:
        print(f"Predicted Salary: Not available")

    # Salary tier distribution
    if probabilities.get('salary_distribution'):
        print("\n[SALARY TIER DISTRIBUTION]")
        salary_dist = probabilities['salary_distribution']
        # Sort by probability descending
        sorted_tiers = sorted(salary_dist.items(), key=lambda x: x[1], reverse=True)
        
        print("Probability by salary range:")
        for tier, prob in sorted_tiers:
            bar_length = int(prob / 5)
            bar = "█" * bar_length
            print(f"  {tier:12} → {prob:6.1f}% {bar}")
        
        # Calculate comprehensive derived probabilities
        # Direct calculation - no models needed, just mathematical cumulative logic
        try:
            derived_probs = {
                ">2 LPA": round((3/5 * salary_dist.get("0-5 LPA", 0)) + 
                               salary_dist.get("5-10 LPA", 0) + 
                               salary_dist.get("10-15 LPA", 0) + 
                               salary_dist.get("15-20 LPA", 0) + 
                               salary_dist.get("20-30 LPA", 0) + 
                               salary_dist.get("30-40 LPA", 0) + 
                               salary_dist.get(">40 LPA", 0), 1),
                ">5 LPA": round(salary_dist.get("5-10 LPA", 0) + 
                               salary_dist.get("10-15 LPA", 0) + 
                               salary_dist.get("15-20 LPA", 0) + 
                               salary_dist.get("20-30 LPA", 0) + 
                               salary_dist.get("30-40 LPA", 0) + 
                               salary_dist.get(">40 LPA", 0), 1),
                ">10 LPA": round(salary_dist.get("10-15 LPA", 0) + 
                                salary_dist.get("15-20 LPA", 0) + 
                                salary_dist.get("20-30 LPA", 0) + 
                                salary_dist.get("30-40 LPA", 0) + 
                                salary_dist.get(">40 LPA", 0), 1),
                ">15 LPA": round(salary_dist.get("15-20 LPA", 0) + 
                                salary_dist.get("20-30 LPA", 0) + 
                                salary_dist.get("30-40 LPA", 0) + 
                                salary_dist.get(">40 LPA", 0), 1),
                ">20 LPA": round(salary_dist.get("20-30 LPA", 0) + 
                                salary_dist.get("30-40 LPA", 0) + 
                                salary_dist.get(">40 LPA", 0), 1),
                ">25 LPA": round((5/10 * salary_dist.get("20-30 LPA", 0)) + 
                                salary_dist.get("30-40 LPA", 0) + 
                                salary_dist.get(">40 LPA", 0), 1),
                ">30 LPA": round(salary_dist.get("30-40 LPA", 0) + 
                                salary_dist.get(">40 LPA", 0), 1),
                ">35 LPA": round((5/10 * salary_dist.get("30-40 LPA", 0)) + 
                                salary_dist.get(">40 LPA", 0), 1),
                ">40 LPA": round(salary_dist.get(">40 LPA", 0), 1)
            }
        except Exception as e:
            print(f"[!] Error calculating derived probabilities: {e}")
            derived_probs = None
        
        # Display all derived probabilities
        if derived_probs:
            print("\n[DERIVED PROBABILITIES]")
            print("Cumulative chances of earning above thresholds:")
            for threshold in [">2 LPA", ">5 LPA", ">10 LPA", ">15 LPA", ">20 LPA", 
                            ">25 LPA", ">30 LPA", ">35 LPA", ">40 LPA"]:
                prob = derived_probs.get(threshold, 0)
                bar_length = int(prob / 5)
                bar = "█" * bar_length
                print(f"  Chance of {threshold:8} → {prob:6.1f}% {bar}")

    # Job role prediction
    if probabilities.get('job_role_prediction'):
        print(f"\nPredicted Job Role: {probabilities['job_role_prediction']}")
    else:
        print(f"\nPredicted Job Role: Not available")

    # Recommended companies
    if probabilities.get('recommended_companies'):
        print(f"Recommended Companies: {', '.join(probabilities['recommended_companies'][:5])}")
    else:
        print(f"Recommended Companies: Not available")

    print("\n" + "="*60)


def main():
    """Main function"""
    print_header()

    # Get student ID
    student_id = get_student_id()

    # Load student from CSV
    print(f"\nLoading student {student_id}...")
    student_data = load_student_from_csv(student_id)

    if student_data is None:
        print(f"Student ID {student_id} not found in database!")
        print(f"Available students: 200000-200099")
        return

    # Show current data
    show_student_info(student_data)

    # Check if scores are complete
    has_all_scores = check_has_all_scores(student_data)

    if has_all_scores:
        print("\n✓ Student has all required scores!")
        update = input("\nDo you want to UPDATE the skill scores? (y/n): ").strip().lower()
    else:
        print("\n! Student is missing some skill scores!")
        print("Collecting missing scores...")
        update = 'y'

    # Collect/Update scores if needed
    if update == 'y':
        print("\nCollecting skill scores...")
        dsa_score = collect_dsa_score()
        project_score = collect_project_score()
        aptitude_score, ats_score = collect_aptitude_ats_scores()
        hr_score = collect_hr_score()

        # Update student data
        student_data['dsa_score'] = dsa_score
        student_data['project_score'] = project_score
        student_data['aptitude_score'] = aptitude_score
        student_data['resume_ats_score'] = ats_score
        student_data['hr_score'] = hr_score

        # Save to CSV
        print("\nSaving scores to database...")
        if save_student_to_csv(student_id, student_data):
            print("Scores saved successfully!")
        else:
            print("Error saving scores!")
            return

    # Calculate probabilities
    print("\n" + "="*60)
    print("CALCULATING PLACEMENT PROBABILITIES")
    print("="*60)

    probabilities = calculate_placement_probabilities(student_data)

    if probabilities is None:
        print("Cannot calculate probabilities - missing required scores!")
        return

    # Save predictions to separate Predicted_Data.csv file
    print("\nSaving predictions to database...")
    salary_distribution = probabilities.get('salary_distribution')
    if save_predictions_to_csv(student_id, probabilities, salary_distribution):
        print("Predictions saved successfully!")
    else:
        print("Error saving predictions!")
        return

    # Display results
    display_results(student_data, probabilities)

    print("\nAll operations completed successfully!")
    print(f"Predictions saved to: {PREDICTIONS_CSV}")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
