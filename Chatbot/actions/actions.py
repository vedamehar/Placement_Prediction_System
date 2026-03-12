import pandas as pd
from typing import Any, Text, Dict, List, Optional, Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from fuzzywuzzy import process
import os

# Import placement prediction actions
try:
    from .actions_placement import (
        ActionGetPlacementProbability,
        ActionGetEligibleCompanies,
        ActionGetSkillGap
    )
    PLACEMENT_ACTIONS_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Could not import placement actions: {e}")
    PLACEMENT_ACTIONS_AVAILABLE = False

# INTERNAL PERSISTENT LOGGING FOR AUDIT
DEBUG_FILE = os.path.join(os.path.dirname(__file__), "../audit_debug.txt")

def log_debug(msg):
    try:
        with open(DEBUG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
        print(msg) # Still print to terminal
    except Exception as e:
        print(f"[WARNING] Could not write to debug file: {e}")

# Clear log on startup (optional - comment out to keep logs)
# if os.path.exists(DEBUG_FILE):
#     os.remove(DEBUG_FILE)

# ==================== DATA PATHS ====================
# Centralised data directory at the project root (shared with Flask backend)
# Future CSV files for training should be placed in the same folder.
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "company_profiles_with_difficulty.csv")

# ==================== GLOBAL DATA STORE ====================
class DataStore:
    """Singleton data loader for CSV"""
    _df = None
    _company_list = []

    @classmethod
    def load(cls):
        try:
            cls._df = pd.read_csv(CSV_PATH)
            cls._df['company_name'] = cls._df['company_name'].astype(str)
            cls._company_list = cls._df['company_name'].tolist()
            print(f"[DATA] Loaded {len(cls._company_list)} companies from CSV")
        except FileNotFoundError:
            print(f"[ERROR] {CSV_PATH} not found")
            cls._df = pd.DataFrame()
        except Exception as e:
            print(f"[ERROR] CSV Load Error: {e}")
            cls._df = pd.DataFrame()

    @classmethod
    def get_df(cls):
        if cls._df is None:
            cls.load()
        return cls._df

    @classmethod
    def get_company_list(cls):
        if not cls._company_list:
            cls.load()
        return cls._company_list

# Initialize on import
DataStore.load()

# ==================== ENTITY RESOLVER ====================
# ==================== ENTITY RESOLVER ====================

ALIAS_MAP = {
    'micro': 'Microsoft',
    'ms': 'Microsoft',
    'goog': 'Google',
    'ggl': 'Google',
    'amzn': 'Amazon',
    'tcs': 'TCS',
    'infy': 'Infosys'
}

def _backlogs_allowed_count(val) -> int:
    """Convert backlogs_allowed to int (0 = not allowed, >0 = max backlogs).
    Handles both legacy True/False strings and new-style integer values."""
    try:
        return int(float(str(val)))
    except (ValueError, TypeError):
        return 1 if str(val).strip().lower() == 'true' else 0

def resolve_alias(text: Text) -> Optional[Text]:
    """Strict Rule-Based Alias Resolution"""
    if not text:
        return None
    tokens = text.lower().replace('?', '').replace('.', '').split()
    for token in tokens:
        if token in ALIAS_MAP:
            return ALIAS_MAP[token]
    return None

def resolve_company(tracker: Tracker) -> Tuple[Optional[Text], Optional[Text]]:
    """
    ENHANCED: Alias (Rule) -> Entity -> Fuzzy -> Context
    Returns: (company, match_source)
    """
    intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
    
    # Whitelist of intents allowed to use context (follow-ups)
    CONTEXT_ALLOWED_INTENTS = [
        'ask_avg_package', 'ask_max_package', 'ask_min_cgpa', 
        'ask_allowed_departments', 'ask_required_skills', 
        'ask_backlog_allowed', 'ask_max_backlogs', 'ask_company_backlogs',
        'ask_company_tier', 'ask_hiring_roles', 
        'ask_eligibility_summary', 'ask_interview_process', 
        'ask_preparation_roadmap', 'ask_company_eligibility',
        'ask_prep_topics_by_area',
        # New human-like intents
        'ask_company_overview', 'ask_company_difficulty', 'ask_company_skills',
        'ask_company_hiring_pattern', 'ask_company_job_roles', 'ask_company_category',
        'ask_company_tier_info', 'ask_company_preparation', 'ask_company_suitability',
        'ask_company_departments', 'ask_company_backlog_info',
    ]

    print(f"[DEBUG] RAW ENTITIES: {tracker.latest_message.get('entities', [])}")

    latest_entity = next(
        (e['value'] for e in tracker.latest_message.get('entities', []) 
         if e['entity'] == 'company'), 
        None
    )
    
    previous_company_slot = tracker.get_slot("company") # Added check for 'company' slot
    
    # Context check (Only if intent is in whitelist)
    # Priority: Context Slot > Company Slot
    last_company = tracker.get_slot("last_company_asked")
    if intent not in CONTEXT_ALLOWED_INTENTS:
        last_company = None
        previous_company_slot = None
    
    raw_text = tracker.latest_message.get('text', '')
    
    print(f"[DEBUG] Intent: {intent} | Entity: {latest_entity} | Context Allowed: {intent in CONTEXT_ALLOWED_INTENTS} | Last Context: {last_company} | Company Slot: {previous_company_slot}")
    
    company_list = DataStore.get_company_list()
    if not company_list:
        return None, None
    
    # Priority 0: Strict Alias Mapping (Rule-Based)
    alias_match = resolve_alias(raw_text)
    if alias_match:
        print(f"[DEBUG] resolve_company | match_source: alias | match: {alias_match}")
        return alias_match, 'alias'
    
    # Priority 1: Use entity if available
    if latest_entity:
        target = latest_entity
        threshold = 60
        best_match, score = process.extractOne(target, company_list)
        if score >= threshold:
            print(f"[DEBUG] match_source: entity | score: {score} | match: {best_match}")
            return best_match, 'entity'
    
    # Priority 2: Fuzzy match on raw text (Only if intent implies a company query)
    IF_COMPANY_INTENT = latest_entity or intent in CONTEXT_ALLOWED_INTENTS or "topic" in raw_text.lower() or "eligible" in raw_text.lower()
    
    if IF_COMPANY_INTENT:
        target = raw_text
        # Lower threshold for raw text if keywords are present
        threshold = 70 if any(k in raw_text.lower() for k in ["topic", "prep", "eligible", "criteria"]) else 85
        best_match, score = process.extractOne(target, company_list)
        if score >= threshold:
            log_debug(f"[DEBUG] resolve_company | match_source: fuzzy | score: {score} | match: {best_match} | query: {target}")
            log_debug(f"[DEBUG] resolve_company | match_source: fuzzy | score: {score} | match: {best_match} | query: {target}")
            return best_match, 'fuzzy'
            
    # CRITICAL: If alias/fuzzy failed, DO NOT fallback to context if it's a completely new query 
    # that looks like a company name but failed validation.
    # But current logic only checks context if 'last_company' exists.
    
    # Priority 3: Use context if allowed
    
    # 3a. Use 'last_company_asked' (Immediate previous context)
    if last_company:
        log_debug(f"[DEBUG] resolve_company | match_source: context | value: {last_company}")
        return last_company, 'context'
        
    # 3b. Use 'company' slot (Holding state from 'inform_company')
    if previous_company_slot:
        log_debug(f"[DEBUG] resolve_company | match_source: slot_company | value: {previous_company_slot}")
        return previous_company_slot, 'context'
        
    log_debug(f"[DEBUG] resolve_company | No company resolved | Intent: {intent} | Text: {raw_text}")
    return None, None

