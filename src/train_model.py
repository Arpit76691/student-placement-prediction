"""
=============================================================================
STUDENT PLACEMENT PREDICTION - MODEL TRAINING & EVALUATION PIPELINE
=============================================================================
Course / Certification: Microsoft Azure AI-900 (Azure AI Fundamentals)
Topic: Supervised Machine Learning - Binary Classification Pipeline

Key Steps:
    1. Exploratory Data Analysis (EDA) and Visualization
    2. Data Preprocessing (Imputation, Encoding, Scaling) via Scikit-Learn Pipeline
    3. Model Training & Comparison:
       - Model 1: Logistic Regression (Linear baseline)
       - Model 2: Decision Tree Classifier (Non-linear tree baseline)
       - Model 3: Random Forest Classifier (Ensemble bagging method)
    4. Model Evaluation (Accuracy, Precision, Recall, F1, ROC-AUC, 5-Fold CV)
    5. Artifact Persistence:
       - Best Pipeline saved to `models/model.pkl`
       - All Metrics saved to `models/metrics.json`
       - Visualizations saved to `screenshots/*.png`
=============================================================================
"""

import os
import json
import joblib
import sklearn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    classification_report
)

# Set global plotting style for professional presentation
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

def ensure_directories():
    """Ensure all required output directories exist."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    screenshots_dir = os.path.join(base_dir, "screenshots")
    models_dir = os.path.join(base_dir, "models")
    backend_dir = os.path.join(base_dir, "backend")
    
    for d in [screenshots_dir, models_dir, backend_dir]:
        os.makedirs(d, exist_ok=True)
    return base_dir, screenshots_dir, models_dir, backend_dir

def main():
    base_dir, screenshots_dir, models_dir, backend_dir = ensure_directories()
    data_path = os.path.join(base_dir, "data", "placement_data.csv")
    
    print("=" * 70)
    print("STEP 1: LOADING DATASET & EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 70)
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    
    print(f"\nDataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nSummary Statistics of Numerical Features:")
    print(df.describe().round(2))
    
    print("\nMissing Values Count:")
    missing = df.isnull().sum()
    print(missing[missing > 0])
    
    feature_cols = [
        "cgpa",
        "internships",
        "projects",
        "communication_skills",
        "aptitude_score",
        "backlogs",
        "certifications"
    ]
    target_col = "placed"
    
    # --- Visualization 1: Class Balance ---
    print("\nGenerating Chart 1: Class Balance...")
    plt.figure(figsize=(6, 5))
    class_counts = df[target_col].value_counts()
    colors = ["#2ecc71" if c == "Yes" else "#e74c3c" for c in class_counts.index]
    ax = sns.barplot(x=class_counts.index, y=class_counts.values, palette=colors)
    plt.title("Target Distribution (Placed: Yes vs No)", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Placement Status", fontsize=12)
    plt.ylabel("Number of Students", fontsize=12)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())} ({p.get_height()/len(df)*100:.1f}%)",
                    (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                    ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    plt.savefig(os.path.join(screenshots_dir, "class_balance.png"), dpi=300)
    plt.close()
    
    # --- Visualization 2: Correlation Heatmap ---
    print("Generating Chart 2: Correlation Heatmap...")
    plt.figure(figsize=(9, 7))
    corr_df = df[feature_cols].copy()
    corr_df["placed_numeric"] = df[target_col].map({"Yes": 1, "No": 0})
    corr_matrix = corr_df.corr()
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True, linewidths=0.5)
    plt.title("Feature Correlation Matrix (including Target)", fontsize=14, fontweight="bold", pad=12)
    plt.savefig(os.path.join(screenshots_dir, "correlation_heatmap.png"), dpi=300)
    plt.close()
    
    # --- Visualization 3: Feature Distributions & Boxplots ---
    print("Generating Chart 3: Feature Distributions & Placement Comparisons...")
    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    axes = axes.flatten()
    for i, col in enumerate(feature_cols):
        sns.boxplot(x=target_col, y=col, data=df, ax=axes[i], palette=["#e74c3c", "#2ecc71"])
        axes[i].set_title(f"{col.replace('_', ' ').title()} vs Placed", fontweight="bold")
        axes[i].set_xlabel("Placed")
    # Hide the 8th subplot (since there are 7 features)
    fig.delaxes(axes[7])
    plt.suptitle("Feature Distributions Segregated by Placement Outcome", fontsize=16, fontweight="bold")
    plt.savefig(os.path.join(screenshots_dir, "distributions.png"), dpi=300)
    plt.close()
    
    print("=" * 70)
    print("STEP 2: PREPROCESSING & STRATIFIED TRAIN/TEST SPLIT")
    print("=" * 70)
    X = df[feature_cols]
    y = df[target_col].map({"Yes": 1, "No": 0})
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    print(f"Training Set: {X_train.shape[0]} samples (70%)")
    print(f"Testing Set:  {X_test.shape[0]} samples (30%)")
    
    print("=" * 70)
    print("STEP 3 & 4: MODEL TRAINING, CROSS-VALIDATION & EVALUATION")
    print("=" * 70)
    
    # Define candidate models
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=500),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=5, min_samples_leaf=10),
        "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100, max_depth=6, min_samples_leaf=5)
    }
    
    pipelines = {}
    metrics_summary = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, clf in models.items():
        print(f"\n--- Training & Evaluating: {name} ---")
        pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", clf)
        ])
        
        # 5-Fold Cross-Validation on Training Data
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1")
        
        # Fit pipeline on full training data
        pipe.fit(X_train, y_train)
        pipelines[name] = pipe
        
        # Evaluate on Test Data
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]
        
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred))
        rec = float(recall_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred))
        roc_auc = float(roc_auc_score(y_test, y_prob))
        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std())
        
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        metrics_summary[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "cv_f1_mean": round(cv_mean, 4),
            "cv_f1_std": round(cv_std, 4),
            "confusion_matrix": cm
        }
        
        print(f"Accuracy:  {acc * 100:.2f}%")
        print(f"Precision: {prec * 100:.2f}%")
        print(f"Recall:    {rec * 100:.2f}%")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC-AUC:   {roc_auc:.4f}")
        print(f"5-Fold CV F1: {cv_mean:.4f} (+/- {cv_std:.4f})")
    
    # --- Select Best Model ---
    best_model_name = max(metrics_summary.keys(), key=lambda k: (metrics_summary[k]["f1_score"], metrics_summary[k]["roc_auc"]))
    best_pipeline = pipelines[best_model_name]
    print(f"\n>>> Selected Best Model: {best_model_name} <<<")
    
    # --- Visualization 4: Model Comparison Bar Chart ---
    print("\nGenerating Chart 4: Model Comparison...")
    comp_df = pd.DataFrame(metrics_summary).T[["accuracy", "precision", "recall", "f1_score", "roc_auc"]]
    comp_plot_df = comp_df.reset_index().melt(id_vars="index", var_name="Metric", value_name="Score")
    comp_plot_df.rename(columns={"index": "Model"}, inplace=True)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x="Metric", y="Score", hue="Model", data=comp_plot_df, palette="viridis")
    plt.title("Comparative Performance Across Models", fontsize=14, fontweight="bold", pad=12)
    plt.ylim(0.65, 1.0)
    plt.ylabel("Score", fontsize=12)
    plt.xlabel("Evaluation Metric", fontsize=12)
    plt.legend(loc="lower right")
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(f"{h:.2f}", (p.get_x() + p.get_width() / 2., h + 0.005),
                        ha="center", va="bottom", fontsize=8, rotation=90)
    plt.savefig(os.path.join(screenshots_dir, "model_comparison.png"), dpi=300)
    plt.close()
    
    # --- Visualization 5: Confusion Matrix for Best Model ---
    print(f"Generating Chart 5: Confusion Matrix for {best_model_name}...")
    plt.figure(figsize=(6, 5))
    best_cm = np.array(metrics_summary[best_model_name]["confusion_matrix"])
    labels = ["Not Placed (No)", "Placed (Yes)"]
    sns.heatmap(best_cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, cbar=False)
    plt.title(f"Confusion Matrix: {best_model_name}", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Predicted Label", fontsize=11, fontweight="bold")
    plt.ylabel("Actual True Label", fontsize=11, fontweight="bold")
    plt.savefig(os.path.join(screenshots_dir, "confusion_matrix.png"), dpi=300)
    plt.close()
    
    # --- Visualization 6: ROC Curves ---
    print("Generating Chart 6: ROC Curves...")
    plt.figure(figsize=(8, 6))
    for name, pipe in pipelines.items():
        probs = pipe.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, probs)
        auc = metrics_summary[name]["roc_auc"]
        plt.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {auc:.3f})")
    plt.plot([0, 1], [0, 1], color="grey", lw=1.5, linestyle="--", label="Random Chance (AUC = 0.500)")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=11)
    plt.ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11)
    plt.title("Receiver Operating Characteristic (ROC) Curves", fontsize=13, fontweight="bold", pad=12)
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(screenshots_dir, "roc_curve.png"), dpi=300)
    plt.close()
    
    # --- Visualization 7: Feature Importance ---
    print(f"Generating Chart 7: Feature Importance for {best_model_name}...")
    plt.figure(figsize=(8, 5))
    classifier = best_pipeline.named_steps["classifier"]
    
    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        importances = np.abs(classifier.coef_[0])
    else:
        importances = np.ones(len(feature_cols))
        
    feat_df = pd.DataFrame({"Feature": feature_cols, "Importance": importances})
    feat_df = feat_df.sort_values(by="Importance", ascending=False)
    
    ax = sns.barplot(x="Importance", y="Feature", data=feat_df, palette="mako")
    plt.title(f"Feature Importance ({best_model_name})", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Relative Importance Score", fontsize=11)
    plt.ylabel("Student Attribute", fontsize=11)
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f"{width:.3f}", (width + 0.005, p.get_y() + p.get_height() / 2.),
                    va="center", fontsize=10)
    plt.savefig(os.path.join(screenshots_dir, "feature_importance.png"), dpi=300)
    plt.close()
    
    # Save artifacts
    print("=" * 70)
    print("STEP 5: SAVING TRAINED PIPELINE & METRICS")
    print("=" * 70)
    
    model_save_path = os.path.join(models_dir, "model.pkl")
    joblib.dump(best_pipeline, model_save_path)
    print(f"Trained pipeline saved to: {model_save_path}")
    
    # Also save a copy inside backend/ for self-contained deployment
    backend_model_path = os.path.join(backend_dir, "model.pkl")
    joblib.dump(best_pipeline, backend_model_path)
    print(f"Backend deployment copy saved to: {backend_model_path}")
    
    # Store complete metadata
    export_data = {
        "best_model": best_model_name,
        "scikit_learn_version": sklearn.__version__,
        "features": feature_cols,
        "target": target_col,
        "classes": ["No", "Yes"],
        "models": metrics_summary
    }
    
    metrics_path = os.path.join(models_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(export_data, f, indent=4)
    print(f"Performance metrics saved to: {metrics_path}")
    
    print("\nScikit-Learn Version used:", sklearn.__version__)
    print("Training and evaluation completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
