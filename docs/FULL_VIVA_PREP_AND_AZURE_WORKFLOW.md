# Master Guide: Viva Voce Preparation, End-to-End Workflow & Azure Deployment
## Project: Student Placement Prediction using Microsoft Azure Machine Learning
### Certification Target: Microsoft Azure AI-900 (Azure AI Fundamentals)

---

## TABLE OF CONTENTS
1. [Executive Summary & Quick Facts](#1-executive-summary--quick-facts)
2. [Complete Project Workflow: What We Built from Scratch](#2-complete-project-workflow-what-we-built-from-scratch)
   - [Phase 1: Dataset Generation & Logic](#phase-1-dataset-generation--logic)
   - [Phase 2: Exploratory Data Analysis & Leakage-Free Preprocessing](#phase-2-exploratory-data-analysis--leakage-free-preprocessing)
   - [Phase 3: Model Building, Evaluation & Selection](#phase-3-model-building-evaluation--selection)
   - [Phase 4: Serialization & Packaging](#phase-4-serialization--packaging)
   - [Phase 5: FastAPI Backend Development](#phase-5-fastapi-backend-development)
   - [Phase 6: Streamlit Frontend Interface](#phase-6-streamlit-frontend-interface)
   - [Phase 7: Automated Integration Testing](#phase-7-automated-integration-testing)
3. [All Steps to Deploy & Upload to Microsoft Azure](#3-all-steps-to-deploy--upload-to-microsoft-azure)
   - [Option A: Azure App Service (Production REST API)](#option-a-azure-app-service-production-rest-api)
   - [Option B: Azure ML Studio (Visual Designer & AutoML)](#option-b-azure-ml-studio-visual-designer--automl)
   - [Option C: Azure ML SDK v2 (Managed Online Endpoints)](#option-c-azure-ml-sdk-v2-managed-online-endpoints)
   - [Resource Teardown & Cost Management](#resource-teardown--cost-management)
4. [Master Viva Voce Catalog (50+ High-Yield Questions & Answers)](#4-master-viva-voce-catalog-50-high-yield-questions--answers)
   - [Domain 1: Core Machine Learning Fundamentals (Q1–Q12)](#domain-1-core-machine-learning-fundamentals-q1q12)
   - [Domain 2: Project Architecture & Model Insights (Q13–Q22)](#domain-2-project-architecture--model-insights-q13q22)
   - [Domain 3: Azure Machine Learning Studio & MLOps (Q23–Q32)](#domain-3-azure-machine-learning-studio--mlops-q23q32)
   - [Domain 4: Azure App Service & REST API Architecture (Q33–Q38)](#domain-4-azure-app-service--rest-api-architecture-q33q38)
   - [Domain 5: Microsoft Responsible AI Principles (Q39–Q44)](#domain-5-microsoft-responsible-ai-principles-q39q44)
   - [Domain 6: Azure AI Services Suite (AI-900 Breadth) (Q45–Q50)](#domain-6-azure-ai-services-suite-ai-900-breadth-q45q50)
5. [The 2-Minute Viva Elevator Pitch](#5-the-2-minute-viva-elevator-pitch)

---

## 1. EXECUTIVE SUMMARY & QUICK FACTS

| Parameter | Project Specification |
| :--- | :--- |
| **Project Title** | Student Placement Prediction using Microsoft Azure Machine Learning |
| **Problem Formulation** | Supervised Binary Classification (`placed`: "Yes" / "No") |
| **Curriculum Alignment** | Microsoft Certified: Azure AI Fundamentals (Exam AI-900) |
| **Target Audience** | Academic Institutions, Students, Training & Placement Cells (TPCs) |
| **Dataset Size & Features**| 1,000 Records, 7 Features (`cgpa`, `internships`, `projects`, `communication_skills`, `aptitude_score`, `backlogs`, `certifications`) |
| **Dataset Balance** | 63.1% Placed ("Yes") / 36.9% Not Placed ("No") |
| **Missing Values** | ~3% synthetic missing values injected across `cgpa`, `aptitude_score`, `communication_skills` |
| **Candidate Models** | Logistic Regression, Decision Tree Classifier, Random Forest Classifier |
| **Top Model Selected** | **Logistic Regression** (Accuracy: **87.67%**, Precision: **90.86%**, Recall: **89.42%**, F1-Score: **0.9013**, ROC-AUC: **0.9573**) |
| **5-Fold Cross-Validation**| F1 Mean: **0.9200 ± 0.0174** |
| **Backend Framework** | FastAPI (Async ASGI) with Pydantic validation and Gunicorn/Uvicorn runtime |
| **Cloud Hosting Target** | Microsoft Azure App Service (Linux B1 Plan) & Azure ML Studio |
| **Frontend Dashboard** | Streamlit with real-time health checks, scenario presets, and animated SVG probability gauge |
| **Active Live Backend URL**| `https://placement-api-student101.azurewebsites.net` |

---

## 2. COMPLETE PROJECT WORKFLOW: WHAT WE BUILT FROM SCRATCH

### Phase 1: Dataset Generation & Logic
**File**: `data/generate_dataset.py` $\rightarrow$ `data/placement_data.csv`
1. **Mathematical Formulation**: We designed a domain-driven synthetic generator using a reproducible random seed (`seed=42`).
2. **Log-Odds Equation**:
   $$z = -16.0 + 1.25(\text{CGPA}) + 0.80(\text{Internships}) + 0.50(\text{Projects}) + 0.40(\text{Comm}) + 0.05(\text{Aptitude}) - 1.40(\text{Backlogs}) + 0.35(\text{Certs}) + \epsilon$$
   where $\epsilon \sim \mathcal{N}(0, 1.0)$ simulates real-world interview variance.
3. **Probability Mapping**: Probabilities are mapped via the Sigmoid function $P = \frac{1}{1 + e^{-z}}$. Values with $P \ge 0.50$ are labeled "Yes", else "No".
4. **Data Imperfection**: Injected ~3% `NaN` values across key columns to demonstrate real-world data cleaning capabilities.

---

### Phase 2: Exploratory Data Analysis & Leakage-Free Preprocessing
**Files**: `src/train_model.py` and `notebooks/train_model.ipynb`
1. **Exploratory Data Analysis (EDA)**:
   - Generated and exported 7 visual charts to `screenshots/` (300 DPI):
     - `class_balance.png`: 63.1% Yes vs. 36.9% No distribution.
     - `correlation_heatmap.png`: Pearson matrix showing CGPA ($+0.55$) and Backlogs ($-0.48$) as primary drivers.
     - `distributions.png`: Boxplots proving placed students have higher CGPA ($> 7.8$) and zero backlogs.
2. **Scikit-Learn Pipeline Encapsulation**:
   - Implemented `Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler()), ('classifier', model)])`.
   - **Why Pipeline?** Applying imputer and scaler *inside* the pipeline prevents **Data Leakage** by fitting exclusively on the training folds and applying identical transformations to test/production data.
3. **Stratified Split**: 70% Training (700 rows) / 30% Testing (300 rows) with target stratification to preserve class ratios.

---

### Phase 3: Model Building, Evaluation & Selection
**Files**: `src/train_model.py` $\rightarrow$ `models/metrics.json`
1. **Candidate Algorithms**:
   - **Logistic Regression**: Linear parametric baseline (`max_iter=500`).
   - **Decision Tree**: Non-parametric tree (`max_depth=5`, `min_samples_leaf=10`).
   - **Random Forest**: Ensemble bagging method (`n_estimators=100`, `max_depth=6`).
2. **Comprehensive Evaluation (Held-out 300 test samples)**:
   - **Logistic Regression (Best)**: Accuracy **87.67%**, Precision **90.86%**, Recall **89.42%**, F1 **0.9013**, ROC-AUC **0.9573**, 5-Fold CV F1 **0.9200**.
   - **Random Forest**: Accuracy 86.33%, Precision 87.37%, Recall 91.53%, F1 0.8941, ROC-AUC 0.9229.
   - **Decision Tree**: Accuracy 82.00%, Precision 84.97%, Recall 86.77%, F1 0.8586, ROC-AUC 0.8674.
3. **Why Logistic Regression Won**:
   The underlying true placement probability follows a smooth, monotonic sigmoid relationship. Logistic Regression models continuous probabilities directly, whereas decision trees create orthogonal step-wise splits that suffer from quantization error on small-to-medium sample sizes (1,000 rows).

---

### Phase 4: Serialization & Packaging
**Artifacts**: `models/model.pkl`, `backend/model.pkl`, `models/metrics.json`
1. Serialized the best trained pipeline (including median imputer, standard scaler, and logistic regression weights) using `joblib.dump()`.
2. Created an identical standalone copy inside `backend/model.pkl` so that the cloud backend container is 100% self-contained.
3. Exported all performance metrics, confusion matrices, and Scikit-Learn versions (`1.9.1`) to `models/metrics.json`.

---

### Phase 5: FastAPI Backend Development
**Files**: `backend/main.py`, `backend/requirements.txt`, `backend/startup.sh`
1. **FastAPI Architecture**:
   - Async lifespan loading (`@asynccontextmanager`): Loads `model.pkl` into memory **once** on application boot, ensuring sub-50ms inference latency without disk reads.
   - Automatic OpenAPI / Swagger UI at `/docs`.
   - Built-in CORS middleware to allow cross-origin requests from web frontends.
2. **Endpoints Provided**:
   - `GET /`: Service information and documentation routes.
   - `GET /health`: Lightweight probe returning `{"status": "ok"}` for Azure monitoring.
   - `POST /predict`: Primary inference route taking validated student attributes and returning:
     ```json
     {
       "placed": "Yes",
       "probability": 1.0,
       "confidence_percentage": 100.0,
       "message": "Outstanding profile! Very high probability of securing top-tier campus placement."
     }
     ```
3. **Pydantic Validation (`StudentFeatures`)**:
   - `cgpa`: Float, $5.0 \le \text{cgpa} \le 10.0$
   - `internships`: Int, $0 \le \text{internships} \le 20$
   - `projects`: Int, $0 \le \text{projects} \le 50$
   - `communication_skills`: Float, $1.0 \le \text{comm} \le 10.0$
   - `aptitude_score`: Float, $0.0 \le \text{aptitude} \le 100.0$
   - `backlogs`: Int, $0 \le \text{backlogs} \le 20$
   - `certifications`: Int, $0 \le \text{certifications} \le 30$
4. **Linux Startup Script (`backend/startup.sh`)**:
   ```bash
   gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

---

### Phase 6: Streamlit Frontend Interface
**Files**: `frontend/app.py`, `.streamlit/config.toml`
1. **Design System**: Built on a modern palette inspired by Linear, Stripe, and Vercel:
   - Off-white canvas (`#FAFAF9`), White cards (`#FFFFFF`), Border (`#E7E5E4`), Deep Teal accent (`#0F766E`), Warm Amber alert (`#B45309`).
2. **Crash-Proof URL Resolution**:
   - Graceful 3-tier fallback hierarchy: Streamlit secrets $\rightarrow$ `API_URL` environment variable $\rightarrow$ Azure Default (`https://placement-api-student101.azurewebsites.net`).
   - Prevents `StreamlitSecretNotFoundError` when `.streamlit/secrets.toml` is absent.
3. **Features**:
   - Real-time backend status badge in sidebar with manual "Refresh" button.
   - Interactive profile simulation presets: `Custom`, `High Achiever`, `Moderate Candidate`, `At-Risk Candidate`.
   - Circular SVG probability gauge with percentage in center.
   - Influence bars showing breakdown of CGPA, Aptitude, and Communication.

---

### Phase 7: Automated Integration Testing
**File**: `tests/test_api.py`
Automated test suite verifying endpoints across 3 scenarios:
1. **High Achiever Profile**: Expected `placed == "Yes"` (Passes with $P \approx 1.0$).
2. **At-Risk Profile**: Expected `placed == "No"` (Passes with $P \approx 0.0$).
3. **Borderline Profile**: Verifies numerical probability stability ($P \approx 0.225$).

---

## 3. ALL STEPS TO DEPLOY & UPLOAD TO MICROSOFT AZURE

### Option A: Azure App Service (Production REST API)
This is the primary production deployment method used for hosting the FastAPI backend.

#### Step 1: Azure CLI Authentication
Open PowerShell or Bash and authenticate:
```bash
az login
```
*(A browser window will open. Select your Microsoft Azure account).*

#### Step 2: Set Target Subscription
```bash
az account list --output table
az account set --subscription "<YOUR_SUBSCRIPTION_ID_OR_NAME>"
```

#### Step 3: Create Resource Group
Create a central resource group in your preferred Azure region:
```bash
az group create --name rg-placement --location centralindia
```

#### Step 4: Deploy the FastAPI Backend
Navigate directly into the `backend/` directory where `main.py`, `model.pkl`, and `requirements.txt` reside:
```bash
cd d:\gglobal\placement-project\backend

az webapp up \
  --name placement-api-student101 \
  --resource-group rg-placement \
  --runtime "PYTHON:3.11" \
  --sku B1
```
*Flags explained*:
- `--name`: Globally unique Azure DNS prefix (`.azurewebsites.net`).
- `--runtime`: Linux Python 3.11 curated container.
- `--sku B1`: Basic Tier (Dedicated vCPU, supports custom startup scripts, avoids cold start).

#### Step 5: Configure Custom Linux Startup Command
Azure App Service Linux containers require Gunicorn with Uvicorn worker processes:
```bash
az webapp config set \
  --resource-group rg-placement \
  --name placement-api-student101 \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"
```

#### Step 6: Restart and Stream Live Application Logs
```bash
az webapp restart --name placement-api-student101 --resource-group rg-placement
az webapp log tail --name placement-api-student101 --resource-group rg-placement
```
*(Verify output shows: `Application startup complete` and `Uvicorn running on http://0.0.0.0:8000`)*.

#### Step 7: Verify Live Endpoints
- **Interactive Swagger Documentation**: `https://placement-api-student101.azurewebsites.net/docs`
- **Health Check Probe**: `https://placement-api-student101.azurewebsites.net/health`
- **Run automated test suite against Azure**:
  ```bash
  cd d:\gglobal\placement-project
  python tests/test_api.py --url https://placement-api-student101.azurewebsites.net
  ```

---

### Option B: Azure ML Studio (Visual Designer & AutoML)
Used for the practical examination and visual screenshot evidence in [ml.azure.com](https://ml.azure.com).

#### 1. Workspace & Compute Provisioning
1. In Azure Portal, search for **Azure Machine Learning** $\rightarrow$ Click **+ Create** $\rightarrow$ **New Workspace**.
2. Name: `mlw-placement-dev`, Resource Group: `rg-placement`, Region: `Central India`.
3. Launch Studio at [ml.azure.com](https://ml.azure.com).
4. Navigate to **Compute** $\rightarrow$ **Compute Clusters** $\rightarrow$ Click **+ New**:
   - VM Size: `Standard_DS11_v2`
   - Compute Name: `cpu-cluster`
   - Minimum nodes: `0` (Prevents idle charges!)
   - Maximum nodes: `2`

#### 2. Register Placement Dataset
1. In Studio, go to **Data** $\rightarrow$ **+ Create** $\rightarrow$ **From local files**.
2. Name: `placement-students-dataset`, Type: `Tabular`.
3. Upload `data/placement_data.csv`. Verify all 9 columns and headers.

#### 3. Visual Designer Pipeline
1. Go to **Designer** $\rightarrow$ **+ New pipeline**.
2. Assemble the following pre-built visual modules:
   - `placement-students-dataset`
   - $\rightarrow$ `Select Columns in Dataset` (Exclude `student_id`)
   - $\rightarrow$ `Clean Missing Data` (Replace missing with `Median` on `cgpa`, `aptitude_score`, `comm_skills`)
   - $\rightarrow$ `Split Data` (Fraction: `0.7`, Randomized: `True`, Stratified on `placed`)
   - $\rightarrow$ `Train Model` connected to `Two-Class Logistic Regression` (Label: `placed`)
   - $\rightarrow$ `Score Model` connected to the 30% Test output
   - $\rightarrow$ `Evaluate Model`
3. Click **Submit**. Review the generated ROC curve and confusion matrix.

#### 4. Automated ML (AutoML) Job
1. Go to **Automated ML** $\rightarrow$ **+ New Automated ML job**.
2. Select `placement-students-dataset`. Target column: `placed`.
3. Compute target: `cpu-cluster`.
4. Task: **Classification**. Primary metric: `AUC weighted`. Check *Explain best model*.
5. Set runtime timeout to `15` minutes.
6. Submit and review the AutoML model leaderboard (VotingEnsemble, LightGBM, RandomForest, LogisticRegression).

---

### Option C: Azure ML SDK v2 (Managed Online Endpoints)
**Files**: `azure_ml/azure_ml_sdk_v2.py`, `azure_ml/score.py`, `azure_ml/test_endpoint.py`

1. **Authentication**: Uses `DefaultAzureCredential()` or `InteractiveBrowserCredential()`.
2. **Register Data Asset**:
   ```python
   data_asset = Data(name="placement_students_dataset", version="1", path="../data/placement_data.csv", type=AssetTypes.URI_FILE)
   ml_client.data.create_or_update(data_asset)
   ```
3. **Register Custom Model**:
   ```python
   model_asset = Model(name="placement_prediction_model", version="1", path="../models/model.pkl", type=AssetTypes.CUSTOM_MODEL)
   ml_client.models.create_or_update(model_asset)
   ```
4. **Provision Managed Online Endpoint**:
   ```python
   endpoint = ManagedOnlineEndpoint(name="placement-endpoint-prod", auth_mode="key")
   ml_client.online_endpoints.begin_create_or_update(endpoint).result()
   ```
5. **Deploy with `score.py`**:
   Deploys on a `Standard_DS2_v2` instance using the curated Azure ML Scikit-learn container image, routing 100% of production traffic to deployment `blue`.
6. **Inference Test**:
   ```bash
   python azure_ml/test_endpoint.py --uri <SCORING_URI> --key <PRIMARY_KEY>
   ```

---

### Resource Teardown & Cost Management
> ⚠️ **CRITICAL FOR VIVA**: Examiners often ask how you manage cloud costs.
- **Compute Clusters**: Scaled with **Min nodes = 0**, so Azure automatically deallocates VM instances after 120 seconds of inactivity ($0 idle cost).
- **Managed Online Endpoints**: Dedicated VMs charge hourly as long as they exist. Delete them immediately after evaluation:
  ```bash
  az ml online-endpoint delete --name placement-endpoint-prod --resource-group rg-placement --workspace-name mlw-placement-dev --yes
  ```
- **Delete Entire Resource Group**:
  ```bash
  az group delete --name rg-placement --yes --no-wait
  ```

---

## 4. MASTER VIVA VOCE CATALOG (50+ HIGH-YIELD QUESTIONS & ANSWERS)

### Domain 1: Core Machine Learning Fundamentals (Q1–Q12)

#### Q1: What is Machine Learning?
**Answer**: Machine Learning is a branch of artificial intelligence where algorithms learn patterns and statistical relationships directly from historical data to make predictions or decisions on unseen data without being explicitly hardcoded with deterministic if-else rules.

#### Q2: What is Supervised Learning and why is this project an example of it?
**Answer**: Supervised learning trains a mathematical model on paired input-output examples $(\mathbf{x}_i, y_i)$ where ground truth labels are provided. Our project is supervised because each student record has both features (CGPA, backlogs, etc.) and a known ground-truth outcome (`placed`: Yes/No).

#### Q3: What is the difference between Classification and Regression?
**Answer**:
- **Classification** predicts discrete categorical class labels (e.g., Binary: Placed / Not Placed; Multiclass: Grade A / B / C).
- **Regression** predicts continuous numeric values (e.g., predicting starting salary package in LPA).

#### Q4: What is the difference between Features and Labels?
**Answer**:
- **Features ($X$)**: The independent measurable attributes used for prediction (e.g., CGPA, internships, projects, aptitude score).
- **Label ($y$)**: The dependent target variable we want the model to learn and predict (`placed`).

#### Q5: What is Data Leakage and how did you prevent it?
**Answer**: Data leakage occurs when information from outside the training dataset (such as test set mean or scale) contaminates model training. We prevented it by encapsulating transformers (`SimpleImputer`, `StandardScaler`) inside a Scikit-Learn `Pipeline`. Transformers fit *only* on training data and subsequently transform the test data.

#### Q6: Why did you use a 70/30 train-test split with Stratification?
**Answer**: 70% provides sufficient statistical power to fit model parameters while holding out 30% for unbiased validation. Stratification guarantees that the class distribution (63.1% Yes, 36.9% No) is preserved identically across training and test subsets, avoiding sampling bias.

#### Q7: What is Overfitting and how do you detect it?
**Answer**: Overfitting occurs when a model memorizes training noise and sample idiosyncrasies rather than generalizable relationships. It is detected when training accuracy is near 100% while test accuracy drops significantly. We countered it using depth regularization (`max_depth=6`) and 5-fold cross-validation.

#### Q8: What is Underfitting and how do you resolve it?
**Answer**: Underfitting happens when a model is overly simplistic and cannot capture underlying trends, resulting in low training and test scores. It is resolved by adding more expressive features, training longer, or selecting non-linear models.

#### Q9: What is K-Fold Cross-Validation?
**Answer**: A validation technique where the training dataset is split into $K$ equal folds. The model is trained on $K-1$ folds and validated on the remaining fold, rotating $K$ times. The average validation score reflects true generalization performance independent of a single lucky split.

#### Q10: What is a Confusion Matrix?
**Answer**: A $2 \times 2$ matrix summarizing classification outcomes:
- **True Positive (TP)**: Actually Placed, Predicted Placed.
- **True Negative (TN)**: Actually Not Placed, Predicted Not Placed.
- **False Positive (FP / Type I Error)**: Actually Not Placed, Predicted Placed.
- **False Negative (FN / Type II Error)**: Actually Placed, Predicted Not Placed.

#### Q11: What is the difference between Precision and Recall?
**Answer**:
- **Precision** ($\frac{TP}{TP + FP}$): Of all students the model predicted as "Placed", how many actually got placed? Focuses on minimizing False Positives.
- **Recall / Sensitivity** ($\frac{TP}{TP + FN}$): Of all students who were actually placed, how many did the model identify? Focuses on minimizing False Negatives.

#### Q12: What is the F1-Score and ROC-AUC?
**Answer**:
- **F1-Score**: Harmonic mean of Precision and Recall ($2 \cdot \frac{P \cdot R}{P + R}$), providing a single balanced metric when classes are uneven.
- **ROC-AUC**: The Area Under the Receiver Operating Characteristic curve (TPR vs. FPR across all thresholds). A score of 0.9573 means there is a 95.73% probability that the model ranks a randomly chosen placed candidate higher than an unplaced candidate.

---

### Domain 2: Project Architecture & Model Insights (Q13–Q22)

#### Q13: What algorithms did you compare in this project?
**Answer**: We evaluated three distinct mathematical families:
1. **Logistic Regression** (Generalized linear model with sigmoid link function)
2. **Decision Tree Classifier** (Non-parametric recursive partitioning)
3. **Random Forest Classifier** (Ensemble bootstrap aggregation of 100 decision trees)

#### Q14: What were the exact results of the three models?
**Answer**:
- **Logistic Regression**: Accuracy: **87.67%**, Precision: **90.86%**, Recall: **89.42%**, F1: **0.9013**, ROC-AUC: **0.9573**, 5-Fold CV F1: **0.9200**.
- **Random Forest**: Accuracy: **86.33%**, Precision: **87.37%**, Recall: **91.53%**, F1: **0.8941**, ROC-AUC: **0.9229**, 5-Fold CV F1: **0.8792**.
- **Decision Tree**: Accuracy: **82.00%**, Precision: **84.97%**, Recall: **86.77%**, F1: **0.8586**, ROC-AUC: **0.8674**, 5-Fold CV F1: **0.8653**.

#### Q15: Why did Logistic Regression outperform Random Forest in your dataset?
**Answer**: The true underlying placement probability in real recruitment follows a smooth, monotonic sigmoid relationship with weighted linear contributions. Logistic Regression directly fits continuous sigmoid boundaries, whereas decision trees approximate continuous curves using orthogonal step splits, introducing discretization errors on 1,000 samples.

#### Q16: How does Logistic Regression predict a binary outcome?
**Answer**: It computes a linear weighted sum of normalized inputs:
$$z = w_0 + w_1 x_1 + w_2 x_2 + \dots + w_n x_n$$
and applies the Sigmoid function $\sigma(z) = \frac{1}{1 + e^{-z}}$ to yield a calibrated probability between 0.0 and 1.0. If $P \ge 0.50$, it predicts "Yes" (Placed).

#### Q17: What were the most important features in determining student placement?
**Answer**:
1. **Active Backlogs (Highest negative weight)**: Having multiple uncleared backlogs triggers immediate recruitment disqualification.
2. **CGPA (Highest positive academic weight)**: Fundamental eligibility criterion for company shortlisting.
3. **Internships & Technical Projects (Strong positive weights)**: Practical industry experience strongly differentiates candidates in technical interview rounds.

#### Q18: Why did you scale features using `StandardScaler`?
**Answer**: Features like `aptitude_score` (30–100) have vastly wider ranges than `internships` (0–4) or `cgpa` (5–10). `StandardScaler` standardizes features to zero mean and unit variance ($z = \frac{x - \mu}{\sigma}$), ensuring gradient descent updates weights proportionally without large-scale features dominating.

#### Q19: Why use median imputation instead of mean imputation for missing values?
**Answer**: The median is robust against extreme outliers and skewed distributions. Academic metrics like backlogs and aptitude can have skewed distributions where mean values could introduce unrealistic fractional values.

#### Q20: What is the purpose of `models/metrics.json`?
**Answer**: It acts as an auditable metadata registry containing test evaluation scores, cross-validation metrics, Scikit-Learn versions, and confusion matrices, enabling the Streamlit frontend to dynamically display model benchmarks.

#### Q21: What is the Scikit-Learn version pinned in your requirements and why?
**Answer**: `scikit-learn==1.9.1`. Python pickle serialization (`joblib`) requires identical library versions across training and serving environments to avoid unpickling attribute errors on Azure.

#### Q22: What does the confusion matrix of your best model show?
**Answer**: On 300 test samples (111 actual Not Placed, 189 actual Placed):
- **True Negatives**: 94 correctly identified as Not Placed.
- **False Positives**: 17 wrongly predicted as Placed.
- **False Negatives**: 20 wrongly predicted as Not Placed.
- **True Positives**: 169 correctly identified as Placed.

---

### Domain 3: Azure Machine Learning Studio & MLOps (Q23–Q32)

#### Q23: What is an Azure Machine Learning Workspace?
**Answer**: The top-level centralized cloud resource in Azure that manages the complete ML lifecycle, including datasets, compute targets, experiments, model registries, and deployed REST endpoints.

#### Q24: What are the primary compute options in Azure ML?
**Answer**:
1. **Compute Instances**: Single-node cloud workstations (running Ubuntu Linux with JupyterLab and VS Code) for interactive data exploration.
2. **Compute Clusters**: Multi-node auto-scaling CPU/GPU clusters designed for automated training and batch execution (scales to 0 when idle).
3. **Managed Online Endpoints**: Fully managed cloud infrastructure for serving real-time predictions.

#### Q25: What is an Azure ML Datastore vs. Data Asset?
**Answer**:
- **Datastore**: A secure connection abstraction to an underlying Azure storage service (e.g., Azure Blob Storage or Azure Data Lake Gen2).
- **Data Asset**: A versioned metadata pointer to a specific file or folder in a datastore (`placement-students-dataset` v1).

#### Q26: What is Azure ML Designer?
**Answer**: A visual, drag-and-drop web canvas in Azure ML Studio that allows engineers to construct end-to-end data preparation, training, scoring, and evaluation pipelines without writing code.

#### Q27: What modules did you connect in your Azure ML Designer pipeline?
**Answer**:
Dataset $\rightarrow$ Select Columns in Dataset $\rightarrow$ Clean Missing Data $\rightarrow$ Split Data (70/30) $\rightarrow$ Train Model (Two-Class Logistic Regression) $\rightarrow$ Score Model $\rightarrow$ Evaluate Model.

#### Q28: What is Automated Machine Learning (AutoML)?
**Answer**: An automated feature in Azure ML that iterates through dozens of algorithms (LightGBM, XGBoost, Random Forest, Logistic Regression), optimizes hyperparameters, and generates a ranked leaderboard based on a target metric (AUC weighted).

#### Q29: What is an Azure ML Managed Online Endpoint?
**Answer**: A turnkey production hosting service in Azure ML that handles containerization, SSL certificates, load balancing, blue-green deployment traffic splitting, and auto-scaling for real-time model inference.

#### Q30: What is the role of `score.py` in Azure ML endpoints?
**Answer**: It is the scoring entry script inside the deployment container defining:
- `init()`: Runs once when container boots; locates and loads `model.pkl` into memory.
- `run(raw_data)`: Runs on every HTTP POST request; deserializes JSON, runs inference, and returns JSON predictions.

#### Q31: What is Azure ML SDK v2?
**Answer**: The modern Python SDK (`azure-ai-ml`) for programmatically interacting with Azure ML resources, enabling Infrastructure as Code (IaC) and CI/CD pipelines.

#### Q32: How did you prevent high cloud bills in Azure ML?
**Answer**: We configured compute clusters with **Minimum nodes = 0**, ensuring VM nodes deallocate after 120 idle seconds. For Managed Online Endpoints, we provisioned them for testing and deleted them immediately using `az ml online-endpoint delete`.

---

### Domain 4: Azure App Service & REST API Architecture (Q33–Q38)

#### Q33: What is Azure App Service and why did we host our backend there?
**Answer**: Azure App Service is a fully managed Platform-as-a-Service (PaaS) for hosting web apps and REST APIs. We used it for our FastAPI backend because it provides predictable low-cost hosting (Linux B1 SKU), custom startup commands, and automated HTTPS.

#### Q34: What is the difference between Azure App Service and Azure ML Endpoints?
**Answer**:
- **Azure App Service**: General-purpose web hosting PaaS ideal for custom full-stack web applications, lightweight REST APIs (FastAPI), with flat monthly pricing.
- **Azure ML Endpoint**: Specialized ML serving infrastructure with native model versioning, automatic data drift tracking, and model explainability, running on dedicated VM hourly billing.

#### Q35: Why did you choose FastAPI over Flask?
**Answer**:
1. **Asynchronous Throughput**: Native ASGI architecture for high concurrency.
2. **Automatic Data Validation**: Deep integration with Pydantic for request validation.
3. **Interactive Documentation**: Auto-generates OpenAPI (Swagger UI) at `/docs`.

#### Q36: What is the role of Gunicorn and Uvicorn in the backend?
**Answer**:
- **Uvicorn**: High-performance ASGI web server for running asynchronous Python code.
- **Gunicorn**: Process manager that forks and supervises multiple Uvicorn workers (`-k uvicorn.workers.UvicornWorker`) to ensure fault tolerance and concurrency on Linux.

#### Q37: What is the purpose of the `/health` endpoint?
**Answer**: It serves as a lightweight health probe for cloud monitoring services (such as Azure App Service health checks) to verify that the container is alive and the model is loaded into memory without running an inference computation.

#### Q38: How does the Streamlit frontend communicate with the backend?
**Answer**: The user inputs values on the Streamlit dashboard. Upon clicking "Predict placement", Streamlit dispatches an HTTP POST request containing a JSON payload to `{API_URL}/predict`. The backend returns the classification and probability, which Streamlit renders dynamically.

---

### Domain 5: Microsoft Responsible AI Principles (Q39–Q44)

#### Q39: What are Microsoft's 6 Core Responsible AI Principles?
**Answer**:
1. **Fairness**: AI systems should treat all people fairly.
2. **Reliability & Safety**: Systems must perform reliably and safely.
3. **Privacy & Security**: Systems must protect data privacy.
4. **Inclusiveness**: AI should empower everyone and be accessible.
5. **Transparency**: Systems should be understandable and explainable.
6. **Accountability**: Developers and organizations remain accountable for AI outcomes.

#### Q40: How does your project satisfy the principle of Fairness?
**Answer**: We strictly omitted demographic and sensitive personal attributes—such as gender, religion, race, caste, socio-economic status, and disability status—from the training features. Placement predictions are based strictly on objective academic performance and demonstrable technical competencies.

#### Q41: How does your project address Transparency and Explainability?
**Answer**: The system outputs calibrated probabilities (e.g., 85.2%) rather than opaque binary decisions. It provides visual influence bars and contextual recommendation messages explaining *why* a student is at risk (e.g., highlighting that clearing backlogs will restore placement eligibility).

#### Q42: How is Privacy and Security implemented in your project?
**Answer**:
- Personal student identifiers (`student_id`) are stripped before model training.
- API traffic is encrypted in transit using HTTPS/TLS.
- Cloud configurations use environment variables and role-based access control rather than hardcoded credentials.

#### Q43: How is Reliability and Safety ensured?
**Answer**:
- Pydantic models enforce strict boundary validation on inputs ($5.0 \le \text{CGPA} \le 10.0$).
- Median imputation handles missing values safely.
- 5-fold cross-validation demonstrated low model variance ($\pm 0.0174$).

#### Q44: What is Accountability in the context of this system?
**Answer**: The system is designed as a *decision-support tool* for training and placement officers and students, not an autonomous hiring filter. Human placement officers maintain final oversight over all campus recruitment recommendations.

---

### Domain 6: Azure AI Services Suite (AI-900 Breadth) (Q45–Q50)

#### Q45: What is Azure AI Vision?
**Answer**: A pre-built cloud service providing computer vision capabilities including optical character recognition (OCR), image analysis, object detection, face detection, and image tagging via REST API calls.

#### Q46: What is Azure AI Language?
**Answer**: A natural language processing service providing sentiment analysis, key phrase extraction, named entity recognition (NER), language detection, and conversational language understanding (CLU).

#### Q47: What is Azure AI Speech?
**Answer**: A cloud service that converts spoken audio to text (Speech-to-Text), synthesizes natural human speech from text (Text-to-Speech), and performs real-time speech translation.

#### Q48: What is Azure AI Document Intelligence (formerly Form Recognizer)?
**Answer**: An AI service that uses advanced machine learning to extract text, key-value pairs, tables, and document structures from invoices, receipts, identity documents, and academic transcripts.

#### Q49: What is Azure OpenAI Service?
**Answer**: An enterprise Azure offering that provides access to OpenAI's advanced generative AI models (such as GPT-4o and DALL-E 3) combined with Microsoft Azure's enterprise security, compliance, data privacy, and virtual network integration.

#### Q50: How could Azure AI Document Intelligence enhance this placement system in the future?
**Answer**: It could automatically parse PDF resumes and university marksheets, extracting CGPA, completed certifications, and internship details directly into the input schema, eliminating manual data entry.

---

## 5. THE 2-MINUTE VIVA ELEVATOR PITCH

When the examiner asks: *"Tell me about your project,"* deliver this structured, confident summary:

> *"Good morning, examiners. My capstone project is **Student Placement Prediction using Microsoft Azure Machine Learning**, aligned with the Microsoft Azure AI-900 certification curriculum.*
>
> *Campus recruitment is critical for academic institutions, yet traditional placement guidance is often reactive and informal. Our goal was to build a proactive, production-grade supervised classification system that predicts whether an undergraduate student will be placed based on 7 academic and demonstrable competency metrics.*
>
> *We developed a balanced 1,000-sample dataset reflecting real recruitment dynamics and injected 3% missing values to simulate real-world data challenges. To eliminate data leakage, we encapsulated median imputation, standard scaling, and estimators inside a Scikit-Learn pipeline. We benchmarked Logistic Regression, Decision Trees, and Random Forests using 5-fold cross-validation. **Logistic Regression** achieved the best overall performance with **87.67% accuracy, a 0.9013 F1-score, and an outstanding 0.9573 ROC-AUC**.*
>
> *For deployment, we built a dual-cloud architecture. First, an asynchronous **FastAPI REST backend** hosted on **Azure App Service (Linux B1)** using Gunicorn and Uvicorn workers, providing automated Swagger documentation and health monitoring. Second, we implemented cloud-native workflows in **Azure Machine Learning Studio**, including visual **Designer Pipelines**, **AutoML**, and **Managed Online Endpoints** via the Azure ML Python SDK v2. We also built an intuitive, lightweight **Streamlit dashboard** featuring candidate profile presets and a circular probability gauge.*
>
> *Finally, our project strictly adheres to Microsoft's **Responsible AI** principles—omitting demographic identifiers to ensure fairness, maintaining privacy through HTTPS encryption, and providing explainable feature influence bars.*
>
> *The application is live, and I would be happy to demonstrate the prediction flow or explain the underlying Azure architecture."*
