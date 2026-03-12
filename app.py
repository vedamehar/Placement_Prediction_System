"""
Flask API Server for EduPlus Placement Prediction System
Connects Python backend with React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os
import requests as http_requests
from pathlib import Path

# Import Python modules
from modules.leetcode_dsa import LeetCodeDSA
from modules.github_project import GitHubProject
from modules.aptitude_ats import AptitudeATS
from modules.hr_round import HRRound
from modules.ml_models import MLModels
from modules.feature_engineering import FeatureEngineering
from modules.service_product_probability import ServiceProductProbability
from modules.salary_probability import SalaryTierPredictor
import pandas as pd

app = Flask(__name__)
CORS(app)

# File paths
STUDENT_CSV = os.path.join(os.path.dirname(__file__), 'data/student_profiles_100.csv')
PREDICTIONS_CSV = os.path.join(os.path.dirname(__file__), 'data/Predicted_Data.csv')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'EduPlus API is running'})

@app.route('/api/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get student info - validates if student exists"""
    try:
        if not os.path.exists(STUDENT_CSV):
            print(f"[ERROR] Student CSV not found at {STUDENT_CSV}")
            return jsonify({'exists': False, 'message': 'Student data not found'}), 404
        
        df = pd.read_csv(STUDENT_CSV)
        print(f"[DEBUG] Loaded {len(df)} students from CSV")
        print(f"[DEBUG] Looking for student_id: {student_id}, Type: {type(student_id)}")
        
        # Ensure student_id column is integer type
        df['student_id'] = df['student_id'].astype(int)
        student = df[df['student_id'] == student_id]
        
        print(f"[DEBUG] Found {len(student)} matching students")
        
        if len(student) == 0:
            print(f"[ERROR] Student {student_id} not found in CSV")
            return jsonify({
                'exists': False,
                'message': 'Student not found',
                'student_id': student_id
            }), 404
        
        student_row = student.iloc[0].to_dict()
        student_name = str(student_row.get('name', 'Unknown'))
        
        print(f"[SUCCESS] Found student: {student_name} (ID: {student_id})")
        
        # Check if prediction exists
        last_prediction = None
        if os.path.exists(PREDICTIONS_CSV):
            try:
                pred_df = pd.read_csv(PREDICTIONS_CSV)
                pred_df['student_id'] = pred_df['student_id'].astype(int)
                pred = pred_df[pred_df['student_id'] == student_id]
                if len(pred) > 0:
                    last_prediction = pred.iloc[0].to_dict()
                    print(f"[DEBUG] Found existing prediction for student {student_id}")
            except Exception as pe:
                print(f"[DEBUG] No predictions file or error reading: {pe}")
        
        response = {
            'exists': True,
            'name': student_name,
            'id': student_id,
            'student_id': student_id,
            'data': student_row,
            'lastPrediction': last_prediction
        }
        
        print(f"[RESPONSE] Returning: {response}")
        return jsonify(response), 200
    
    except Exception as e:
        print(f"[EXCEPTION] Error in get_student: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'exists': False}), 500

@app.route('/api/integrations/leetcode', methods=['POST'])
def fetch_leetcode():
    """Fetch LeetCode score from username"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'error': 'Username required', 'score': None}), 400
        
        print(f"[LeetCode] Fetching score for username: {username}")
        
        # Create instance with username
        leetcode = LeetCodeDSA(username)
        
        # Fetch data from LeetCode API
        lc_data = leetcode.fetch_leetcode_data()
        
        if lc_data is None:
            print(f"[LeetCode] Username '{username}' not found or API error")
            return jsonify({
                'error': 'Username not found. Please enter score manually.',
                'score': None,
                'username': username
            }), 200
        
        # Calculate score from fetched data
        score = leetcode.calculate_dsa_score()
        
        print(f"[LeetCode] Successfully calculated score: {score} for user: {username}")
        
        return jsonify({
            'score': score,
            'username': username,
            'source': 'leetcode',
            'data': lc_data
        }), 200
    
    except Exception as e:
        print(f"[LeetCode] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Error fetching LeetCode data: {str(e)}',
            'score': None
        }), 200

@app.route('/api/integrations/github', methods=['POST'])
def fetch_github():
    """Fetch GitHub score from username"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'error': 'Username required', 'score': None}), 400
        
        print(f"[GitHub] Fetching data for username: {username}")
        
        # Verify user exists using GitHub API
        import requests
        try:
            # Simple GitHub API call to check if user exists
            response = requests.get(
                f'https://api.github.com/users/{username}',
                timeout=5,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            if response.status_code != 200:
                print(f"[GitHub] Username '{username}' not found (status: {response.status_code})")
                return jsonify({
                    'error': 'GitHub username not found. Please enter score manually.',
                    'score': None,
                    'username': username
                }), 200
            
            user_data = response.json()
            
            # Calculate score based on public repos and other metrics
            public_repos = user_data.get('public_repos', 0)
            followers = user_data.get('followers', 0)
            
            # Simple scoring: base 30 + (repos * 3) + (followers * 0.5), capped at 100
            score = min(30 + (public_repos * 3) + (followers * 0.5), 100)
            score = round(max(score, 0), 2)  # Ensure >= 0
            
            print(f"[GitHub] Successfully calculated score: {score} for user: {username}")
            
            return jsonify({
                'score': score,
                'username': username,
                'source': 'github',
                'public_repos': public_repos,
                'followers': followers
            }), 200
            
        except requests.exceptions.RequestException as req_err:
            print(f"[GitHub] Request error: {str(req_err)}")
            return jsonify({
                'error': f'Could not verify GitHub user. Please enter score manually.',
                'score': None
            }), 200
    
    except Exception as e:
        print(f"[GitHub] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Error fetching GitHub data: {str(e)}',
            'score': None
        }), 200

@app.route('/api/integrations/github-projects', methods=['POST'])
def evaluate_github_projects():
    """Evaluate GitHub project repositories properly"""
    try:
        print("\n" + "#"*70)
        print("# 📡 INCOMING REQUEST: /api/integrations/github-projects (POST)")
        print("#"*70)
        
        data = request.json
        repo_urls = data.get('repo_urls', [])
        
        print(f"\n[REQUEST] Received {len(repo_urls)} repository URL(s):")
        for idx, url in enumerate(repo_urls, 1):
            print(f"  [{idx}] {url}")
        
        if not repo_urls:
            print(f"\n[ERROR] No repositories provided in request")
            return jsonify({
                'error': 'No repositories provided',
                'score': None
            }), 400
        
        print(f"\n[INIT] Initializing GitHub Project Analyzer...")
        
        # Use GitHubProject module to properly evaluate repos
        github = GitHubProject()
        
        print(f"\n" + "="*70)
        print(f"[BACKEND] Starting GitHub Project Evaluation Process")
        print(f"="*70)
        
        average_score = github.evaluate_multiple_projects(repo_urls)
        
        print(f"="*70)
        print(f"[BACKEND] GitHub evaluation process completed successfully")
        print(f"="*70)
        
        print(f"\n[RESPONSE PREP] Preparing response data...")
        print(f"  • Repositories analyzed: {len(github.repos)}")
        print(f"  • Average score: {average_score}/100")
        print(f"  • Sanitizing data for transmission...")
        
        # Sanitize repos data for JSON serialization
        sanitized_repos = []
        for repo_idx, repo in enumerate(github.repos, 1):
            try:
                print(f"     [Repo {repo_idx}/{len(github.repos)}] Encoding repo data...")
                sanitized_repo = {}
                for key, value in repo.items():
                    try:
                        if isinstance(value, (int, float, bool)):
                            sanitized_repo[key] = value
                        elif isinstance(value, list):
                            sanitized_repo[key] = [str(v).encode('utf-8', errors='ignore').decode('utf-8') for v in value]
                        else:
                            sanitized_repo[key] = str(value).encode('utf-8', errors='ignore').decode('utf-8')
                    except Exception as field_err:
                        print(f"        ⚠️  Could not sanitize field '{key}': {field_err}")
                        sanitized_repo[key] = None
                sanitized_repos.append(sanitized_repo)
                print(f"     ✅ Repo {repo_idx} encoded successfully")
            except Exception as repo_err:
                print(f"  ❌ Error encoding repo {repo_idx}: {repo_err}")
        
        print(f"\n[RESPONSE PREP] All data sanitized and ready")
        print(f"[RESPONSE] Transmitting {len(sanitized_repos)} repositories to frontend")
        print(f"[RESPONSE] HTTP Status: 200 OK")
        print("#"*70 + "\n")
        
        return jsonify({
            'score': float(average_score),
            'repo_count': len(repo_urls),
            'repos': sanitized_repos,
            'message': f'Analyzed {len(repo_urls)} repositories'
        }), 200
    
    except Exception as e:
        print(f"\n[ERROR] Exception occurred during GitHub evaluation:")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Error Message: {str(e)}")
        import traceback
        print(f"\nFull Traceback:")
        traceback.print_exc()
        print("#"*70 + "\n")
        return jsonify({
            'error': f'Error evaluating repositories: {str(e)}',
            'score': None
        }), 200

@app.route('/api/aptitude/links', methods=['GET'])
def get_aptitude_links():
    """Get aptitude test links"""
    return jsonify({
        'aptitude_url': 'https://aptitude-test.com/',
        'ats_url': 'https://enhancv.com/resources/resume-checker/'
    }), 200

@app.route('/api/hr-round/questions', methods=['GET'])
def get_hr_questions():
    """Get HR round questions"""
    questions = [
        "Describe a project where you had a major responsibility. What was your role?",
        "Tell me about a time when your team faced a problem. How did you handle it?",
        "Describe a failure or mistake you made in a project. What did you learn?",
        "How do you handle pressure or tight deadlines?",
        "Explain a situation where you had to learn something new quickly."
    ]
    return jsonify({'questions': questions}), 200

@app.route('/api/hr-round/evaluate', methods=['POST'])
def evaluate_hr_round():
    """Evaluate HR round answers"""
    try:
        data = request.json
        answers = data.get('answers', [])
        
        if not answers or len(answers) == 0:
            return jsonify({
                'error': 'No answers provided',
                'score': None
            }), 400
        
        print(f"[HR Round] Evaluating {len(answers)} answers")
        
        # Use HRRound module to evaluate
        hr = HRRound()
        hr.answers = answers
        hr_score = hr.calculate_hr_score()
        
        print(f"[HR Round] HR score calculated: {hr_score}/100")
        
        return jsonify({
            'score': float(hr_score),
            'breakdown': {
                'communication': float(hr.scores.get('communication', 0)),
                'star_structure': float(hr.scores.get('star_structure', 0)),
                'ownership': float(hr.scores.get('ownership', 0)),
                'consistency': float(hr.scores.get('consistency', 0))
            },
            'message': 'HR evaluation complete'
        }), 200
    
    except Exception as e:
        print(f"[HR Round] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Error evaluating HR round: {str(e)}',
            'score': None
        }), 200

