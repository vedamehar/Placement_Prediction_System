# 🎓 Placement Prediction System

An intelligent AI-powered system that predicts student placement outcomes with company-specific accuracy, salary tiers, and personalized career recommendations using machine learning and advanced analytics.

## ✨ Features

- **Placement Prediction**: Predicts whether a student will be placed or not
- **Salary Tier Prediction**: Estimates salary ranges (Entry-level, Mid-level, Senior)
- **Job Role Recommendation**: Suggests suitable job roles based on student profile
- **Company Matching**: Recommends companies based on student skills and preferences
- **Service/Product Probability**: Calculates likelihood of placement in service vs. product companies
- **Multi-Source Evaluation**:
  - LeetCode DSA problem-solving assessment
  - GitHub project complexity analysis
  - Aptitude & ATS-compliant resume scoring
  - HR round interview evaluation
- **Interactive Chatbot**: Rasa-powered conversational interface
- **REST API & React UI**: Modern web interface with real-time predictions

## 📋 Project Structure

```
Placement_Prediction_System/
├── data/                              # Data files
│   ├── student_profiles_100.csv       # Student academic profiles
│   ├── company_profiles_with_difficulty.csv  # Company database
│   ├── campus_placement_dataset_final_academic_4000.csv  # Training data
│   └── Predicted_Data.csv             # Output predictions
│
├── modules/                           # Core Python modules
│   ├── leetcode_dsa.py               # LeetCode DSA evaluation
│   ├── github_project.py             # GitHub project analysis
│   ├── aptitude_ats.py               # Aptitude & resume scoring
│   ├── hr_round.py                   # HR interview evaluation
│   ├── feature_engineering.py        # Data preprocessing
│   ├── ml_models.py                  # ML model management
│   ├── service_product_probability.py # Service/Product classification
│   └── salary_probability.py         # Salary prediction
│
├── Chatbot/                           # Rasa chatbot
│   ├── actions/                      # Custom actions
│   ├── data/                         # NLU training data
│   ├── config.yml                    # Rasa configuration
│   ├── domain.yml                    # Chatbot domain
│   └── requirements.txt              # Chatbot dependencies
│
├── UI Eduplus/                        # React frontend
│   ├── src/
│   │   ├── app/components/          # React components
│   │   ├── styles/                  # CSS styles
│   │   └── main.tsx                 # Entry point
│   ├── package.json                 # NPM dependencies
│   └── vite.config.ts               # Vite configuration
│
├── app.py                             # Flask API server
├── main.py                            # CLI prediction interface
├── train_models.py                    # Model training script
├── train_salary_model.py              # Salary model training
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for React UI)
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vedamehar/Placement_Prediction_System.git
   cd Placement_Prediction_System
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train ML models (First time only)**
   ```bash
   python train_models.py
   python train_salary_model.py
   ```

## 💻 Usage

### 1. CLI Prediction
```bash
python main.py
```
Provides a command-line interface to:
- Input student profiles
- Get placement predictions
- View salary tier estimates
- See company recommendations

### 2. REST API & Web Interface
```bash
python app.py
```
Starts Flask API server at `http://localhost:5000`

Then run the React frontend:
```bash
cd "UI Eduplus"
npm install
npm run dev
```
Access the web UI at the provided local URL

### 3. Chatbot Interface
```bash
cd Chatbot
bash run.sh  # On Windows: run.bat
```
Launches Rasa chatbot for conversational interactions

## 📊 System Components

### Data Input
The system evaluates students across multiple dimensions:

| Component | Evaluation Method | Source |
|-----------|------------------|--------|
| **DSA Skills** | LeetCode problem solving stats | LeetCode API |
| **Projects** | GitHub repository analysis | GitHub API |
| **Academic** | CGPA, semester scores, attendance | Student CSV |
| **Aptitude** | Quantitative & reasoning tests | Apts test scores |
| **Resume** | ATS keyword compliance | Resume text |
| **HR Round** | Interview communication score | HR evaluation |

### ML Models
- **Placement Model**: XGBoost classifier for placement prediction
- **Salary Model**: Regression model for salary range prediction
- **Role Model**: Multi-class classifier for job role prediction
- **Company Recommender**: KNN-based company matching

### Output
```json
{
  "student_id": "STU001",
  "placement_probability": 0.87,
  "salary_tier": "Mid-level",
  "salary_range": "4.5-6.5 LPA",
  "recommended_roles": ["Software Engineer", "Data Analyst"],
  "recommended_companies": ["Company A", "Company B", "Company C"],
  "service_company_probability": 0.45,
  "product_company_probability": 0.55
}
```

## ⚙️ Configuration

### Key Files
- **Chatbot config**: `Chatbot/config.yml`
- **Chatbot domain**: `Chatbot/domain.yml`
- **Model paths**: Configured in `modules/ml_models.py`
- **API endpoints**: Defined in `app.py`

### Environment Variables
```bash
# Optional: Configure these in .env file
FLASK_ENV=development
FLASK_DEBUG=True
CORS_ORIGINS=*
RASA_SERVER_URL=http://localhost:5005
```

## 🧪 Testing & Validation

```bash
# Validate system setup
python validate_system.py

# Update company profiles
python update_profiles.py

# Generate predictions for batch
python main.py
```

## 📦 Dependencies

### Python Packages
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning
- `xgboost` - Gradient boosting
- `requests` - HTTP requests (for APIs)
- `flask` - API server
- `flask-cors` - CORS support
- `joblib` - Model serialization

### Frontend
- `React` - UI framework
- `TypeScript` - Type safety
- `Tailwind CSS` - Styling
- `Vite` - Build tool

### Chatbot
- `Rasa` - NLU & dialogue management
- See `Chatbot/requirements.txt`

## 🔄 Workflow

```
1. Student provides profile data
   ↓
2. System evaluates across all dimensions
   ↓
3. Features are engineered & normalized
   ↓
4. ML models generate predictions
   ↓
5. Results are aggregated & ranked
   ↓
6. Recommendations displayed with confidence scores
```

## 📈 Performance

- **Placement Prediction Accuracy**: ~87%
- **Salary Tier Prediction Accuracy**: ~82%
- **Job Role Prediction Accuracy**: ~79%
- **Average Response Time**: <500ms per prediction

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👤 Author

**Vedam Eswar**
- GitHub: [@vedamehar](https://github.com/vedamehar)
- Email: vedamehar@gmail.com

## 🐛 Issues & Support

Found a bug or have suggestions? [Create an issue](https://github.com/vedamehar/Placement_Prediction_System/issues)

## 🎯 Roadmap

- [ ] Mobile app for placement tracking
- [ ] Real-time LeetCode API integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language chatbot support
- [ ] Predictive analysis for hiring trends
- [ ] Interview preparation module

---

**⭐ If you found this helpful, please star the repository!**

For questions or collaboration, feel free to reach out to vedamehar@gmail.com