# ==================== HUMAN-LIKE RESPONSE TEMPLATES ====================

def _tier_label(tier_val) -> str:
    t = str(tier_val).strip()
    if '1' in t:   return "Tier-1"
    if '2' in t:   return "Tier-2"
    if '3' in t:   return "Tier-3"
    return str(t)

def _difficulty_label(d) -> str:
    try:
        v = float(d)
        if v >= 8:   return "highly competitive"
        if v >= 6:   return "moderately competitive"
        return "relatively accessible"
    except Exception:
        return "competitive"

def _hiring_label(h) -> str:
    try:
        v = float(h)
        if v >= 8:   return "a mass recruiter hiring a large number of students"
        if v >= 5:   return "a selective recruiter that hires in moderate numbers"
        return "a niche recruiter that hires very selectively"
    except Exception:
        return "an active campus recruiter"

def _backlogs_sentence(row) -> str:
    max_bl = _backlogs_allowed_count(row['backlogs_allowed'])
    if max_bl == 0:
        return "No backlogs are allowed — candidates must have a clean academic record."
    return f"Students with up to {max_bl} active backlog(s) are allowed to apply."

# --- TEMPLATE 1: Company Overview ---
def tpl_company_overview(row) -> str:
    tier = _tier_label(row['company_tier'])
    diff = _difficulty_label(row['difficulty_factor'])
    if tier == "Tier-1":
        tier_note = "one of the most sought-after companies on campus"
    elif tier == "Tier-2":
        tier_note = "a strong mid-tier company with good growth opportunities"
    else:
        tier_note = "a service-oriented company that hires in large volumes"
    return (
        f"{row['company_name']} is a {tier} {row['company_cat']} company and is considered {tier_note}.\n\n"
        f"It recruits fresh engineering graduates primarily for roles such as {row['job_role_notes']}.\n\n"
        f"The average salary offered is around {row['avg_package_lpa']} LPA, and the highest package "
        f"can reach up to {row['max_package_lpa']} LPA.\n\n"
        f"Students need a minimum CGPA of {row['min_cgpa']} to apply, and the company accepts "
        f"candidates from departments such as {row['allowed_departments']}.\n\n"
        f"Key skills required include: {row['required_skills']}.\n\n"
        f"The hiring process is {diff}, with an overall difficulty rating of "
        f"{row['difficulty_factor']}/10."
    )

# --- TEMPLATE 2: Eligibility ---
def tpl_eligibility(row) -> str:
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        cgpa_note = "This is a premium company, so the CGPA bar is strict."
    elif tier == "Tier-2":
        cgpa_note = "This is reasonable for a mid-tier company."
    else:
        cgpa_note = "This is a relatively low bar, making it accessible to most students."
    return (
        f"To apply for {row['company_name']}, students need a minimum CGPA of {row['min_cgpa']}. "
        f"{cgpa_note}\n\n"
        f"Eligible departments include: {row['allowed_departments']}.\n\n"
        f"{_backlogs_sentence(row)}\n\n"
        f"Candidates should also have skills such as {row['required_skills']} to improve their chances."
    )

# --- TEMPLATE 3: Salary / Package ---
def tpl_salary(row) -> str:
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        comp_note = "Being a Tier-1 company, Google offers some of the most competitive salaries in campus placements."
    elif tier == "Tier-2":
        comp_note = f"As a Tier-2 company, {row['company_name']} offers above-average salaries compared to most campus recruiters."
    else:
        comp_note = f"As a Tier-3 company, {row['company_name']} primarily focuses on volume hiring with standard industry packages."
    # Fix the hardcoded "google" — use company_name
    comp_note = comp_note.replace("Google", row['company_name'])
    return (
        f"{row['company_name']} offers competitive packages for fresh graduates.\n\n"
        f"The average salary is around {row['avg_package_lpa']} LPA, while the highest package "
        f"can go up to {row['max_package_lpa']} LPA.\n\n"
        f"{comp_note}"
    )

