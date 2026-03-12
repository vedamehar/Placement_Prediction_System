"""
HR Round Module
Evaluates HR round performance and soft skills
"""

import language_tool_python
from textstat import flesch_reading_ease
import pandas as pd


class HRRound:
    """Class for managing HR round evaluation"""
    
    QUESTIONS = [
        "Describe a project where you had a major responsibility. What was your role?",
        "Tell me about a time when your team faced a problem. How did you handle it?",
        "Describe a failure or mistake you made in a project. What did you learn?",
        "How do you handle pressure or tight deadlines?",
        "Explain a situation where you had to learn something new quickly."
    ]
    
    STAR_KEYWORDS = {
        "situation": ["when", "during", "situation", "project"],
        "task": ["responsible", "task", "goal", "role"],
        "action": ["i did", "i handled", "i decided", "i worked", "i took"],
        "result": ["result", "outcome", "learned", "improved", "success"]
    }
    
    OWNERSHIP_WORDS = ["i took responsibility", "i fixed", "i learned", "i handled", "i improved"]
    BLAME_WORDS = ["they failed", "because of others", "team failed", "their fault"]
    
    CONFIDENT_WORDS = ["confident", "comfortable", "clear", "sure"]
    NERVOUS_WORDS = ["nervous", "hesitate", "afraid", "not confident"]
    
    def __init__(self):
        self.answers = []
        self.scores = {}
        self.hr_score = 0
        
        try:
            self.tool = language_tool_python.LanguageTool('en-US')
        except:
            self.tool = None
    
    def conduct_interview(self):
        """Conduct HR interview"""
        print("\n" + "="*50)
        print("🎤 HR ROUND INTERVIEW")
        print("="*50)
        print("\nPlease answer the following questions in 5-8 sentences.")
        print("Be thoughtful and genuine in your responses.\n")
        
        for i, q in enumerate(self.QUESTIONS, 1):
            print(f"\nQ{i}. {q}")
            ans = input("Your answer:\n")
            self.answers.append(ans)
        
        return self.answers
    
    def communication_score(self, text):
        """Evaluate communication quality"""
        if self.tool:
            matches = self.tool.check(text)
            grammar_errors = len(matches)
        else:
            grammar_errors = 0
        
        words = text.split()
        word_count = len(words)
        readability = flesch_reading_ease(text)
        
        grammar_score = max(100 - grammar_errors * 3, 0)
        length_score = min(word_count / 120 * 100, 100)
        clarity_score = min(max(readability, 30), 100)
        
        final = (
            0.15 * grammar_score +
            0.35 * clarity_score +
            0.50 * length_score
        )
        return round(final, 2)
    
    def star_score(self, text):
        """Evaluate STAR structure"""
        text = text.lower()
        score = 0
        for keywords in self.STAR_KEYWORDS.values():
            if any(k in text for k in keywords):
                score += 1
        return round((score / 4) * 100, 2)
    
    def ownership_score(self, text):
        """Evaluate ownership and accountability"""
        text = text.lower()
        score = 0
        
        if any(w in text for w in self.OWNERSHIP_WORDS):
            score += 70
        if any(w in text for w in self.BLAME_WORDS):
            score -= 30
        
        return max(min(score, 100), 0)
    
    def confidence_consistency(self):
        """Evaluate confidence consistency"""
        confidence_hits = 0
        nervous_hits = 0
        
        for ans in self.answers:
            t = ans.lower()
            if any(w in t for w in self.CONFIDENT_WORDS):
                confidence_hits += 1
            if any(w in t for w in self.NERVOUS_WORDS):
                nervous_hits += 1
        
        if confidence_hits > 0 and nervous_hits > 0:
            return 50
        elif confidence_hits > 0:
            return 90
        elif nervous_hits > 0:
            return 60
        else:
            return 70
    
    def calculate_hr_score(self):
        """Calculate final HR score"""
        if not self.answers:
            return 0
        
        combined_text = " ".join(self.answers)
        
        comm = self.communication_score(combined_text)
        star = sum(self.star_score(a) for a in self.answers) / len(self.answers)
        ownership = sum(self.ownership_score(a) for a in self.answers) / len(self.answers)
        consistency = self.confidence_consistency()
        
        self.scores = {
            'communication': comm,
            'star_structure': star,
            'ownership': ownership,
            'consistency': consistency
        }
        
        self.hr_score = round(
            0.25 * comm +
            0.25 * star +
            0.25 * ownership +
            0.25 * consistency,
            2
        )
        
        return self.hr_score
    
    def get_hr_score(self):
        """Get HR score"""
        return self.hr_score
    
    def print_report(self):
        """Print HR evaluation report"""
        print("\n" + "="*50)
        print("HR EVALUATION REPORT")
        print("="*50)
        print(f"Communication Score: {self.scores.get('communication', 0)}/100")
        print(f"STAR Structure Score: {self.scores.get('star_structure', 0):.2f}/100")
        print(f"Ownership & Accountability: {self.scores.get('ownership', 0):.2f}/100")
        print(f"Confidence Consistency: {self.scores.get('consistency', 0)}/100")
        print(f"\n🎯 Final HR Score: {self.hr_score}/100")
        
        if self.hr_score < 35:
            level = "Low HR Readiness (Needs significant practice)"
        elif self.hr_score < 55:
            level = "Basic HR Readiness"
        elif self.hr_score < 70:
            level = "Moderate HR Readiness (Entry-level suitable)"
        elif self.hr_score < 85:
            level = "Strong HR Readiness"
        else:
            level = "Very Strong HR Readiness (Confident fresher)"
        
        print(f"Assessment: {level}")
        print("="*50)
