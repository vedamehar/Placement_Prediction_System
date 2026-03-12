"""
Aptitude and ATS Module
Evaluates quantitative aptitude and ATS compatibility
"""

import webbrowser


class AptitudeATS:
    """Class for evaluating aptitude test scores and ATS compatibility"""
    
    APTITUDE_LINK = "https://aptitude-test.com/"
    ATS_LINK = "https://enhancv.com/resources/resume-checker/"
    
    def __init__(self):
        self.aptitude_score = None
        self.ats_score = None
    
    def get_aptitude_score(self):
        """Get aptitude test score"""
        print("\n" + "="*50)
        print("📋 APTITUDE TEST")
        print("="*50)
        print(f"\nPlease visit: {self.APTITUDE_LINK}")
        print("\nTake the aptitude test and note your score.")
        print("You can open the link in your browser.")
        
        try:
            open_link = input("\nDo you want to open the link? (y/n): ").strip().lower()
            if open_link == 'y':
                webbrowser.open(self.APTITUDE_LINK)
        except:
            pass
        
        while True:
            try:
                score = float(input("\nEnter your Aptitude Score (0-100): "))
                if 0 <= score <= 100:
                    self.aptitude_score = score
                    print(f"✅ Aptitude Score: {score}/100")
                    return score
                else:
                    print("❌ Please enter a score between 0 and 100")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def get_ats_score(self):
        """Get ATS resume score"""
        print("\n" + "="*50)
        print("📄 RESUME ATS SCORE")
        print("="*50)
        print(f"\nPlease visit: {self.ATS_LINK}")
        print("\nUpload your resume and check your ATS score.")
        print("You can open the link in your browser.")
        
        try:
            open_link = input("\nDo you want to open the link? (y/n): ").strip().lower()
            if open_link == 'y':
                webbrowser.open(self.ATS_LINK)
        except:
            pass
        
        while True:
            try:
                score = float(input("\nEnter your Resume ATS Score (0-100): "))
                if 0 <= score <= 100:
                    self.ats_score = score
                    print(f"✅ Resume ATS Score: {score}/100")
                    return score
                else:
                    print("❌ Please enter a score between 0 and 100")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def get_scores(self):
        """Get both scores"""
        apt = self.get_aptitude_score()
        ats = self.get_ats_score()
        return apt, ats