# --- TEMPLATE 4: Difficulty ---
def tpl_difficulty(row) -> str:
    d = float(row['difficulty_factor']) if str(row['difficulty_factor']).replace('.','').isdigit() else 5
    tier = _tier_label(row['company_tier'])
    if d >= 8:
        opening = f"Getting into {row['company_name']} is considered very tough."
    elif d >= 6:
        opening = f"Getting into {row['company_name']} requires solid preparation."
    else:
        opening = f"{row['company_name']} has a relatively accessible hiring process for well-prepared students."
    if tier == "Tier-1":
        tier_note = "As a Tier-1 company, the bar for technical skills is significantly higher."
    elif tier == "Tier-2":
        tier_note = "As a Tier-2 company, both technical and communication skills matter equally."
    else:
        tier_note = "As a Tier-3 company, aptitude and basics are weighted more heavily."
    return (
        f"{opening} The overall difficulty is rated {row['difficulty_factor']}/10.\n\n"
        f"{tier_note}\n\n"
        f"Here is how the company weights each area during recruitment:\n"
        f"  • DSA & Problem Solving : {row['weight_dsa']}\n"
        f"  • Project Experience    : {row['weight_projects']}\n"
        f"  • CS Fundamentals       : {row['weight_cs']}\n"
        f"  • Aptitude Tests        : {row['weight_aptitude']}\n"
        f"  • HR Interview          : {row['weight_hr']}\n\n"
        f"Focus on the highest-weighted areas to maximise your chances."
    )

# --- TEMPLATE 5: Skills ---
def tpl_skills(row) -> str:
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        focus = "For a Tier-1 company like this, DSA and system design are the most critical areas."
    elif tier == "Tier-2":
        focus = "For a Tier-2 company, a balanced approach across DSA, CS fundamentals, and projects works best."
    else:
        focus = "For a Tier-3 company, aptitude tests and basic programming skills are usually sufficient to clear the initial rounds."
    return (
        f"To get selected at {row['company_name']}, you should develop the following skills:\n\n"
        f"Core required skills: {row['required_skills']}\n\n"
        f"{focus}\n\n"
        f"Recruitment area weights:\n"
        f"  • DSA                   : {row['weight_dsa']}\n"
        f"  • Project Experience    : {row['weight_projects']}\n"
        f"  • CS Fundamentals       : {row['weight_cs']}\n"
        f"  • Aptitude              : {row['weight_aptitude']}"
    )

# --- TEMPLATE 6: Departments ---
def tpl_departments(row) -> str:
    depts = str(row['allowed_departments'])
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        note = "Most Tier-1 companies prefer students from CS/IT backgrounds due to their strong technical focus."
    else:
        note = "Students from related technical branches also stand a good chance if their skills are strong."
    return (
        f"Students from the following departments are eligible to apply for {row['company_name']}:\n"
        f"{depts}\n\n"
        f"{note}"
    )

# --- TEMPLATE 7: Backlog Policy ---
def tpl_backlog_policy(row) -> str:
    max_bl = _backlogs_allowed_count(row['backlogs_allowed'])
    tier = _tier_label(row['company_tier'])
    if max_bl == 0:
        verdict = f"{row['company_name']} has a strict no-backlog policy."
        advice = "You must clear all pending backlogs before applying."
    else:
        verdict = f"{row['company_name']} allows students with up to {max_bl} active backlog(s) to apply."
        advice = "However, clearing your backlogs improves your profile significantly."
    if tier == "Tier-1":
        tier_note = "Tier-1 companies are typically very strict about academic records."
    elif tier == "Tier-2":
        tier_note = "Tier-2 companies are somewhat flexible, but prefer a clean record."
    else:
        tier_note = "Tier-3 companies tend to be more lenient about backlogs during mass hiring."
    return f"{verdict} {tier_note}\n\n{advice}"

# --- TEMPLATE 8: Hiring Pattern ---
def tpl_hiring_pattern(row) -> str:
    return (
        f"{row['company_name']} is {_hiring_label(row['hiring_intensity'])}.\n\n"
        f"The hiring intensity is rated {row['hiring_intensity']}/10, which reflects how actively "
        f"the company participates in campus placements and how many students it typically selects.\n\n"
        f"This is a {row['company_cat']} company, which means its workforce requirements "
        f"are shaped by {'product development cycles' if 'product' in str(row['company_cat']).lower() else 'client project demands and service delivery'}."
    )

# --- TEMPLATE 9: Job Roles ---
def tpl_job_roles(row) -> str:
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        role_note = "These roles are highly competitive and involve working on cutting-edge products used by millions."
    elif tier == "Tier-2":
        role_note = "These roles offer good career growth and exposure to both product and service work."
    else:
        role_note = "These roles are suitable for freshers looking to build industry experience."
    return (
        f"{row['company_name']} typically hires fresh graduates for roles such as:\n"
        f"{row['job_role_notes']}\n\n"
        f"{role_note}"
    )

# --- TEMPLATE 10: Category ---
def tpl_category(row) -> str:
    cat = str(row['company_cat'])
    if 'product' in cat.lower():
        desc = "primarily builds its own software products and platforms"
    elif 'service' in cat.lower():
        desc = "primarily delivers IT services to external clients"
    else:
        desc = "operates across both product and service verticals"
    return (
        f"{row['company_name']} is categorised as a {cat} company.\n\n"
        f"This means the company {desc}. "
        f"The type of work you do, the tech stack you use, and the growth trajectory "
        f"you can expect will all be influenced by this classification."
    )

# --- TEMPLATE 11: Tier ---
def tpl_tier(row) -> str:
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        meaning = ("Tier-1 companies offer the highest salaries, have the toughest interview processes, "
                   "and are the most prestigious. Getting into a Tier-1 company is considered a top achievement.")
    elif tier == "Tier-2":
        meaning = ("Tier-2 companies offer good salaries and career growth. They are competitive but more "
                   "accessible than Tier-1. A strong foundation in CS fundamentals and communication skills is key.")
    else:
        meaning = ("Tier-3 companies focus on mass hiring. They are ideal for students who want to enter "
                   "the industry quickly and build experience before moving to higher-tier roles.")
    return f"{row['company_name']} is classified as a {tier} company.\n\n{meaning}"

