# Microsoft Azure Machine Learning Studio - Step-by-Step Practical Guide

This comprehensive, click-by-click guide is tailored for your **Industrial Internship Exam** and the **Microsoft Azure AI-900 (Azure AI Fundamentals)** certification viva. It details how to implement the **Student Placement Prediction** project using the web-based Azure ML Studio interface ([https://ml.azure.com](https://ml.azure.com)).

---

## Overview of Azure ML Studio Interfaces

Azure ML Studio offers three distinct paradigms to build machine learning models:
1. **Azure ML Designer (Drag-and-Drop)**: Low-code / visual canvas for creating data pre-processing, training, and evaluation pipelines.
2. **Automated ML (AutoML)**: No-code paradigm where Azure automatically explores dozens of algorithms and hyperparameter combinations to find the best model.
3. **Notebooks / Cloud Compute (Code-First)**: Running Jupyter notebooks on dedicated cloud compute instances.

---

## Step 1: Create Azure ML Workspace and Cloud Compute

### 1.1 Create the Workspace
1. Log in to the [Azure Portal](https://portal.azure.com).
2. In the top search bar, type `Azure Machine Learning` and select it.
3. Click **+ Create** -> **New workspace**.
4. Configure the basic details:
   - **Subscription**: Select your active Azure subscription.
   - **Resource group**: Select `rg-placement` (or create a new one).
   - **Workspace name**: `mlw-placement-dev` (must be unique).
   - **Region**: `Central India` (or `East US`).
   - Storage account, Key vault, Application insights: *Leave defaults (Azure auto-creates them)*.
5. Click **Review + Create**, then click **Create**. Wait ~2-3 minutes until deployment completes.
6. Click **Go to resource**, then click the blue button **Launch studio** (which opens [ml.azure.com](https://ml.azure.com)).

> 📸 **SCREENSHOT 1: Azure ML Workspace Overview**  
> *Capture the workspace landing page showing the workspace name, resource group, and subscription.*

---

### 1.2 Create Compute Resources
1. In Azure ML Studio, click **Compute** in the left sidebar under the *Manage* group.
2. Under the **Compute instances** tab (for running notebooks):
   - Click **+ New**.
   - **Compute name**: `ci-placement-dev`.
   - **Virtual machine type**: `CPU`.
   - **Virtual machine size**: Select `Standard_DS11_v2` or `Standard_DS2_v2` (2 cores, 7–14 GB RAM).
   - Click **Create**.
3. Under the **Compute clusters** tab (for running Designer & AutoML training jobs):
   - Click **+ New**.
   - **Virtual machine priority**: `Dedicated` (or `Low priority` for cost savings).
   - **VM size**: `Standard_DS11_v2` (CPU). Click **Next**.
   - **Compute name**: `cpu-cluster`.
   - **Minimum number of nodes**: `0` *(crucial: 0 nodes ensures no billing when idle!)*.
   - **Maximum number of nodes**: `2`.
   - **Idle seconds before scale down**: `120`.
   - Click **Create**.

> 📸 **SCREENSHOT 2: Compute Resources Configuration**  
> *Capture the Compute Clusters page showing `cpu-cluster` in "Succeeded" state with 0 min nodes and 2 max nodes.*

---

## Step 2: Upload Placement Dataset as a Registered Data Asset

1. In the left navigation menu, click **Data** (under the *Assets* section).
2. Click **+ Create** -> **From local files**.
3. **Data basic info**:
   - **Name**: `placement-students-dataset`
   - **Type**: `Tabular` (or `uri_file` in SDK v2)
   - **Description**: `Student placement historical records with academic metrics and placement outcome.`
   - Click **Next**.
4. **Data source**: Choose the default datastore (`workspaceblobstore`). Click **Next**.
5. **File selection**: Click **Upload files**, browse to `data/placement_data.csv`, and upload it. Click **Next**.
6. **Settings and preview**:
   - **File format**: `Delimited`
   - **Delimiter**: `Comma`
   - **Encoding**: `UTF-8`
   - **Column headers**: `All files have same headers`
   - Verify that all 9 columns are detected correctly (`student_id`, `cgpa`, `internships`, `projects`, `communication_skills`, `aptitude_score`, `backlogs`, `certifications`, `placed`). Click **Next**.
7. **Schema**: Verify column data types:
   - `student_id`: String
   - `cgpa`: Decimal / Float
   - `internships`, `projects`, `backlogs`, `certifications`: Integer
   - `communication_skills`, `aptitude_score`: Integer / Decimal
   - `placed`: String (or Boolean)
   - Click **Next**.
8. Click **Create**.

> 📸 **SCREENSHOT 3: Registered Data Asset Preview**  
> *Capture the Data Asset page showing the preview table with columns and summary statistics.*

---

## Step 3: Visual Pipeline in Azure ML Designer

1. In the left menu, click **Designer** (under *Author*).
2. Click the **+** (New pipeline using classic prebuilt components).
3. In the pipeline settings gear icon on the top right:
   - Pipeline name: `Student-Placement-Designer-Pipeline`.
   - Default compute target: Select `cpu-cluster`.
4. From the left asset drawer, drag and connect the following components onto the canvas:

```
[ placement-students-dataset ]
              │
              ▼
    [ Select Columns in Dataset ]   (Exclude student_id, keep all 7 features + placed)
              │
              ▼
       [ Clean Missing Data ]       (Columns: cgpa, aptitude_score, comm_skills; Method: Median)
              │
              ▼
         [ Split Data ]             (Splitting mode: Split Rows, Fraction: 0.70, Stratified: True on 'placed')
         │          │
 (70% Train)      (30% Test)
         │                  │
         ▼                  │
   [ Train Model ] ◄── [ Two-Class Boosted Decision Tree ] or [ Two-Class Logistic Regression ]
         │                  │
         └──────────┬───────┘
                    ▼
              [ Score Model ]
                    │
                    ▼
             [ Evaluate Model ]
```

### Component Configuration Details:
- **Select Columns in Dataset**: Select *All columns*, then rule: *Exclude* column `student_id`.
- **Clean Missing Data**: Target columns: `cgpa`, `aptitude_score`, `communication_skills`. Cleaning mode: *Replace with median*.
- **Split Data**: Fraction of rows in the first output: `0.7`. Randomized split: `True`, Random seed: `42`, Stratified split: `True`, Stratification column: `placed`.
- **Two-Class Boosted Decision Tree** (or **Two-Class Logistic Regression**): Set Max number of leaves: `20`, Min instances per leaf: `10`, Learning rate: `0.1`.
- **Train Model**: Connect Left input to algorithm, Right input to Train output of Split Data. In properties, set **Label column**: `placed`.
- **Score Model**: Left input receives Trained Model; Right input receives Test output (30%) of Split Data.
- **Evaluate Model**: Receives Scored dataset output from Score Model.

5. Click **Submit** on the top right.
   - Experiment name: `placement-designer-run`.
   - Click **Submit** and wait for each step to turn green with a checkmark.

6. Right-click on **Evaluate Model** -> **Outputs + logs** -> Click the graph icon (Visualize):
   - Review the ROC curve, Confusion Matrix, Accuracy, Precision, Recall, and F1-score.

> 📸 **SCREENSHOT 4: Completed Designer Pipeline Canvas**  
> *Capture the full canvas with all nodes showing green checkmarks.*

> 📸 **SCREENSHOT 5: Designer Evaluate Model Metrics & ROC Curve**  
> *Capture the visual evaluation popup showing the ROC curve and confusion matrix.*

---

## Step 4: Automated ML (AutoML) Workflow

1. In the left menu, click **Automated ML** (under *Author*).
2. Click **+ New Automated ML job**.
3. **Select data asset**: Choose `placement-students-dataset`. Click **Next**.
4. **Configure job**:
   - Experiment name: `automl-placement-classification`.
   - Target column: `placed`.
   - Select compute type: `Compute cluster` -> `cpu-cluster`. Click **Next**.
5. **Task type and settings**:
   - Select **Classification**.
   - Click **View additional configuration settings**:
     - Primary metric: `AUC weighted` (or `Accuracy` / `Normalized macro recall`).
     - Explain best model: `Checked` (enables feature importance analysis).
     - Allowed/Blocked models: Leave default or block compute-intensive models.
     - Exit criterion: Job limit time = `15` minutes (to save credits).
     - Concurrency: Max concurrent iterations = `2`.
     - Click **Save**.
   - Under Featurization settings: Ensure imputation is set to *Auto*. Click **Next**.
6. **Validation and test**:
   - Validation type: `k-fold cross-validation`.
   - Number of cross-validations: `5`.
   - Test data: Select test split of 20%. Click **Next**.
7. Click **Submit**.

Once complete (~12-15 minutes):
- Navigate to the **Models** tab in the AutoML job page.
- Review the leaderboard comparing VotingEnsemble, LightGBM, RandomForest, and Logistic Regression.
- Click the best performing model -> Go to the **Explanations** tab to view global feature importance.

> 📸 **SCREENSHOT 6: AutoML Model Leaderboard**  
> *Capture the ranked list of algorithms with their AUC and Accuracy scores.*

> 📸 **SCREENSHOT 7: AutoML Feature Importance (Explanations)**  
> *Capture the bar chart showing CGPA, Backlogs, and Internships as top predictive drivers.*

---

## Step 5: Real-Time Endpoint Deployment & Testing

1. In the completed AutoML run (or completed Designer Real-Time Inference Pipeline), select the top-ranked model.
2. Click **Deploy** -> **Real-time endpoint**.
3. Configure the endpoint settings:
   - **Endpoint name**: `placement-realtime-endpoint`
   - **Compute type**: `Managed`
   - **Authentication type**: `Key-based`
   - **Instance type**: `Standard_DS2_v2` (1 instance)
4. Click **Deploy**. Wait ~5-8 minutes until the endpoint status changes to **Healthy**.
5. Click on the endpoint name and navigate to the **Test** tab:
   - Paste the sample student JSON payload:
   ```json
   {
     "data": [
       {
         "cgpa": 8.75,
         "internships": 2,
         "projects": 3,
         "communication_skills": 8.0,
         "aptitude_score": 82.0,
         "backlogs": 0,
         "certifications": 2
       }
     ]
   }
   ```
   - Click the blue **Test** button.
   - Verify that the response returns `{"predictions": [{"placed": "Yes", "probability": ...}]}`.

> 📸 **SCREENSHOT 8: Azure ML Real-Time Endpoint Test Console**  
> *Capture the Test tab with input JSON on the left and the successful JSON prediction on the right.*

---

## Step 6: Critical Teardown (Avoid Charges)

> ⚠️ **IMMEDIATELY AFTER TAKING SCREENSHOTS**:
> Go to **Endpoints** in Azure ML Studio, select `placement-realtime-endpoint`, and click **Delete**.
> Managed online endpoints allocate dedicated VM hours continuously. Deleting the endpoint ensures zero ongoing compute costs.
