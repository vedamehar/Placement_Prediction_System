# Quick Reference Card - EduPlus PlaceMate AI

## 🚀 Start Here

**Read this first:** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)

---

## ⚡ 3-Step Setup

### Step 1: Install Python 3.10 (5 min)
```
1. Download: https://www.python.org/downloads/release/python-3100/
2. Install (check "Add Python 3.10 to PATH")
3. Verify: python --version
```

### Step 2: Run Setup (15 min)
```bash
setup_improved.bat
```
*Creates venv, installs Rasa, trains model*

### Step 3: Start Chatbot (2 min)
```bash
run_improved.bat
```
*Opens action server + shell*

---

## 💬 Test Commands

```
> hi
> what is google's average package?
> list tier-1 companies
> what should I prepare for amazon?
> goodbye
```

---

## 📊 Project Overview

| Component | Value |
|-----------|-------|
| **Framework** | Rasa 3.6.13 |
| **Python** | 3.10 (required) |
| **Companies** | 50 in database |
| **Intents** | 24 types |
| **Custom Actions** | 40+ |
| **Training Data** | 1,058 lines |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| **config.yml** | NLU configuration |
| **domain.yml** | Intents & responses |
| **data/nlu.yml** | Training examples |
| **data/company_placement_db.csv** | Knowledge base |
| **actions/actions.py** | Custom action handlers |

---

## 🛠️ Commands

### Setup & Validation
```bash
setup_improved.bat           # Setup (one time)
python validate_setup.py     # Verify installation
```

### Development
```bash
rasa train                   # Retrain model
rasa data validate          # Check data
rasa shell                  # Chat interactively
rasa run actions           # Start action server
```

### Manual Setup
```bash
python -m venv venv_rasa
venv_rasa\Scripts\activate.bat
pip install -r requirements.txt
rasa train
rasa run actions    (term 1)
rasa shell          (term 2)
```

---

## ❌ Common Issues

| Issue | Fix |
|-------|-----|
| Python 3.13 error | Install Python 3.10 |
| "No module rasa" | Run setup_improved.bat again |
| Connection refused | Start `rasa run actions` first |
| CSV not found | Ensure data/company_placement_db.csv exists |

→ See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions

---

## ✅ Validation Checklist

Before testing chatbot:
- [ ] Python 3.10 installed
- [ ] `rasa --version` works
- [ ] models/ directory exists
- [ ] `rasa run actions` starts successfully
- [ ] `rasa shell` starts successfully

---

## 📚 Documentation

1. **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** ← Read first
2. **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Detailed setup
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving
4. **[ANALYSIS_SUMMARY.md](ANALYSIS_SUMMARY.md)** - Technical details
5. **[setup_improved.bat](setup_improved.bat)** - Smart setup script
6. **[run_improved.bat](run_improved.bat)** - Smart run script
7. **[validate_setup.py](validate_setup.py)** - Validation tool

---

## 🔍 Project Structure

```
Chatbot/
├── config.yml              ← NLU config
├── domain.yml              ← Intents & responses
├── requirements.txt        ← Dependencies
├── data/
│   ├── nlu.yml            ← Training data (825 lines)
│   ├── stories.yml        ← Dialogue examples
│   ├── rules.yml          ← Fixed rules
│   └── company_placement_db.csv  ← Companies (50)
├── actions/
│   └── actions.py         ← Action handlers (916 lines)
├── models/                ← Trained model (created by training)
└── venv_rasa/             ← Virtual environment (created by setup)
```

---

## 🎯 Next Steps

1. ✅ **Install Python 3.10**
2. ✅ **Run setup_improved.bat**
3. ✅ **Run run_improved.bat**
4. ✅ **Test: type "hi"**
5. 📖 **Read COMPLETE_SETUP_GUIDE.md** for details
6. 🐛 **See TROUBLESHOOTING.md** if needed

---

## 💡 Tips

- **Slow training?** Close other apps, it needs CPU
- **Want faster training?** Reduce epochs in config.yml
- **Add new company?** Edit data/company_placement_db.csv (no retraining)
- **Add new intent?** Edit data/nlu.yml and retrain

---

## 📞 Quick Links

- **Rasa Documentation:** https://rasa.com/docs/rasa
- **Issue Tracker:** https://github.com/RasaHQ/rasa/issues
- **Training Data Format:** https://rasa.com/docs/rasa/nlu-training-data

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Python 3.10 installation | 10 min |
| setup_improved.bat | 15 min |
| Model training | 2-5 min |
| First test | 2 min |
| **Total** | **~30 min** |

---

## 🔑 Key Points

1. **Python 3.10 is REQUIRED** (not 3.11/3.12/3.13)
2. **setup_improved.bat handles everything** automatically
3. **Two terminals needed** (action server + shell)
4. **CSV is read at runtime** (no retraining for company updates)
5. **Documentation is comprehensive** (check if unsure)

---

## Success Indicators

You're ready when you see:

**Terminal 1 (Action Server):**
```
action server is running on 0.0.0.0:5055
```

**Terminal 2 (Chatbot Shell):**
```
>_
```

Then type:
```
> hi
```

And see:
```
Hi! I'm EduPlus PlaceMate AI...
```

---

## Emergency Reset

If something breaks:
```bash
rmdir /s /q venv_rasa models
setup_improved.bat
```

This completely resets everything (safe to run multiple times).

---

**Version:** Quick Reference v1.0
**Last Updated:** February 25, 2026
**Status:** Production Ready (with Python 3.10)