# --- TEMPLATE 12: Preparation ---
def tpl_preparation(row) -> str:
    tier = _tier_label(row['company_tier'])
    if tier == "Tier-1":
        strategy = ("Focus heavily on DSA — practice 150+ problems on LeetCode. "
                    "Learn system design concepts and be ready for 4-5 interview rounds.")
    elif tier == "Tier-2":
        strategy = ("Balance your preparation between DSA, CS fundamentals (DBMS, OS, OOPS), "
                    "and one or two strong projects. Typically 2-3 interview rounds.")
    else:
        strategy = ("Focus on aptitude tests, basic programming, and verbal communication. "
                    "Tier-3 hiring often starts with an online test, followed by HR rounds.")
    return (
        f"To prepare for {row['company_name']}, here is what you should focus on:\n\n"
        f"Core skills: {row['required_skills']}\n\n"
        f"Preparation areas by weight:\n"
        f"  • DSA                   : {row['weight_dsa']}\n"
        f"  • CS Fundamentals       : {row['weight_cs']}\n"
        f"  • Project Experience    : {row['weight_projects']}\n"
        f"  • Aptitude              : {row['weight_aptitude']}\n"
        f"  • HR Interview          : {row['weight_hr']}\n\n"
        f"Strategy: {strategy}"
    )

# --- TEMPLATE 13: Suitability (requires student row too) ---
def tpl_suitability(student, row) -> str:
    cgpa_ok = float(student.get('cgpa', 0)) >= float(row['min_cgpa'])
    max_bl  = _backlogs_allowed_count(row['backlogs_allowed'])
    eligibility = "eligible" if cgpa_ok else "not currently eligible"
    if cgpa_ok:
        cgpa_msg = (f"Your CGPA of {student['cgpa']} meets the minimum requirement of {row['min_cgpa']}. "
                    f"That is a good start!")
    else:
        gap = round(float(row['min_cgpa']) - float(student.get('cgpa', 0)), 2)
        cgpa_msg = (f"Your CGPA of {student['cgpa']} is {gap} points below "
                    f"the required {row['min_cgpa']}.")
    return (
        f"Based on your academic profile, you are {eligibility} to apply for {row['company_name']}.\n\n"
        f"{cgpa_msg}\n\n"
        f"The company allows up to {max_bl} backlog(s).\n\n"
        f"To improve your chances, focus on strengthening: {row['required_skills']}."
    )

# --- TEMPLATE 14: Comparison (two company rows) ---
def tpl_comparison(r1, r2) -> str:
    pkg_winner  = r1['company_name'] if float(r1['avg_package_lpa']) >= float(r2['avg_package_lpa']) else r2['company_name']
    diff_easier = r1['company_name'] if float(r1['difficulty_factor']) <= float(r2['difficulty_factor']) else r2['company_name']
    cgpa_lower  = r1['company_name'] if float(r1['min_cgpa']) <= float(r2['min_cgpa']) else r2['company_name']
    return (
        f"Here is a comparison between {r1['company_name']} and {r2['company_name']}:\n\n"
        f"Average Package:\n"
        f"  • {r1['company_name']} : {r1['avg_package_lpa']} LPA\n"
        f"  • {r2['company_name']} : {r2['avg_package_lpa']} LPA\n"
        f"  → {pkg_winner} offers a higher average salary.\n\n"
        f"Difficulty Level:\n"
        f"  • {r1['company_name']} : {r1['difficulty_factor']}/10\n"
        f"  • {r2['company_name']} : {r2['difficulty_factor']}/10\n"
        f"  → {diff_easier} has a relatively easier selection process.\n\n"
        f"Minimum CGPA:\n"
        f"  • {r1['company_name']} : {r1['min_cgpa']}\n"
        f"  • {r2['company_name']} : {r2['min_cgpa']}\n"
        f"  → {cgpa_lower} has a lower CGPA requirement."
    )

# ==================== LAYER 1: COMPANY-SPECIFIC ACTIONS ====================

