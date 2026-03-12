"""
Placement Prediction Chatbot Actions
Integrates with the Backend API for placement predictions
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import json

# Backend API URL
BACKEND_API_URL = "http://localhost:5000"


class ActionGetPlacementProbability(Action):
    """Get placement probability for a student"""
    
    def name(self) -> Text:
        return "action_get_placement_probability"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Execute the action"""
        try:
            # Try to get student ID from slots
            student_id = tracker.get_slot("student_id")
            
            if not student_id:
                # Ask for student ID
                dispatcher.utter_message(
                    text="I'd be happy to help! To get your placement probability, I need your Student ID. "
                         "Please provide your Student ID (e.g., 200001)."
                )
                return []
            
            # Call backend API
            response = requests.post(
                f"{BACKEND_API_URL}/api/predict",
                json={"student_id": int(student_id)},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                placement = data['data']['placement']
                
                message = (
                    f"📊 **Your Placement Analysis**\n\n"
                    f"Student ID: {student_id}\n"
                    f"Name: {data['data']['name']}\n"
                    f"Branch: {data['data']['branch']}\n"
                    f"CGPA: {data['data']['cgpa']}\n\n"
                    f"**Placement Probabilities:**\n"
                    f"• Overall: {placement['overall_probability']:.2f}%\n"
                    f"• Service Companies: {placement['service_company_prob']:.2f}%\n"
                    f"• Product Companies: {placement['product_company_prob']:.2f}%\n"
                )
                
                if placement.get('predicted_salary'):
                    message += f"\n💰 Predicted Salary: ₹{placement['predicted_salary']:.2f} LPA\n"
                
                if placement.get('predicted_role'):
                    message += f"👔 Predicted Role: {placement['predicted_role']}\n"
                
                dispatcher.utter_message(text=message)
                
                # Store student ID for follow-up questions
                return [SlotSet("student_id", student_id)]
            
            elif response.status_code == 404:
                error_data = response.json()
                dispatcher.utter_message(
                    text=f"❌ {error_data.get('error', 'Student not found')}\n\n"
                         f"Valid Student IDs are 200000-200099. "
                         f"Please check and try again with a valid ID."
                )
                return [SlotSet("student_id", None)]
            
            else:
                error_data = response.json()
                dispatcher.utter_message(
                    text=f"⚠️ Error: {error_data.get('error', 'Unable to calculate prediction')}\n\n"
                         f"Details: {error_data.get('details', 'Unknown error')}"
                )
                return []
        
        except requests.exceptions.ConnectionError:
            dispatcher.utter_message(
                text="❌ Cannot connect to the prediction service. "
                     "Please make sure the backend API is running on http://localhost:5000"
            )
            return []
        
        except requests.exceptions.Timeout:
            dispatcher.utter_message(
                text="❌ Request timeout. The prediction service is taking too long to respond."
            )
            return []
        
        except Exception as e:
            dispatcher.utter_message(
                text=f"❌ Error: {str(e)}\n\n"
                     f"Please try again or contact support."
            )
            return []


class ActionGetEligibleCompanies(Action):
    """Get companies a student is eligible for"""
    
    def name(self) -> Text:
        return "action_get_eligible_companies"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Execute the action"""
        try:
            student_id = tracker.get_slot("student_id")
            
            if not student_id:
                dispatcher.utter_message(
                    text="I need your Student ID to check eligible companies. "
                         "Please provide your Student ID (e.g., 200001)."
                )
                return []
            
            # Call backend API
            response = requests.post(
                f"{BACKEND_API_URL}/api/predict",
                json={"student_id": int(student_id)},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                eligible_companies = data['data']['eligible_companies']
                
                if not eligible_companies:
                    dispatcher.utter_message(
                        text="Based on your current profile, you may not be eligible for any companies yet. "
                             "Consider improving your skills to increase eligibility."
                    )
                    return []
                
                # Group by tier
                tier1 = [c for c in eligible_companies if 'Tier-1' in c.get('tier', '')]
                tier2 = [c for c in eligible_companies if 'Tier-2' in c.get('tier', '')]
                tier3 = [c for c in eligible_companies if 'Tier-3' in c.get('tier', '')]
                
                message = "🏢 **Eligible Companies:**\n\n"
                
                if tier1:
                    message += "**Tier-1 Companies:**\n"
                    for company in tier1[:5]:  # Show top 5
                        message += f"• {company['name']} - {company['category']}\n"
                    message += "\n"
                
                if tier2:
                    message += "**Tier-2 Companies:**\n"
                    for company in tier2[:5]:
                        message += f"• {company['name']} - {company['category']}\n"
                    message += "\n"
                
                if tier3:
                    message += "**Tier-3 Companies:**\n"
                    for company in tier3[:5]:
                        message += f"• {company['name']} - {company['category']}\n"
                
                message += f"\n*Total eligible: {len(eligible_companies)} companies*"
                dispatcher.utter_message(text=message)
                
                return []
            
            else:
                error_data = response.json()
                dispatcher.utter_message(
                    text=f"❌ Error: {error_data.get('error', 'Cannot fetch companies')}"
                )
                return []
        
        except Exception as e:
            dispatcher.utter_message(
                text=f"❌ Error: {str(e)}"
            )
            return []


class ActionGetSkillGap(Action):
    """Get skill gap analysis for a student"""
    
    def name(self) -> Text:
        return "action_get_skill_gap"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Execute the action"""
        try:
            student_id = tracker.get_slot("student_id")
            
            if not student_id:
                dispatcher.utter_message(
                    text="Please provide your Student ID to get skill gap analysis."
                )
                return []
            
            # Call backend API
            response = requests.post(
                f"{BACKEND_API_URL}/api/predict",
                json={"student_id": int(student_id)},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                scores = data['data']['skills']
                
                # Identify gaps
                gaps = []
                for skill, score in scores.items():
                    if score < 70:
                        gaps.append((skill, score))
                
                gaps.sort(key=lambda x: x[1])
                
                message = "📈 **Your Skill Gap Analysis:**\n\n"
                
                if gaps:
                    message += "**Areas to Improve (Score < 70):**\n"
                    for skill, score in gaps:
                        message += f"• {skill.replace('_', ' ').title()}: {score:.1f} → Target: 80+\n"
                else:
                    message += "✅ Great! Your skills are above 70 in all areas!\n"
                
                message += "\n**Current Scores:**\n"
                for skill, score in sorted(scores.items(), key=lambda x: x[1]):
                    status = "✅" if score >= 80 else "⚠️" if score >= 70 else "❌"
                    message += f"{status} {skill.replace('_', ' ').title()}: {score:.1f}\n"
                
                dispatcher.utter_message(text=message)
                
                return []
            
            else:
                error_data = response.json()
                dispatcher.utter_message(
                    text=f"❌ Error: {error_data.get('error')}"
                )
                return []
        
        except Exception as e:
            dispatcher.utter_message(
                text=f"❌ Error: {str(e)}"
            )
            return []