@app.route('/api/predictions/generate', methods=['POST'])
def generate_predictions():
    """Generate placement predictions"""
    try:
        data = request.json
        
        # Only take the required 5 scores, but add defaults for ML model compatibility
        student_data = {
            'student_id': data.get('studentId'),
            'dsa_score': float(data.get('dsa_score', 50)),
            'project_score': float(data.get('project_score', 50)),
            'aptitude_score': float(data.get('aptitude_score', 50)),
            'hr_score': float(data.get('hr_score', 50)),
            'resume_ats_score': float(data.get('resume_ats_score', 50)),
            'github_projects': int(data.get('github_projects', 0)),
            'github_project_links': data.get('github_project_links', []),
            # Add defaults for ML model compatibility (not used in input, but required by feature engineering)
            'cs_fundamentals_score': 50.0,  # Default value
            'cgpa': 7.0,  # Default value
            'hackathon_wins': 0  # Default value
        }
        
        print(f"[PREDICTION] Generating prediction for student {student_data['student_id']}")
        print(f"[PREDICTION] Input scores: DSA={student_data['dsa_score']}, Project={student_data['project_score']}, "
              f"Aptitude={student_data['aptitude_score']}, HR={student_data['hr_score']}, ATS={student_data['resume_ats_score']}")
        
        # Prepare ML inputs using only the 5 scores
        student_scores = {
            'dsa_score': student_data['dsa_score'],
            'project_score': student_data['project_score'],
            'aptitude_score': student_data['aptitude_score'],
            'hr_score': student_data['hr_score'],
            'resume_ats_score': student_data['resume_ats_score']
        }
        
        # Load ML models
        models_obj = MLModels()
        if not models_obj.load_models():
            raise Exception("Failed to load ML models")
        
        # Feature engineering - create student features from the 5 scores
        fe = FeatureEngineering()
        fe.fitted = True
        fe.scaler = models_obj.scaler
        
        # Create feature vector from the 5 scores (with defaults for other fields)
        student_features = fe.prepare_student_input(student_data)
        
        print(f"[PREDICTION] Feature vector shape: {student_features.shape if hasattr(student_features, 'shape') else len(student_features)}")
        
        # Get placement probability
        try:
            raw_prob = models_obj.placement_model.predict_proba([student_features])[0][1]
            print(f"[PREDICTION] Raw ML probability: {raw_prob}")
        except Exception as e:
            print(f"[PREDICTION] Error getting placement probability: {e}")
            raw_prob = 0.5
        
        # Apply penalties based on scores
        skill_avg = (student_scores['dsa_score'] + student_scores['project_score']) / 2
        soft_avg = (student_scores['aptitude_score'] + student_data.get('hr_score', 50)) / 2
        
        p = raw_prob
        if skill_avg < 40:
            p *= 0.4
            print(f"[PREDICTION] Applied skill penalty (avg: {skill_avg})")
        if soft_avg < 40:
            p *= 0.6
            print(f"[PREDICTION] Applied soft skill penalty (avg: {soft_avg})")
        
        ml_placement_prob = max(0.05, min(1.0, p))
        print(f"[PREDICTION] Adjusted ML probability: {ml_placement_prob}")
        
        # Get salary prediction
        salary_pred = None
        salary_distribution = None
        
        try:
            if models_obj.salary_model:
                salary_pred_raw = models_obj.salary_model.predict([student_features])[0]
                salary_pred = max(3.0, min(50.0, salary_pred_raw))  # Clamp between 3-50 LPA
                print(f"[PREDICTION] Predicted salary: {salary_pred} LPA")
            else:
                salary_pred = 5.0  # Default salary
        except Exception as e:
            print(f"[PREDICTION] Error predicting salary: {e}")
            salary_pred = 5.0
        
        # Get salary distribution
        try:
            salary_predictor = SalaryTierPredictor()
            if salary_predictor.load_model():
                salary_distribution = salary_predictor.predict_salary_distribution(student_data)
                print(f"[PREDICTION] Salary distribution computed")
            else:
                # Create default distribution
                salary_distribution = {
                    "0-5 LPA": 0.4,
                    "5-10 LPA": 0.3,
                    "10-15 LPA": 0.15,
                    "15-20 LPA": 0.08,
                    "20-30 LPA": 0.05,
                    "30-40 LPA": 0.02,
                    ">40 LPA": 0.01
                }
        except Exception as e:
            print(f"[PREDICTION] Error getting salary distribution: {e}")
            salary_distribution = {
                "0-5 LPA": 0.4,
                "5-10 LPA": 0.3,
                "10-15 LPA": 0.15,
                "15-20 LPA": 0.08,
                "20-30 LPA": 0.05,
                "30-40 LPA": 0.02,
                ">40 LPA": 0.01
            }
        
        # Get job role
        role_name = "SDE"
        try:
            if models_obj.jobrole_model and models_obj.role_encoder:
                role_pred = models_obj.jobrole_model.predict([student_features])[0]
                role_name = models_obj.role_encoder.inverse_transform([role_pred])[0]
                print(f"[PREDICTION] Predicted job role: {role_name}")
        except Exception as e:
            print(f"[PREDICTION] Error predicting job role: {e}")
            role_name = "Software Engineer"
        
        # Get company recommendations
        recommended_companies = []
        try:
            if models_obj.knn_companies and models_obj.companies_list is not None:
                distances, indices = models_obj.knn_companies.kneighbors([student_features], n_neighbors=5)
                recommended_companies = [models_obj.companies_list[idx] for idx in indices[0]]
                print(f"[PREDICTION] Recommended companies: {recommended_companies}")
        except Exception as e:
            print(f"[PREDICTION] Error getting company recommendations: {e}")
            recommended_companies = []
        
        # Calculate derived probabilities
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
        
        # Calculate salary ranges
        salary_min = max(0, salary_pred * 0.7) if salary_pred else 0
        salary_mid = salary_pred if salary_pred else 0
        salary_max = max(0, salary_pred * 1.3) if salary_pred else 0
        
        response_data = {
            'success': True,
            'overall_placement_probability': float(round(ml_placement_prob * 100, 2)),
            'predicted_salary_lpa': float(round(salary_pred, 2)) if salary_pred else 0,
            'salary_range_min_lpa': float(round(salary_min, 2)),
            'salary_range_mid_lpa': float(round(salary_mid, 2)),
            'salary_range_max_lpa': float(round(salary_max, 2)),
            'prob_salary_gt_2_lpa': float(derived_probs.get(">2 LPA", 0)),
            'prob_salary_gt_5_lpa': float(derived_probs.get(">5 LPA", 0)),
            'prob_salary_gt_10_lpa': float(derived_probs.get(">10 LPA", 0)),
            'prob_salary_gt_15_lpa': float(derived_probs.get(">15 LPA", 0)),
            'prob_salary_gt_20_lpa': float(derived_probs.get(">20 LPA", 0)),
            'prob_salary_gt_25_lpa': float(derived_probs.get(">25 LPA", 0)),
            'prob_salary_gt_30_lpa': float(derived_probs.get(">30 LPA", 0)),
            'prob_salary_gt_35_lpa': float(derived_probs.get(">35 LPA", 0)),
            'prob_salary_gt_40_lpa': float(derived_probs.get(">40 LPA", 0)),
            'predicted_job_role': str(role_name),
            'recommended_companies': [str(c) for c in recommended_companies]
        }
        
        print(f"[PREDICTION] [OK] Prediction completed successfully")
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"[ERROR] Error generating predictions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/predictions/save', methods=['POST'])
def save_predictions():
    """Save predictions to CSV"""
    try:
        data = request.json
        student_id = data.get('studentId')
        predictions = data.get('predictions', {})
        
        # Prepare row
        row_data = {
            'student_id': student_id,
            'overall_placement_probability': predictions.get('overall_placement_probability', 0),
            'predicted_salary_lpa': predictions.get('predicted_salary_lpa', 0),
            'salary_range_min_lpa': predictions.get('salary_range_min_lpa', 0),
            'salary_range_mid_lpa': predictions.get('salary_range_mid_lpa', 0),
            'salary_range_max_lpa': predictions.get('salary_range_max_lpa', 0),
            'prob_salary_gt_2_lpa': predictions.get('prob_salary_gt_2_lpa', 0),
            'prob_salary_gt_5_lpa': predictions.get('prob_salary_gt_5_lpa', 0),
            'prob_salary_gt_10_lpa': predictions.get('prob_salary_gt_10_lpa', 0),
            'prob_salary_gt_15_lpa': predictions.get('prob_salary_gt_15_lpa', 0),
            'prob_salary_gt_20_lpa': predictions.get('prob_salary_gt_20_lpa', 0),
            'prob_salary_gt_25_lpa': predictions.get('prob_salary_gt_25_lpa', 0),
            'prob_salary_gt_30_lpa': predictions.get('prob_salary_gt_30_lpa', 0),
            'prob_salary_gt_35_lpa': predictions.get('prob_salary_gt_35_lpa', 0),
            'prob_salary_gt_40_lpa': predictions.get('prob_salary_gt_40_lpa', 0),
            'predicted_job_role': predictions.get('predicted_job_role', ''),
            'recommended_companies': ','.join(predictions.get('recommended_companies', []))
        }
        
        # Read or create CSV
        if os.path.exists(PREDICTIONS_CSV):
            df = pd.read_csv(PREDICTIONS_CSV)
            student_idx = df[df['student_id'] == student_id].index
            
            if len(student_idx) > 0:
                for key, value in row_data.items():
                    df.at[student_idx[0], key] = value
            else:
                df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        else:
            df = pd.DataFrame([row_data])
        
        df.to_csv(PREDICTIONS_CSV, index=False)
        
        return jsonify({'success': True, 'message': 'Predictions saved'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<int:student_id>', methods=['GET'])
def get_predictions(student_id):
    """Get student predictions"""
    try:
        if not os.path.exists(PREDICTIONS_CSV):
            return jsonify({'predictions': None}), 200
        
        df = pd.read_csv(PREDICTIONS_CSV)
        pred = df[df['student_id'] == student_id]
        
        if len(pred) == 0:
            return jsonify({'predictions': None}), 200
        
        predictions = pred.iloc[0].to_dict()
        return jsonify({'predictions': predictions}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

RASA_WEBHOOK_URL = os.environ.get('RASA_URL', 'http://localhost:5005') + '/webhooks/rest/webhook'

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """Proxy messages to the Rasa chatbot server"""
    try:
        data = request.json
        student_id = data.get('student_id')
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        rasa_payload = {
            'sender': str(student_id) if student_id else 'anonymous',
            'message': message
        }

        rasa_response = http_requests.post(
            RASA_WEBHOOK_URL,
            json=rasa_payload,
            timeout=15
        )
        rasa_response.raise_for_status()

        bot_messages = rasa_response.json()  # list of {recipient_id, text, ...}
        answer = ' '.join(msg.get('text', '') for msg in bot_messages if msg.get('text'))

        if not answer:
            answer = "I'm sorry, I didn't understand that. Could you rephrase?"

        return jsonify({
            'answer': answer,
            'source': 'rasa_chatbot'
        }), 200

    except http_requests.exceptions.ConnectionError:
        return jsonify({
            'answer': 'The chatbot server is not running. Please start the Rasa server first.',
            'intent': 'error',
            'source': 'error'
        }), 503
    except http_requests.exceptions.Timeout:
        return jsonify({
            'answer': 'The chatbot took too long to respond. Please try again.',
            'intent': 'error',
            'source': 'error'
        }), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