class ActionGetAvgPackage(Action):
    def name(self) -> Text:
        return "action_get_avg_package"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's average package? (e.g., 'Google average package')")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            response = tpl_salary(row)
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
        except IndexError:
            response = f"Average package data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetMaxPackage(Action):
    def name(self) -> Text:
        return "action_get_max_package"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's maximum package?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            # Show max package highlighted within full salary template
            response = tpl_salary(row)
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
        except IndexError:
            response = f"Maximum package data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetMinCGPA(Action):
    def name(self) -> Text:
        return "action_get_min_cgpa"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's CGPA requirement?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            val = row['min_cgpa']
            tier = _tier_label(row['company_tier'])
            if tier == "Tier-1":
                note = "This is a premium company — the CGPA bar is strict."
            elif tier == "Tier-2":
                note = "This is reasonable for a mid-tier company."
            else:
                note = "This is a relatively accessible requirement."
            response = f"{company} requires a minimum CGPA of {val}. {note}"
            print(f"[DEBUG] Action: {self.name()} | Company: {company} | CGPA: {val}")
        except IndexError:
            response = f"CGPA data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetAllowedDepartments(Action):
    def name(self) -> Text:
        return "action_get_allowed_departments"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's branch eligibility?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            response = tpl_departments(row)
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
        except IndexError:
            response = f"Branch eligibility data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetRequiredSkills(Action):
    def name(self) -> Text:
        return "action_get_required_skills"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's skill requirements?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            response = tpl_skills(row)
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
        except IndexError:
            response = f"Skill data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetCompanyBacklogPolicy(Action):
    def name(self) -> Text:
        return "action_get_company_backlog_policy"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's backlog policy?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
            response = tpl_backlog_policy(row)
                
        except IndexError:
            response = f"Backlog policy not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetCompanyTier(Action):
    def name(self) -> Text:
        return "action_get_company_tier"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's tier?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            response = tpl_tier(row)
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
        except IndexError:
            response = f"Tier data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetHiringRoles(Action):
    def name(self) -> Text:
        return "action_get_hiring_roles"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker) # FIXED: Resolve company first

        if not company:
            dispatcher.utter_message(text="Which company's hiring roles?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            response = tpl_job_roles(row)
            print(f"[DEBUG] Action: {self.name()} | Company: {company}")
        except IndexError:
            response = f"Hiring roles data not available for {company}."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetEligibilitySummary(Action):
    def name(self) -> Text:
        return "action_get_eligibility_summary"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's eligibility criteria?")
            return [SlotSet("company_name", None)]
        
        print(f"[ACTION] {self.name()} | Resolved Company: {company}")
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            print(f"[ACTION] {self.name()} | CSV Row Index: {row_index}")
            response = tpl_eligibility(row)
        except IndexError:
            print(f"[ACTION] {self.name()} | ERROR: Company not found in CSV")
            response = f"Eligibility data not available for {company}."
        
        dispatcher.utter_message(text=response)
        events = [SlotSet("company", None)]
        if source in ['entity', 'fuzzy', 'alias']:
            events.append(SlotSet("last_company_asked", company))
        else:
            events.append(SlotSet("last_company_asked", None))
        return events

class ActionCheckEligibility(Action):
    def name(self) -> Text:
        return "action_check_eligibility"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        
        if not company:
             dispatcher.utter_message(text="Which company's eligibility do you want to check?")
             return [SlotSet("company_name", None)]
        
        text = tracker.latest_message.get('text', '')
        import re
        
        # Regex for text-based extraction
        cgpa_pattern = r'(\d+(?:\.\d+)?)\s*(?:cgpa|pointer|cp|gpa)'
        backlog_pattern = r'(\d+)\s*(?:backlogs?|active backlogs?)'
        
        cgpa_match = re.search(cgpa_pattern, text, re.IGNORECASE)
        backlog_match = re.search(backlog_pattern, text, re.IGNORECASE)
        
        user_cgpa = float(cgpa_match.group(1)) if cgpa_match else None
        user_backlogs = int(backlog_match.group(1)) if backlog_match else 0
        
        if user_cgpa is None:
             dispatcher.utter_message(text=f"Please specify your CGPA to check eligibility for {company}. (e.g. 'I have 8.5 CGPA')")
             return [SlotSet("company", None), SlotSet("last_company_asked", company)]
             
        df = DataStore.get_df()
        try:
             row_index = df[df['company_name'] == company].index[0]
             row = df.iloc[row_index]
             
             min_cgpa = float(row['min_cgpa'])
             max_backlogs = _backlogs_allowed_count(row['backlogs_allowed'])
             backlogs_allowed = max_backlogs > 0
             
             cgpa_ok = user_cgpa >= min_cgpa
             backlog_ok = (user_backlogs <= max_backlogs) if backlogs_allowed else (user_backlogs == 0)
            
             is_eligible = cgpa_ok and backlog_ok
             status_icon = "✅ Eligible" if is_eligible else "❌ Not Eligible"
             cgpa_sym = "✔" if cgpa_ok else "❌"
             backlog_sym = "✔" if backlog_ok else "❌"
             
             print(f"[DEBUG] Action: {self.name()} | Company: {company} | CGPA: {user_cgpa} vs {min_cgpa} | Backlogs: {user_backlogs} vs {max_backlogs}")

             response = (
                 f"🎯 Eligibility Assessment for {company}:\n\n"
                 f"{cgpa_sym} CGPA: {user_cgpa} (Min required: {min_cgpa})\n"
                 f"{backlog_sym} Backlogs: {user_backlogs} (Max allowed: {max_backlogs if backlogs_allowed else 0})\n\n"
                 f"📢 Result: You are {status_icon} for {company}."
             )
             dispatcher.utter_message(text=response)
             
        except Exception as e:
             print(f"[ACTION] {self.name()} | ERROR: {str(e)}")
             dispatcher.utter_message(text="Data not available for this company.")

        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionGetInterviewProcess(Action):
    def name(self) -> Text:
        return "action_get_interview_process"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker) # Fixed: Resolve company first!

        if not company:
            dispatcher.utter_message(text="Which company's interview process? (e.g., 'Amazon interview rounds')")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            
            round_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            rounds = []
            
            for i in range(1, 5): 
                name = row.get(f'round{i}_name', '')
                if pd.isna(name) or not str(name).strip(): continue
                
                duration = row.get(f'round{i}_duration_min', 'N/A')
                focus = row.get(f'round{i}_focus', 'General')
                rounds.append(f"{round_emojis[i-1]} **{name}**\n   ⏱ Duration: {duration} mins\n   🎯 Focus: {focus}")

            print(f"[DEBUG] Action: {self.name()} | Company: {company} | Rounds Found: {len(rounds)}")

            if rounds:
                response = f"⚔️ Interview Process for {company}:\n\n" + "\n\n".join(rounds)
            else:
                response = "Data not available for this company."
        
        except IndexError:
            response = "Data not available for this company."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]

class ActionPrepTopicsByArea(Action):
    def name(self) -> Text:
        return "action_prep_topics_by_area"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        
        # Check if it's a general HR query without company/area mentioned specifically
        # (Though rules should handle ask_general_hr_question, this is safety)
        if intent == 'ask_general_hr_question':
            return []

        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's specific topics? (e.g., 'Google dbms topics')")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
            
        prep_area = next((e['value'] for e in tracker.latest_message.get('entities', []) if e['entity'] == 'prep_area'), None)
        
        # STRICT MANDATORY MAPPING
        AREA_TO_COLUMN = {
            'dsa': 'prep_dsa_topics',
            'dbms': 'prep_dbms_topics',
            'oops': 'prep_oops_topics',
            'system_design': 'prep_system_design_topics',
            'hr': 'prep_hr_topics'
        }
        
        target_col = AREA_TO_COLUMN.get(prep_area.lower()) if prep_area else None
            
        if not target_col:
             dispatcher.utter_message(text=f"Please specify a valid topic area (DSA, DBMS, OOPS, System Design, HR) for {company}.")
             return [SlotSet("company", None), SlotSet("last_company_asked", None)]

        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            
            # DIAGNOSTIC LOGGING
            log_debug(f"[DIAGNOSTIC] Company: {company} | Target Column: {target_col}")
            log_debug(f"[DIAGNOSTIC] Columns in DF: {df.columns.tolist()}")
            
            topic_content = row.get(target_col, '')
            log_debug(f"[DEBUG] Action: {self.name()} | Content: {topic_content}")

            if pd.isna(topic_content) or str(topic_content).upper() == 'NA' or not str(topic_content).strip():
                 response = "Data not available for this company."
            else:
                 formatted_area = prep_area.replace('_', ' ').upper()
                 response = f"{formatted_area} Topics for {company}:\n- {topic_content}"
                 
            dispatcher.utter_message(text=response)
            
        except IndexError:
             dispatcher.utter_message(text=f"Company {company} not found.")
             
        # STRICT SLOT RESET POLICY: Reset prep_area to prevent loop
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None), SlotSet("prep_area", None)]

