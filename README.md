# Student Placement Prediction using Microsoft Azure Machine Learning
### Academic Internship Project & Microsoft Azure AI-900 (Azure AI Fundamentals) Comprehensive Deliverable

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-v1.9.1-orange.svg)](https://scikit-learn.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-green.svg)](https://fastapi.tiangolo.com/)
[![Azure App Service](https://img.shields.io/badge/Hosted%20on-Azure%20App%20Service-0078D4.svg)](https://azure.microsoft.com/services/app-service/)
[![Azure AI-900](https://img.shields.io/badge/Certification-Azure%20AI--900-blueviolet.svg)](https://learn.microsoft.com/certifications/exams/ai-900/)

---

## 📌 Project Overview
This repository contains the complete, production-grade implementation of **"Student Placement Prediction using Microsoft Azure Machine Learning"**. The system solves a binary classification problem: predicting whether an undergraduate engineering student will secure campus placement (**Placed: Yes / No**) based on 7 academic and skill-oriented features:
1. **CGPA** (Cumulative Grade Point Average: 5.0 to 10.0)
2. **Internships** (Count of internships: 0 to 4)
3. **Projects** (Academic / open-source projects: 0 to 6)
4. **Communication Skills** (Soft skills rating: 1 to 10)
5. **Aptitude Score** (Assessment test score: 30 to 100)
6. **Backlogs** (Active or historic course backlogs: 0 to 5)
7. **Certifications** (Industry professional certifications: 0 to 6)

The project includes:
- **Synthetic Data Engine** with realistic correlations and ~3% missing values.
- **Scikit-Learn Preprocessing Pipeline** (median imputation, standard scaling, classification) preventing data leakage.
- **Comparative Modeling**: Logistic Regression, Decision Tree, and Random Forest evaluated across Accuracy, Precision, Recall, F1, ROC-AUC, and 5-fold cross-validation.
- **FastAPI REST API** with Pydantic validation, CORS middleware, and automatic Swagger docs at `/docs`.
- **Azure App Service Configuration** using Gunicorn with Uvicorn workers for production cloud hosting.
- **Azure Machine Learning Studio Integration**: Complete click-by-click instructions for Azure ML Designer, AutoML, and SDK v2 managed online endpoints.
- **Streamlit Interactive Frontend** for live simulations.
- **Full Academic Project Report** (both `.md` and `.docx` format) and a 45+ Question Viva Voce guide for exam preparation.

---

## 🏆 Model Performance Summary (Real Evaluated Metrics)

Evaluated on held-out test data (30% test split, 300 samples) and 5-fold stratified cross-validation:

| Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV F1 (Mean ± Std) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **87.67%** | **90.86%** | **89.42%** | **0.9013** | **0.9573** | **0.9200 ± 0.0174** | **Selected Best** |
| **Random Forest** | 86.33% | 87.37% | 91.53% | 0.8941 | 0.9229 | 0.8792 ± 0.0162 | Candidate 2 |
| **Decision Tree** | 82.00% | 84.97% | 86.77% | 0.8586 | 0.8674 | 0.8653 ± 0.0184 | Candidate 3 |

*Serialized Artifacts:* `models/model.pkl`, `backend/model.pkl`, and `models/metrics.json`.

---

## 📂 Project Repository Structure

```
placement-project/
├── data/
│   ├── generate_dataset.py       # Synthetic data generator (1,000 samples, ~3% NaNs)
│   └── placement_data.csv        # Generated dataset (63.1% Yes, 36.9% No)
├── notebooks/
│   └── train_model.ipynb         # Step-by-step Jupyter Notebook for EDA & training
├── src/
│   └── train_model.py            # Reproducible model training & chart export script
├── screenshots/                  # High-resolution evaluation charts for thesis & viva
│   ├── class_balance.png
│   ├── correlation_heatmap.png
│   ├── distributions.png
│   ├── model_comparison.png
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   └── feature_importance.png
├── models/
│   ├── model.pkl                 # Serialized best pipeline (Scikit-Learn 1.9.1)
│   └── metrics.json              # Complete performance metrics JSON
├── backend/
│   ├── main.py                   # FastAPI REST API with Pydantic validation
│   ├── model.pkl                 # Self-contained model copy for Azure deployment
│   ├── requirements.txt          # Pinned backend dependencies
│   └── startup.sh                # Azure App Service Linux startup script
├── frontend/
│   ├── app.py                    # Interactive Streamlit dashboard
│   ├── metrics.json              # Model metrics for sidebar display
│   └── requirements.txt          # Frontend dependencies
├── azure_ml/
│   ├── azure_ml_sdk_v2.py        # Azure ML SDK v2 workflow (Assets, Models, Endpoints)
│   ├── score.py                  # Entry script for Azure ML Managed Online Endpoints
│   └── test_endpoint.py          # REST tester for live Azure ML Endpoints
├── tests/
│   └── test_api.py               # Integration test suite (/health and /predict)
├── docs/
│   ├── AZURE_ML_STUDIO_STEPS.md  # Click-by-click Azure ML Studio guide (ml.azure.com)
│   ├── DEPLOY_AZURE.md           # Copy-paste Azure CLI deployment guide
│   └── VIVA_QA.md                # 45+ Viva questions & concise answers for AI-900
├── report/
│   ├── report.md                 # 20-30 page comprehensive markdown project report
│   ├── report.docx               # Academic Word thesis (Times New Roman, 1.5 spacing)
│   └── generate_docx.py          # Python compiler converting Markdown to Word
├── requirements.txt              # Root consolidated dependencies
└── README.md                     # Master project documentation
```

---

## 🚀 Quickstart: Running Locally (No Azure Account Required)

### 1. Prerequisites & Environment Setup
Clone this repository and create a virtual environment:
```bash
cd placement-project
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 2. (Optional) Regenerate Dataset & Train Model
```bash
# 1. Generate dataset:
python data/generate_dataset.py

# 2. Train and evaluate all models (outputs models/ and screenshots/):
python src/train_model.py
```

### 3. Launch FastAPI Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```
- Open Swagger UI in browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health probe: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Automated API Integration Tests
In a separate terminal:
```bash
python tests/test_api.py --url http://127.0.0.1:8000
```

### 5. Launch Streamlit Frontend Dashboard
```bash
cd frontend
streamlit run app.py
```
- Open UI in browser: [http://localhost:8501](http://localhost:8501)
- Try the **Quick Preset Profiles** in the sidebar ("High Achiever", "At-Risk Candidate") to simulate instant predictions!

---

## ☁️ Deploying to Microsoft Azure App Service

See [`docs/DEPLOY_AZURE.md`](docs/DEPLOY_AZURE.md) for detailed commands. Summary:

```bash
# 1. Log in to Azure CLI
az login

# 2. Create Resource Group
az group create --name rg-placement --location centralindia

# 3. Deploy FastAPI backend from backend/ directory
cd backend
az webapp up --name placement-api-<yourname> --resource-group rg-placement --runtime "PYTHON:3.11" --sku B1

# 4. Configure startup command
az webapp config set --resource-group rg-placement --name placement-api-<yourname> \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"

# 5. Test Live Cloud API
python tests/test_api.py --url https://placement-api-<yourname>.azurewebsites.net
```

---

## 🧠 Azure ML Studio (Designer & AutoML)

For visual drag-and-drop modeling in [ml.azure.com](https://ml.azure.com), follow the detailed step-by-step instructions in:
- [`docs/AZURE_ML_STUDIO_STEPS.md`](docs/AZURE_ML_STUDIO_STEPS.md)

This includes explicit **"SCREENSHOT n: ..."** markers for all 8 visual milestones required in your internship submission.

---

## 🎓 Viva Voce & Exam Preparation

A comprehensive guide with 45+ questions and student-friendly answers covering:
- Supervised vs Unsupervised Learning, Overfitting, Pipelines, Metrics
- Why Logistic Regression outperformed Random Forest in this domain
- Azure ML Workspace, Compute Clusters, Datastores, Designer, AutoML
- Microsoft's 6 Responsible AI Principles (Fairness, Reliability, Privacy, Inclusiveness, Transparency, Accountability)
- Azure AI Services: Computer Vision, Language, Speech, Document Intelligence, Azure OpenAI

See [`docs/VIVA_QA.md`](docs/VIVA_QA.md).

---

## 📝 What to Customize for Your Exam Submission

Before submitting your final report to your university / internship examiner:
1. **Personal Information**: Open `report/report.md` (and regenerate `report.docx` via `python report/generate_docx.py`) to replace:
   - `[Student Name]` with your actual name.
   - `[Roll No]` with your university registration / roll number.
   - `[College Name / University Institute of Technology]` with your institution.
   - `[Guide: Abhishek Tiwari]` (already set as your mentor).
2. **Azure Screenshots**: If you have an active Azure subscription, execute the steps in `docs/AZURE_ML_STUDIO_STEPS.md` and insert your live Azure Portal screenshots into the designated placeholders `[INSERT AZURE SCREENSHOT]` in Word.
