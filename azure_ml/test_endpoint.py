"""
=============================================================================
AZURE MACHINE LEARNING - REST ENDPOINT INVOCATION TESTER
=============================================================================
Course / Certification: Microsoft Azure AI-900 (Azure AI Fundamentals)

Description:
    Tests an Azure Machine Learning Managed Online Endpoint using standard
    HTTP POST requests, Bearer token authentication (Scoring Key), and JSON payload.

Usage:
    # Set your endpoint URI and primary key:
    python azure_ml/test_endpoint.py --uri <SCORING_URI> --key <PRIMARY_KEY>
=============================================================================
"""

import os
import json
import argparse
import requests

def test_azure_ml_endpoint(scoring_uri: str, api_key: str):
    """
    Sends an inference payload to the Azure ML Managed Online Endpoint.
    """
    print("=" * 70)
    print("INVOKING AZURE ML MANAGED ONLINE ENDPOINT")
    print(f"Endpoint URI: {scoring_uri}")
    print("=" * 70)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    sample_payload = {
        "data": [
            {
                "cgpa": 8.75,
                "internships": 2,
                "projects": 3,
                "communication_skills": 8.0,
                "aptitude_score": 82.0,
                "backlogs": 0,
                "certifications": 2
            },
            {
                "cgpa": 5.30,
                "internships": 0,
                "projects": 0,
                "communication_skills": 3.0,
                "aptitude_score": 35.0,
                "backlogs": 3,
                "certifications": 0
            }
        ]
    }
    
    print("\nSending Payload:")
    print(json.dumps(sample_payload, indent=2))
    
    try:
        response = requests.post(scoring_uri, headers=headers, json=sample_payload, timeout=30)
        print(f"\nHTTP Status Code: {response.status_code}")
        print("Response Content:")
        print(response.text)
        
        if response.status_code == 200:
            print("\n>>> Azure ML Managed Online Endpoint responded successfully!")
        else:
            print(f"\nEndpoint invocation returned error code: {response.status_code}")
            
    except Exception as e:
        print(f"\nFailed to connect to endpoint: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invoke Azure ML Managed Online Endpoint.")
    parser.add_argument(
        "--uri",
        default=os.environ.get("AZUREML_SCORING_URI", "https://<your-endpoint-name>.<region>.inference.ml.azure.com/score"),
        help="Azure ML Managed Online Endpoint Scoring URI"
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("AZUREML_PRIMARY_KEY", "<your-scoring-key>"),
        help="Azure ML Endpoint Primary Authentication Key"
    )
    args = parser.parse_args()
    test_azure_ml_endpoint(args.uri, args.key)