class ActionGetPreparationRoadmap(Action):
    def name(self) -> Text:
        return "action_get_preparation_roadmap"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Hard Fix for Loop: If user explicitly says "full", ignore prep_area slot artifact
        raw_text = tracker.latest_message.get('text', '').lower()
        explicit_full = any(w in raw_text for w in ["full", "complete", "entire", "whole", "all"])

        # HARD BLOCK as per TC-22 Requirement (Only if NOT explicitly asking for full)
        if tracker.get_slot("prep_area") and not explicit_full:
            dispatcher.utter_message(
                text="Please specify if you want the full study roadmap or only a specific topic."
            )
            return []

        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[ACTION] {self.name()} | Intent: {intent}")
        
        company, source = resolve_company(tracker) # FIXED: Resolve company first

        if not company:
            dispatcher.utter_message(text="Which company's preparation roadmap? (e.g., 'Google preparation topics')")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        df = DataStore.get_df()
        try:
            row_index = df[df['company_name'] == company].index[0]
            row = df.iloc[row_index]
            
            prep_sections = []
            
            # 1. Technical Areas (Dynamic Mapping)
            AREA_TO_LABEL = {
                'prep_dsa_topics': 'DSA',
                'prep_system_design_topics': 'System Design',
                'prep_oops_topics': 'OOPS',
                'prep_dbms_topics': 'DBMS',
                'prep_hr_topics': 'HR'
            }
            
            for col, label in AREA_TO_LABEL.items():
                val = row.get(col, '')
                if pd.notna(val) and str(val).strip() and str(val).upper() != 'NA':
                    prep_sections.append(f"🔹 {label}:\n- {val}")
            
            print(f"[DEBUG] Action: {self.name()} | Company: {company} | Prep Sections: {len(prep_sections)}")

            if prep_sections:
                response = f"📘 Full Preparation Roadmap for {company}:\n\n" + "\n\n".join(prep_sections)
            else:
                # Fallback: detailed topic columns not in CSV, use human-like preparation template
                response = tpl_preparation(row)
        
        except IndexError:
            response = "Data not available for this company."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


# -------------------- NEW HUMAN-LIKE LAYER 1 ACTIONS --------------------

class ActionGetCompanyOverview(Action):
    def name(self) -> Text:
        return "action_get_company_overview"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's overview would you like?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_company_overview(row)
        except IndexError:
            response = f"Overview not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionGetCompanyDifficulty(Action):
    def name(self) -> Text:
        return "action_get_company_difficulty"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's difficulty level?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_difficulty(row)
        except IndexError:
            response = f"Difficulty data not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionGetHiringPattern(Action):
    def name(self) -> Text:
        return "action_get_hiring_pattern"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's hiring pattern?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_hiring_pattern(row)
        except IndexError:
            response = f"Hiring pattern data not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionGetJobRoles(Action):
    def name(self) -> Text:
        return "action_get_job_roles"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's job roles?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_job_roles(row)
        except IndexError:
            response = f"Job role data not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionGetCompanyCategory(Action):
    def name(self) -> Text:
        return "action_get_company_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's category?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_category(row)
        except IndexError:
            response = f"Category data not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionGetCompanyTierInfo(Action):
    def name(self) -> Text:
        return "action_get_company_tier_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's tier information?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_tier(row)
        except IndexError:
            response = f"Tier info not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionGetCompanyPreparation(Action):
    def name(self) -> Text:
        return "action_get_company_preparation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company, source = resolve_company(tracker)
        if not company:
            dispatcher.utter_message(text="Which company's preparation guide?")
            return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        df = DataStore.get_df()
        try:
            row = df[df['company_name'] == company].iloc[0]
            response = tpl_preparation(row)
        except IndexError:
            response = f"Preparation guide not available for {company}."
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", company if source in ['entity', 'fuzzy', 'alias'] else None)]


class ActionCompareCompanies(Action):
    def name(self) -> Text:
        return "action_compare_companies"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = [e['value'] for e in tracker.latest_message.get('entities', []) if e['entity'] == 'company']
        df = DataStore.get_df()

        if len(entities) < 2:
            dispatcher.utter_message(text="Please name two companies to compare. (e.g., 'Compare Google and Infosys')")
            return [SlotSet("company", None)]

        try:
            from fuzzywuzzy import process as fwp
            company_list = df['company_name'].tolist()
            name1 = fwp.extractOne(entities[0], company_list)[0]
            name2 = fwp.extractOne(entities[1], company_list)[0]
            row1 = df[df['company_name'] == name1].iloc[0]
            row2 = df[df['company_name'] == name2].iloc[0]
            response = tpl_comparison(row1, row2)
        except Exception as e:
            print(f"[ERROR] ActionCompareCompanies: {e}")
            response = "Could not compare those companies. Please check the company names and try again."

        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", None)]


# ==================== LAYER 2: AGGREGATE ACTIONS ====================

