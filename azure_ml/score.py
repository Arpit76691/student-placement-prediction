"""
=============================================================================
AZURE MACHINE LEARNING - MANAGED ONLINE ENDPOINT SCORING SCRIPT
=============================================================================
Course / Certification: Microsoft Azure AI-900 (Azure AI Fundamentals)

Description:
    Standard scoring script interface required by Azure Machine Learning Managed
    Online Endpoints. Contains two compulsory functions:
      1. init(): Executed once when the deployment container starts. Loads the model.
      2. run(raw_data): Executed on every HTTP inference request.
=============================================================================
"""

import os
import json
import joblib
import logging
import pandas as pd

# Global variable to hold the loaded model pipeline
model = None

def init():
    """
    Executed when the scoring container starts up.
    Reads the model from the AZUREML_MODEL_DIR environment variable or fallback path.
    """
    global model
    logging.info("Initializing Azure ML scoring script...")
    
    # Azure ML sets AZUREML_MODEL_DIR to the directory containing registered artifacts
    model_dir = os.getenv("AZUREML_MODEL_DIR", "")
    
    # Candidate paths to locate model.pkl
    candidate_paths = [
        os.path.join(model_dir, "model.pkl"),
        os.path.join(model_dir, "models", "model.pkl"),
        os.path.join(os.path.dirname(__file__), "..", "models", "model.pkl"),
        os.path.join(os.path.dirname(__file__), "model.pkl"),
        "models/model.pkl"
    ]
    
    model_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            model_path = p
            break
            
    if model_path is None:
        raise FileNotFoundError(f"Could not locate model.pkl in candidate paths: {candidate_paths}")
        
    logging.info(f"Loading trained model pipeline from: {model_path}")
    model = joblib.load(model_path)
    logging.info("Model pipeline loaded successfully into Azure ML scoring runtime.")

def run(raw_data):
    """
    Executed on every POST inference request.
    
    Parameters:
        raw_data (str): Raw JSON string received in the HTTP request payload.
        
    Returns:
        str: JSON-encoded response with predictions and probabilities.
    """
    global model
    logging.info("Processing incoming scoring request...")
    
    try:
        data_dict = json.loads(raw_data)
        
        # Support both 'data' wrapper and flat list/dict format
        if "data" in data_dict:
            payload = data_dict["data"]
        else:
            payload = data_dict
            
        # If payload is a single object, wrap it into a list
        if isinstance(payload, dict):
            payload = [payload]
            
        input_df = pd.DataFrame(payload)
        
        # Ensure correct column naming and order
        feature_order = [
            "cgpa",
            "internships",
            "projects",
            "communication_skills",
            "aptitude_score",
            "backlogs",
            "certifications"
        ]
        input_df = input_df[feature_order]
        
        # Perform inference
        predictions = model.predict(input_df)
        probabilities = model.predict_proba(input_df)[:, 1]
        
        results = []
        for pred, prob in zip(predictions, probabilities):
            results.append({
                "placed": "Yes" if int(pred) == 1 else "No",
                "probability": round(float(prob), 4),
                "confidence_percentage": round(float(prob if pred == 1 else (1.0 - prob)) * 100, 2)
            })
            
        return json.dumps({"predictions": results})
        
    except Exception as e:
        error_msg = f"Inference execution failed: {str(e)}"
        logging.error(error_msg)
        return json.dumps({"error": error_msg})
