"""
=============================================================================
STUDENT PLACEMENT PREDICTION - FASTAPI BACKEND API
=============================================================================
Course / Certification: Microsoft Azure AI-900 (Azure AI Fundamentals)
Host Target: Azure App Service (Linux Python 3.11/3.12) / Azure ML Managed Online Endpoint

Description:
    Provides production-ready RESTful endpoints to predict student campus
    placement likelihood using a Scikit-Learn classification pipeline.
=============================================================================
"""

import os
import joblib
import pandas as pd
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Global reference to the loaded Scikit-Learn pipeline
ml_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that loads the machine learning pipeline into memory 
    once at application startup and cleans up upon shutdown.
    """
    global ml_pipeline
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")
    
    # Fallback to ../models/model.pkl if running in repository structure
    if not os.path.exists(model_path):
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "model.pkl")
        
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
        
    print(f"Loading trained machine learning pipeline from: {model_path}")
    ml_pipeline = joblib.load(model_path)
    print("Model pipeline successfully loaded into memory.")
    yield
    print("Application shutting down, releasing resources.")

# Initialize FastAPI application with comprehensive metadata for OpenAPI / Swagger
app = FastAPI(
    title="Student Placement Prediction API",
    description="""
    ## Azure AI-900 Internship Project API
    Predicts student campus placement outcomes (**Placed: Yes / No**) based on academic 
    and skill metrics using a trained Machine Learning Pipeline.
    
    ### Key Features:
    * **Automated Data Preprocessing**: SimpleImputer & StandardScaler
    * **Class Prediction**: Binary classification with placement probability
    * **Azure Ready**: Designed for Azure App Service & Azure ML Managed Online Endpoints
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Enable Cross-Origin Resource Sharing (CORS) for Streamlit frontend & web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local and cloud testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentFeatures(BaseModel):
    """
    Pydantic schema enforcing data types, default examples, and boundary validations
    for incoming student evaluation requests.
    """
    cgpa: float = Field(
        ..., ge=0.0, le=10.0, description="Cumulative Grade Point Average (0.0 to 10.0)", example=8.25
    )
    internships: int = Field(
        ..., ge=0, le=20, description="Number of completed internships", example=2
    )
    projects: int = Field(
        ..., ge=0, le=50, description="Number of completed academic / personal projects", example=3
    )
    communication_skills: float = Field(
        ..., ge=1.0, le=10.0, description="Communication & soft skills rating (1.0 to 10.0)", example=7.5
    )
    aptitude_score: float = Field(
        ..., ge=0.0, le=100.0, description="General aptitude and technical assessment score (0 to 100)", example=78.0
    )
    backlogs: int = Field(
        ..., ge=0, le=20, description="Number of active or historic backlogs", example=0
    )
    certifications: int = Field(
        ..., ge=0, le=30, description="Number of industry-recognized professional certifications", example=2
    )

class PredictionResponse(BaseModel):
    """
    Response schema returning placement outcome, probability, and contextual feedback.
    """
    placed: str = Field(..., description="Predicted placement outcome: 'Yes' or 'No'")
    probability: float = Field(..., description="Estimated probability of placement (0.0 to 1.0)")
    confidence_percentage: float = Field(..., description="Confidence percentage of the prediction")
    message: str = Field(..., description="Contextual career recommendation message")

@app.get("/", tags=["General"])
def read_root() -> Dict[str, Any]:
    """Root endpoint welcoming users and providing documentation links."""
    return {
        "project": "Student Placement Prediction using Microsoft Azure Machine Learning",
        "status": "Online",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health", tags=["Monitoring"])
def health_check() -> Dict[str, str]:
    """Health check probe endpoint for Azure App Service and container monitors."""
    if ml_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model pipeline is not yet loaded into memory."
        )
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict_placement(features: StudentFeatures) -> PredictionResponse:
    """
    Inference endpoint: accepts validated student characteristics, executes the pipeline,
    and returns placement classification with probability score.
    """
    global ml_pipeline
    if ml_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Model pipeline is currently unavailable."
        )
    
    try:
        # Construct DataFrame matching the exact feature order of training
        input_data = pd.DataFrame([{
            "cgpa": features.cgpa,
            "internships": features.internships,
            "projects": features.projects,
            "communication_skills": features.communication_skills,
            "aptitude_score": features.aptitude_score,
            "backlogs": features.backlogs,
            "certifications": features.certifications
        }])
        
        # Calculate predicted class and probability distribution
        predicted_class_idx = int(ml_pipeline.predict(input_data)[0])
        probabilities = ml_pipeline.predict_proba(input_data)[0]
        placement_prob = float(probabilities[1])  # Probability of class 1 ("Yes")
        
        placed_status = "Yes" if predicted_class_idx == 1 else "No"
        confidence_pct = round(placement_prob * 100 if placed_status == "Yes" else (1.0 - placement_prob) * 100, 2)
        
        # Generate friendly, actionable feedback message
        if placed_status == "Yes":
            if placement_prob >= 0.80:
                msg = "Outstanding profile! Very high probability of securing top-tier campus placement."
            else:
                msg = "Favorable profile for campus placement. Keep reinforcing core technical and interview skills."
        else:
            if features.backlogs > 0:
                msg = "Placement likelihood is reduced by active backlogs. Clearing backlogs will significantly boost chances."
            else:
                msg = "Profile indicates room for improvement in internships, aptitude, or communication skills."
                
        return PredictionResponse(
            placed=placed_status,
            probability=round(placement_prob, 4),
            confidence_percentage=confidence_pct,
            message=msg
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference computation error: {str(e)}"
        )