class ActionListCompaniesByCGPA(Action):
    def name(self) -> Text:
        return "action_list_companies_by_cgpa"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()
        
        import re
        cgpa_match = re.search(r'(\d+\.?\d*)', user_text)
        cgpa_threshold = float(cgpa_match.group(1)) if cgpa_match else 7.0
        
        if 'lowest' in user_text or 'low cgpa' in user_text or 'easy cgpa' in user_text or 'minimum requirement' in user_text:
            sorted_df = df.sort_values('min_cgpa', ascending=True)
            companies_data = sorted_df[['company_name', 'min_cgpa']].values.tolist()
            companies = [c[0] for c in companies_data]
            response = "Companies with lowest CGPA requirements:\n" + "\n".join([f"- {c[0]}: {c[1]} CGPA" for c in companies_data[:15]])
        elif 'above' in user_text or 'more than' in user_text or 'greater' in user_text:
            filtered = df[df['min_cgpa'] <= cgpa_threshold]
            companies = filtered['company_name'].tolist()
            response = f"Companies accepting CGPA {cgpa_threshold} or above:\n" + "\n".join([f"- {c}" for c in companies[:15]])
        elif 'below' in user_text or 'less than' in user_text:
            filtered = df[df['min_cgpa'] >= cgpa_threshold]
            companies = filtered['company_name'].tolist()
            response = f"Companies requiring CGPA below {cgpa_threshold}:\n" + "\n".join([f"- {c}" for c in companies[:15]])
        else:
            filtered = df[df['min_cgpa'] <= cgpa_threshold]
            companies = filtered['company_name'].tolist()
            response = f"Companies for CGPA {cgpa_threshold}:\n" + "\n".join([f"- {c}" for c in companies[:15]])
        
        if not companies:
            response = f"No companies found for CGPA {cgpa_threshold}."
        
        dispatcher.utter_message(text=response)
        return []

class ActionListCompaniesAllowingBacklogs(Action):
    def name(self) -> Text:
        return "action_list_companies_allowing_backlogs"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        filtered = df[df['backlogs_allowed'].apply(_backlogs_allowed_count) > 0]
        companies = filtered['company_name'].tolist()
        
        # String-based detection: count vs list
        user_text = tracker.latest_message.get('text', '').lower()
        count_keywords = ['how many', 'count', 'total', 'number of']
        is_count_query = any(keyword in user_text for keyword in count_keywords)
        
        if is_count_query:
            response = f"Total companies allowing backlogs: {len(companies)}"
        else:
            if companies:
                response = f"Companies Allowing Backlogs ({len(companies)} total):\n" + "\n".join([f"- {c}" for c in companies[:20]])
            else:
                response = "No companies found that allow backlogs."
        
        dispatcher.utter_message(text=response)
        return []

class ActionCountCompanies(Action):
    def name(self) -> Text:
        return "action_count_companies"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()
        
        print(f"[DEBUG] Action: {self.name()} | Query: {user_text}")

        if 'backlog' in user_text:
            count = len(df[df['backlogs_allowed'].apply(_backlogs_allowed_count) > 0])
            response = f"Total companies allowing backlogs: {count}"
        elif 'tier-1' in user_text or 'tier 1' in user_text:
            count = len(df[df['company_tier'].str.contains('Tier-1', case=False, na=False)])
            response = f"There are {count} Tier-1 companies in our database."
        elif 'cgpa' in user_text:
            import re
            cgpa_match = re.search(r'(\d+\.?\d*)', user_text)
            cgpa = float(cgpa_match.group(1)) if cgpa_match else 7.0
            count = len(df[df['min_cgpa'] <= cgpa])
            response = f"There are {count} companies accepting CGPA {cgpa} or above."
        else:
            response = f"Currently, we have information for {len(df)} companies."
        
        dispatcher.utter_message(text=response)
        return [SlotSet("company", None), SlotSet("last_company_asked", None)]

class ActionListTier1Companies(Action):
    def name(self) -> Text:
        return "action_list_tier1_companies"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()

        # Handle "all companies" / "campus visit" queries before tier filtering
        if any(k in user_text for k in ['visit', 'campus', 'all companies', 'every company', 'which companies']):
            all_companies = df['company_name'].tolist()
            response = (f"There are {len(all_companies)} companies visiting our campus:\n" +
                        "\n".join([f"- {c}" for c in all_companies]))
            dispatcher.utter_message(text=response)
            return []

        # Extract tier number (1, 2, or 3)
        tier = None
        if 'tier 1' in user_text or 'tier-1' in user_text or 'tier1' in user_text:
            tier = 'Tier-1'
        elif 'tier 2' in user_text or 'tier-2' in user_text or 'tier2' in user_text:
            tier = 'Tier-2'
        elif 'tier 3' in user_text or 'tier-3' in user_text or 'tier3' in user_text:
            tier = 'Tier-3'
        else:
            # Default to Tier-1 if no tier specified
            tier = 'Tier-1'
        
        # Filter by tier
        filtered = df[df['company_tier'].str.contains(tier, case=False, na=False)]
        companies = filtered['company_name'].tolist()
        
        # String-based detection: count vs list
        count_keywords = ['how many', 'count', 'total', 'number of']
        is_count_query = any(keyword in user_text for keyword in count_keywords)
        
        if is_count_query:
            # Return count only
            response = f"Total {tier} companies: {len(companies)}"
        else:
            # Return list
            if companies:
                response = f"{tier} Companies ({len(companies)} total):\n" + "\n".join([f"- {c}" for c in companies])
            else:
                response = f"No {tier} companies found."
        
        dispatcher.utter_message(text=response)
        return []

class ActionListHighPayingCompanies(Action):
    def name(self) -> Text:
        return "action_list_high_paying_companies"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()
        
        import re
        package_match = re.search(r'(\d+)', user_text)
        threshold = float(package_match.group(1)) if package_match else 10.0
        
        filtered = df[df['avg_package_lpa'] >= threshold].sort_values('avg_package_lpa', ascending=False)
        companies = filtered[['company_name', 'avg_package_lpa']].values.tolist()
        
        if companies:
            response = f"Companies offering {threshold}+ LPA ({len(companies)} total):\n" + "\n".join([f"- {c[0]}: {c[1]} LPA" for c in companies[:15]])
        else:
            response = f"No companies found offering {threshold}+ LPA."
        
        dispatcher.utter_message(text=response)
        return []

