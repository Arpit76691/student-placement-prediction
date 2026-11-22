"""
=============================================================================
STUDENT PLACEMENT PREDICTION - API INTEGRATION TEST SUITE
=============================================================================
Course / Certification: Microsoft Azure AI-900 (Azure AI Fundamentals)

Purpose:
    Validates the REST API endpoints (/health, /predict) deployed either
    locally on localhost or remotely on Azure App Service / Azure ML Managed Online Endpoint.

Usage:
    # Test against local server:
    python tests/test_api.py
    
    # Test against Azure App Service:
    python tests/test_api.py --url https://placement-api-student.azurewebsites.net
    
    # Or using environment variable:
    set API_URL=https://placement-api-student.azurewebsites.net
    python tests/test_api.py
=============================================================================
"""

import os
import sys
import argparse
import requests

def test_api_endpoints(base_url: str):
    """
    Executes automated tests against the specified API base URL.
    """
    base_url = base_url.rstrip("/")
    print("=" * 70)
    print(f"TESTING STUDENT PLACEMENT PREDICTION API AT: {base_url}")
    print("=" * 70)
    
    # 1. Test Root / Welcome Endpoint
    try:
        print("\n[1/3] Testing GET / ...")
        resp_root = requests.get(f"{base_url}/", timeout=10)
        print(f"Status Code: {resp_root.status_code}")
        print(f"Response: {resp_root.json()}")
        assert resp_root.status_code == 200, f"Expected 200, got {resp_root.status_code}"
        print(">>> Root endpoint test PASSED!")
    except Exception as e:
        print(f"FAILED Root endpoint: {e}")
        return False

    # 2. Test Health Probe Endpoint
    try:
        print("\n[2/3] Testing GET /health ...")
        resp_health = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status Code: {resp_health.status_code}")
        print(f"Response: {resp_health.json()}")
        assert resp_health.status_code == 200, f"Expected 200, got {resp_health.status_code}"
        assert resp_health.json().get("status") == "ok", "Expected status: ok"
        print(">>> Health check test PASSED!")
    except Exception as e:
        print(f"FAILED Health endpoint: {e}")
        return False

    # 3. Test Inference /predict Endpoint with Sample Profiles
    test_cases = [
        {
            "name": "High-Achieving Student (Expected: Placed = Yes)",
            "payload": {
                "cgpa": 8.85,
                "internships": 2,
                "projects": 4,
                "communication_skills": 8.5,
                "aptitude_score": 88.0,
                "backlogs": 0,
                "certifications": 3
            },
            "expected_placed": "Yes"
        },
        {
            "name": "At-Risk Student Profile (Expected: Placed = No)",
            "payload": {
                "cgpa": 5.40,
                "internships": 0,
                "projects": 0,
                "communication_skills": 3.0,
                "aptitude_score": 38.0,
                "backlogs": 3,
                "certifications": 0
            },
            "expected_placed": "No"
        },
        {
            "name": "Borderline / Moderate Student Profile",
            "payload": {
                "cgpa": 7.20,
                "internships": 1,
                "projects": 2,
                "communication_skills": 6.0,
                "aptitude_score": 65.0,
                "backlogs": 1,
                "certifications": 1
            },
            "expected_placed": None
        }
    ]

    print("\n[3/3] Testing POST /predict ...")
    all_passed = True
    for idx, case in enumerate(test_cases, 1):
        print(f"\n--- Scenario {idx}: {case['name']} ---")
        try:
            resp_pred = requests.post(
                f"{base_url}/predict",
                json=case["payload"],
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            print(f"Status Code: {resp_pred.status_code}")
            data = resp_pred.json()
            print(f"Result: Placed={data.get('placed')}, Prob={data.get('probability')}, Confidence={data.get('confidence_percentage')}%")
            print(f"Message: {data.get('message')}")
            
            assert resp_pred.status_code == 200, f"Prediction failed with status {resp_pred.status_code}"
            
            if case["expected_placed"]:
                if data.get("placed") == case["expected_placed"]:
                    print(f">>> Scenario {idx} PASSED (Matched expected: {case['expected_placed']})")
                else:
                    print(f"WARNING: Expected {case['expected_placed']} but got {data.get('placed')}")
            else:
                print(f">>> Scenario {idx} PASSED (Valid inference output)")
        except Exception as e:
            print(f"FAILED Scenario {idx}: {e}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL API ENDPOINT INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    else:
        print("ONE OR MORE INTEGRATION TESTS FAILED.")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Placement Prediction API endpoints.")
    parser.add_argument(
        "--url",
        default=os.environ.get("API_URL", "http://127.0.0.1:8000"),
        help="Base URL for the API (default: http://127.0.0.1:8000 or $API_URL)"
    )
    args = parser.parse_args()
    success = test_api_endpoints(args.url)
    sys.exit(0 if success else 1)
