"""
LeetCode DSA Module
Evaluates student's LeetCode problem-solving skills
"""

import requests
from datetime import datetime


class LeetCodeDSA:
    """Class for evaluating DSA skills based on LeetCode profile"""
    
    def __init__(self, username):
        self.username = username
        self.data = None
        self.score = 0
    
    def fetch_leetcode_data(self):
        """Fetch data from LeetCode API"""
        url = "https://leetcode.com/graphql"
        
        query = """
        query getUserData($username: String!) {
          matchedUser(username: $username) {
            submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
              }
              totalSubmissionNum {
                difficulty
                count
              }
            }
            tagProblemCounts {
              fundamental { tagName problemsSolved }
              intermediate { tagName problemsSolved }
              advanced { tagName problemsSolved }
            }
            submissionCalendar
          }
          userContestRanking(username: $username) {
            attendedContestsCount
            rating
          }
        }
        """
        
        payload = {"query": query, "variables": {"username": self.username}}
        
        try:
            res = requests.post(url, json=payload, timeout=10)
            data = res.json()
            
            if data["data"]["matchedUser"] is None:
                return None
            
            user = data["data"]["matchedUser"]
            
            stats = user["submitStatsGlobal"]["acSubmissionNum"]
            total = stats[0]["count"]
            easy = stats[1]["count"]
            medium = stats[2]["count"]
            hard = stats[3]["count"]
            
            total_sub = user["submitStatsGlobal"]["totalSubmissionNum"][0]["count"]
            acceptance_rate = round((total / total_sub) * 100, 2) if total_sub else 0
            
            calendar = eval(user["submissionCalendar"])
            active_days = len(calendar)
            
            dates = sorted([int(ts) for ts in calendar.keys()])
            max_streak = 0
            streak = 0
            prev = None
            
            for ts in dates:
                day = datetime.fromtimestamp(ts).date()
                if prev is None or (day - prev).days == 1:
                    streak += 1
                else:
                    streak = 1
                max_streak = max(max_streak, streak)
                prev = day
            
            topic_counts = {}
            for level in ["fundamental", "intermediate", "advanced"]:
                for tag in user["tagProblemCounts"][level]:
                    topic_counts[tag["tagName"].lower()] = tag["problemsSolved"]
            
            def get_topic(name):
                return topic_counts.get(name, 0)
            
            topics = {
                "arrays": get_topic("array"),
                "strings": get_topic("string"),
                "trees": get_topic("tree"),
                "graphs": get_topic("graph"),
                "dp": get_topic("dynamic programming"),
                "linked_list": get_topic("linked list"),
                "binary_search": get_topic("binary search")
            }
            
            contest = data["data"]["userContestRanking"]
            contest_rating = contest["rating"] if contest and contest["rating"] else 0
            contests_attended = contest["attendedContestsCount"] if contest else 0
            
            self.data = {
                "easy": easy,
                "medium": medium,
                "hard": hard,
                "total": total,
                "acceptance_rate": acceptance_rate,
                "active_days": active_days,
                "max_streak": max_streak,
                "topics": topics,
                "contest_rating": contest_rating,
                "contests_attended": contests_attended
            }
            
            return self.data
        
        except Exception as e:
            print(f"❌ Error fetching LeetCode data: {e}")
            return None
    
    def normalize(self, value, max_value):
        """Normalize value to 0-100 scale"""
        return min((value / max_value) * 100, 100) if max_value else 0
    
    def calculate_dsa_score(self):
        """Calculate DSA score from LeetCode data"""
        if self.data is None:
            return 0
        
        easy = self.data["easy"]
        medium = self.data["medium"]
        hard = self.data["hard"]
        total = self.data["total"]
        
        if total == 0:
            return 0
        
        acceptance = self.data["acceptance_rate"]
        topics = self.data["topics"]
        active_days = self.data["active_days"]
        max_streak = self.data["max_streak"]
        contest_rating = self.data["contest_rating"]
        contests_attended = self.data["contests_attended"]
        
        # Problem Solving Strength (40%)
        difficulty_weight = (1*easy + 2*medium + 3*hard) / total
        volume_score = self.normalize(total, 600)
        pss = 0.6 * volume_score + 0.3 * (difficulty_weight * 30) + 0.1 * acceptance
        
        # Topic Mastery (25%)
        topic_scores = []
        for v in topics.values():
            topic_scores.append(self.normalize(v, 60))
        tms = sum(topic_scores) / len(topic_scores) if topic_scores else 0
        
        # Consistency (20%)
        cs = 0.6 * self.normalize(active_days, 365) + 0.4 * self.normalize(max_streak, 90)
        
        # Competitive Programming (15%)
        if contests_attended >= 3:
            cps = 0.7 * self.normalize(contest_rating, 2800) + 0.3 * self.normalize(contests_attended, 20)
            contest_weight = 0.15
        else:
            cps = 0
            contest_weight = 0.05
        
        # Final Score
        self.score = (
            0.40 * pss +
            0.25 * tms +
            0.20 * cs +
            contest_weight * cps
        )
        
        return round(self.score, 2)
    
    def get_dsa_score(self):
        """Get final DSA score"""
        return round(self.score, 2)
    
    def print_report(self):
        """Print DSA assessment report"""
        if self.data is None:
            print("❌ No LeetCode data available")
            return
        
        print("\n" + "="*50)
        print("LeetCode DSA Assessment Report")
        print("="*50)
        print(f"Username: {self.username}")
        print(f"Total Solved: {self.data['total']} (Easy: {self.data['easy']}, Medium: {self.data['medium']}, Hard: {self.data['hard']})")
        print(f"Acceptance Rate: {self.data['acceptance_rate']}%")
        print(f"Active Days: {self.data['active_days']} | Max Streak: {self.data['max_streak']}")
        print(f"Contest Rating: {self.data['contest_rating']} | Contests: {self.data['contests_attended']}")
        print("\nTopic Coverage:")
        for k, v in self.data["topics"].items():
            print(f"  {k}: {v}")
        print(f"\nDSA Score: {self.score}/100")
        print("="*50)
