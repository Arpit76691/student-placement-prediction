"""
=============================================================================
STUDENT PLACEMENT PREDICTION - SYNTHETIC DATASET GENERATOR
=============================================================================
Purpose:
    Generates a realistic synthetic dataset of 1,000 student records for 
    training machine learning models to predict campus placement (Placed: Yes/No).
    
    This project is aligned with the Microsoft Azure AI-900 (Azure AI Fundamentals)
    curriculum for binary classification tasks.

Features Generated:
    1. student_id: Unique identifier for each student (e.g., STU_1001)
    2. cgpa: Cumulative Grade Point Average (5.0 to 10.0)
    3. internships: Number of internships completed (0 to 4)
    4. projects: Number of academic / personal projects built (0 to 6)
    5. communication_skills: Rating of soft skills and English fluency (1 to 10)
    6. aptitude_score: Score in general aptitude / technical assessments (30 to 100)
    7. backlogs: Number of active or cleared academic backlogs (0 to 5)
    8. certifications: Number of industry-recognized certifications (0 to 6)
    9. placed: Target label - 'Yes' or 'No'

Key Characteristics:
    - Balanced, realistic distribution (~63% Placed, 37% Not Placed)
    - Domain-driven logic: Higher CGPA, internships, projects, aptitude, and communication
      increase placement odds, while academic backlogs heavily reduce them.
    - Controlled stochastic noise to reflect real-world non-deterministic outcomes (~88-92% ML accuracy).
    - Injected ~3% missing values across key features (CGPA, Aptitude, Communication)
      to simulate data imperfection and demonstrate robust ML preprocessing pipelines.
=============================================================================
"""

import os
import numpy as np
import pandas as pd

def generate_placement_dataset(n_samples: int = 1000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a synthetic DataFrame representing student placement statistics.
    
    Parameters:
        n_samples (int): Total number of student records (default: 1000)
        random_state (int): Seed for reproducibility
        
    Returns:
        pd.DataFrame: Generated dataset with realistic correlations and missing values.
    """
    np.random.seed(random_state)
    
    # 1. Generate Student IDs
    student_ids = [f"STU_{1001 + i}" for i in range(n_samples)]
    
    # 2. Generate Independent Feature Distributions
    # CGPA: Normal distribution centered around 7.5, bounded between 5.0 and 10.0
    cgpa = np.random.normal(loc=7.5, scale=1.1, size=n_samples)
    cgpa = np.clip(cgpa, 5.0, 10.0).round(2)
    
    # Internships: Distribution between 0 and 4
    internships = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.30, 0.35, 0.20, 0.10, 0.05])
    
    # Projects: Discrete range 0 to 6
    projects = np.random.choice([0, 1, 2, 3, 4, 5, 6], size=n_samples, p=[0.10, 0.20, 0.30, 0.20, 0.10, 0.06, 0.04])
    
    # Communication Skills: 1 to 10 rating
    comm_skills = np.random.normal(loc=6.5, scale=1.8, size=n_samples)
    comm_skills = np.clip(np.round(comm_skills), 1, 10).astype(int)
    
    # Aptitude Score: 30 to 100
    aptitude_score = np.random.normal(loc=65.0, scale=15.0, size=n_samples)
    aptitude_score = np.clip(np.round(aptitude_score), 30, 100).astype(int)
    
    # Backlogs: Discrete range 0 to 5, skewed towards 0
    backlogs = np.random.choice([0, 1, 2, 3, 4, 5], size=n_samples, p=[0.60, 0.20, 0.10, 0.05, 0.03, 0.02])
    
    # Certifications: Discrete range 0 to 6
    certifications = np.random.choice([0, 1, 2, 3, 4, 5, 6], size=n_samples, p=[0.25, 0.30, 0.22, 0.12, 0.06, 0.03, 0.02])
    
    # 3. Calculate Placement Log-Odds (Linear Combination with Domain Weights)
    # Balanced intercept (-16.0) produces ~60-65% placement rate with realistic ~90% model accuracy
    z = (
        -16.0
        + (1.25 * cgpa)
        + (0.80 * internships)
        + (0.50 * projects)
        + (0.40 * comm_skills)
        + (0.05 * aptitude_score)
        - (1.40 * backlogs)
        + (0.35 * certifications)
        + np.random.normal(0, 1.0, size=n_samples)  # Gaussian noise for realistic outcome uncertainty
    )
    
    # Convert log-odds to probability using the Sigmoid function: P = 1 / (1 + e^-z)
    probabilities = 1.0 / (1.0 + np.exp(-z))
    
    # Class assignment based on standard 0.50 classification threshold
    placed = np.where(probabilities >= 0.50, "Yes", "No")
    
    # Create DataFrame
    df = pd.DataFrame({
        "student_id": student_ids,
        "cgpa": cgpa,
        "internships": internships,
        "projects": projects,
        "communication_skills": comm_skills,
        "aptitude_score": aptitude_score,
        "backlogs": backlogs,
        "certifications": certifications,
        "placed": placed
    })
    
    # 4. Inject ~3% missing values (NaN) to demonstrate real-world preprocessing
    # Missing values are injected into numerical columns: cgpa, aptitude_score, and communication_skills
    for col in ["cgpa", "aptitude_score", "communication_skills"]:
        mask = np.random.rand(n_samples) < 0.03
        df.loc[mask, col] = np.nan
        
    return df

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "placement_data.csv")
    
    print("=" * 60)
    print("Generating synthetic placement dataset (Balanced & Realistic)...")
    df = generate_placement_dataset(n_samples=1000, random_state=42)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully saved to: {output_path}")
    print(f"Dataset Shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nClass Distribution:")
    print(df["placed"].value_counts(normalize=True).round(3) * 100)
    print("\nMissing Values Count:")
    print(df.isnull().sum())
    print("=" * 60)