class ActionListCompaniesByBranch(Action):
    def name(self) -> Text:
        return "action_list_companies_by_branch"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()
        
        branch = None
        if 'cs' in user_text or 'computer science' in user_text:
            branch = 'CS'
        elif 'it' in user_text or 'information technology' in user_text:
            branch = 'IT'
        elif 'ece' in user_text or 'electronics' in user_text:
            branch = 'ECE'
        elif 'ee' in user_text or 'electrical' in user_text:
            branch = 'EE'
        
        if not branch:
            dispatcher.utter_message(text="Which branch? (e.g., 'Companies for CS students')")
            return []
        
        filtered = df[df['allowed_departments'].str.contains(branch, case=False, na=False)]
        companies = filtered['company_name'].tolist()
        
        if companies:
            response = f"Companies for {branch} students ({len(companies)} total):\n" + "\n".join([f"- {c}" for c in companies[:20]])
        else:
            response = f"No companies found for {branch} branch."
        
        dispatcher.utter_message(text=response)
        return []

class ActionListCompaniesByCategory(Action):
    def name(self) -> Text:
        return "action_list_companies_by_category"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()

        if 'easy' in user_text or 'easiest' in user_text or 'accessible' in user_text:
            sorted_df = df.sort_values('difficulty_factor', ascending=True)
            data = sorted_df[['company_name', 'difficulty_factor']].values.tolist()
            response = ("Companies with the easiest hiring processes (sorted by difficulty):\n" +
                        "\n".join([f"- {r[0]} (difficulty: {r[1]}/10)" for r in data[:15]]))
        elif 'product' in user_text:
            filtered = df[df['company_cat'].str.lower().str.contains('product', na=False)]
            companies = filtered['company_name'].tolist()
            response = ((f"Product-based companies ({len(companies)} total):\n" +
                         "\n".join([f"- {c}" for c in companies]))
                        if companies else "No product-based companies found.")
        elif 'service' in user_text:
            filtered = df[df['company_cat'].str.lower().str.contains('service', na=False)]
            companies = filtered['company_name'].tolist()
            response = ((f"Service-based companies ({len(companies)} total):\n" +
                         "\n".join([f"- {c}" for c in companies]))
                        if companies else "No service-based companies found.")
        else:
            companies = df['company_name'].tolist()
            response = (f"All companies in our database ({len(companies)} total):\n" +
                        "\n".join([f"- {c}" for c in companies]))

        dispatcher.utter_message(text=response)
        return []


class ActionCountCompaniesByCriteria(Action):
    def name(self) -> Text:
        return "action_count_companies_by_criteria"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataStore.get_df()
        user_text = tracker.latest_message.get('text', '').lower()
        
        if 'backlog' in user_text:
            count = len(df[df['backlogs_allowed'].apply(_backlogs_allowed_count) > 0])
            response = f"Number of companies allowing backlogs: {count}"
        elif 'tier' in user_text and '1' in user_text:
            count = len(df[df['company_tier'].str.contains('Tier-1', case=False, na=False)])
            response = f"Number of Tier-1 companies: {count}"
        elif 'cgpa' in user_text:
            import re
            cgpa_match = re.search(r'(\d+\.?\d*)', user_text)
            cgpa = float(cgpa_match.group(1)) if cgpa_match else 7.0
            count = len(df[df['min_cgpa'] <= cgpa])
            response = f"Number of companies accepting CGPA {cgpa}+: {count}"
        else:
            response = f"Total companies in database: {len(df)}"
        
        dispatcher.utter_message(text=response)
        return []

class ActionProvideCompanyOptions(Action):
    def name(self) -> Text:
        return "action_provide_company_options"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Resolve company (expecting entity or fuzzy)
        company, source = resolve_company(tracker)
        
        if not company:
             dispatcher.utter_message(text="Which company are you interested in?")
             return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        message = f"What would you like to know about {company}?"
        buttons = [
            {"title": "Package", "payload": "package"},
            {"title": "CGPA", "payload": "cgpa"},
            {"title": "Backlog Policy", "payload": "backlog policy"},
            {"title": "Roles", "payload": "roles"},
            {"title": "Interview Process", "payload": "interview process"},
            {"title": "Preparation", "payload": "preparation topics"},
        ]
        dispatcher.utter_message(text=message, buttons=buttons)
        
        # CR-04: Set 'company' (Active), Clear 'last_company_asked' (Context)
        return [SlotSet("company", company), SlotSet("last_company_asked", None)]

# ==================== UTILITY ====================

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')
        print(f"[DEBUG] Action: {self.name()} | Intent: {intent}")
        
        # Priority 1: Check if company-specific intent but company missing
        # We explicitly avoid mentioning any company here
        company_intents = [
            'ask_avg_package', 'ask_max_package', 'ask_min_cgpa',
            'ask_allowed_departments', 'ask_required_skills',
            'ask_backlog_allowed', 'ask_max_backlogs',
            'ask_company_tier', 'ask_hiring_roles',
            'ask_eligibility_summary', 'ask_interview_process',
            'ask_preparation_roadmap', 'ask_prep_topics_by_area'
        ]
        
        if intent in company_intents:
             dispatcher.utter_message(text="Which company are you asking about? Please specify the company name (e.g., 'Google' or 'TCS').")
             return [SlotSet("company", None), SlotSet("last_company_asked", None)]
        
        # Priority 2: Generic fallback
        dispatcher.utter_message(
            text="I'm sorry, I didn't quite catch that. You can ask me about:\n- Company details (e.g., 'Google package')\n- Eligibility (e.g., 'Check my eligibility for Microsoft')\n- Aggregate queries (e.g., 'Total Tier-1 companies')\n- Preparation (e.g., 'DBMS topics for Amazon')"
        )
        
        return [SlotSet("company", None), SlotSet("last_company_asked", None)]
