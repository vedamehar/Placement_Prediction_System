# EduPlus PlaceMate AI

**Rasa-based Placement Assistant for VIT Pune**

[![Rasa](https://img.shields.io/badge/Rasa-3.6.13-blue.svg)](https://rasa.com/)
[![Python](https://img.shields.io/badge/Python-3.10-green.svg)](https://www.python.org/)

---

## 📌 Overview

A production-ready chatbot that helps college students navigate placements by providing accurate, CSV-driven information about companies, packages, eligibility criteria, and preparation strategies.

**Key Features:**
- ✅ Zero hallucination (CSV-only responses)
- ✅ 24 intents covering company-specific, aggregate, and policy queries
- ✅ 50 companies with real placement data
- ✅ Fuzzy matching for typo handling
- ✅ Demo-safe and viva-safe

---

## 🛠️ Tech Stack

- **Rasa 3.6.13** - NLU & Dialogue Management
- **Python 3.10** - Custom actions
- **Pandas** - CSV data processing
- **FuzzyWuzzy** - Company name matching

---

## 🚀 Quick Start

### ⚡ Easiest Way (Automated Scripts)

**Windows:**
```cmd
setup.bat    # Run once to install
run.bat      # Run every time to start chatbot
```

**Linux/Mac or Git Bash:**
```bash
chmod +x setup.sh run.sh
./setup.sh   # Run once to install
./run.sh     # Run every time to start chatbot
```

The scripts handle everything automatically! See [QUICKSTART.md](QUICKSTART.md) for details.

---

### 📖 Manual Setup (Alternative)

### Prerequisites
- Python 3.10 (Required - Rasa 3.6 does not support Python 3.11+)
- pip

### Installation

1. **Clone and navigate**
```bash
git clone <repository-url>
cd Rasa_Based_chat_bot_college_placment
```

2. **Create virtual environment**
```bash
python -m venv venv_rasa

# Activate (choose based on your terminal):
venv_rasa\Scripts\activate          # PowerShell/CMD (Windows)
source venv_rasa/Scripts/activate   # Bash/Git Bash (Windows)
# source venv_rasa/bin/activate     # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Train the model**
```bash
rasa train
```

5. **Run the chatbot**

**Option 1: Shell Interface**
```bash
# Terminal 1
rasa run actions

# Terminal 2
rasa shell
```

**Option 2: Web UI**
```bash
# Terminal 1
rasa run actions

# Terminal 2
rasa run --enable-api --cors "*"

# Terminal 3
python -m http.server 8000 --directory ui
# Open http://localhost:8000 in browser
```

---

## 📁 Project Structure

```
Rasa_Based_chat_bot_college_placment/
├── actions/
│   ├── __init__.py
│   └── actions.py              # 18 custom actions
├── data/
│   ├── company_placement_db.csv    # 50 companies dataset
│   ├── nlu.yml                 # 24 intents with examples
│   ├── rules.yml               # Intent-action mappings
│   └── stories.yml             # Conversation flows
├── ui/
│   └── index.html              # Web interface
├── config.yml                  # NLU pipeline configuration
├── domain.yml                  # Intents, entities, slots
├── endpoints.yml               # Action server endpoint
├── credentials.yml             # API credentials
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 💬 Example Queries

**Company-Specific:**
- "What is Google's average package?"
- "Does IBM allow backlogs?"
- "What CGPA does Amazon require?"

**Aggregate:**
- "Which companies allow backlogs?"
- "How many tier 2 companies?"
- "Companies offering above 15 LPA"

**Policy:**
- "What are the placement rules?"
- "How to prepare for placements?"

---

## 🐛 Common Issues

### Issue: "No module named 'rasa'"
**Fix:** Activate virtual environment first
```bash
venv_rasa\Scripts\activate
```

### Issue: "Connection refused to localhost:5005"
**Fix:** Start action server first
```bash
rasa run actions
```

### Issue: Python version incompatibility / venv creation fails
**Problem:** Rasa 3.6 requires Python 3.8-3.10 (does NOT work with 3.11+)

**Fix:** Install Python 3.10 and create venv with it
```bash
# Check your Python version
python --version

# If you have Python 3.11+, download Python 3.10 from python.org
# Then create venv with Python 3.10:
py -3.10 -m venv venv_rasa
venv_rasa\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Unable to create process" or launcher errors
**Fix:** Your Python version is incompatible. Use Python 3.10.

---

## 📞 Contact

**Maintainer:** Piyush Mishra  
**Phone:** 9975765965  
**Institute:** VIT Pune  

---

**Status:** Production Ready ✅  
**Last Updated:** February 2026  
**Total Companies:** 50  
**Total Intents:** 24
