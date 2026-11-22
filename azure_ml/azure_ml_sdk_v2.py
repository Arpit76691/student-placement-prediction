"""
=============================================================================
AZURE MACHINE LEARNING SDK v2 - END-TO-END DEPLOYMENT WORKFLOW
=============================================================================
Course / Certification: Microsoft Azure AI-900 (Azure AI Fundamentals)
Topic: Azure Machine Learning (SDK v2) Automation Script

Workflow:
    1. Authenticate with Azure via DefaultAzureCredential / InteractiveBrowserCredential
    2. Connect to the Azure ML Workspace (MLClient)
    3. Register Placement Dataset as a Versioned Azure ML Data Asset (URI_FILE)
    4. Register Trained Pipeline (`model.pkl`) as an Azure ML Custom Model
    5. Provision a Managed Online Endpoint (Real-Time REST API)
    6. Deploy Model with ManagedOnlineDeployment using Azure Curated Environment
    7. Allocate 100% traffic to the deployment and run a test invocation
    8. COST WARNING & RESOURCE CLEANUP GUIDANCE
=============================================================================
"""

import os
import time
import json
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    Data,
    Model,
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Environment,
    CodeConfiguration
)
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

# =============================================================================
# CONFIGURATION & PLACEHOLDERS (Fill these from your Azure Portal)
# =============================================================================
# WARNING: Replace these placeholders with your real Azure subscription credentials.
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "<YOUR_AZURE_SUBSCRIPTION_ID>")
RESOURCE_GROUP   = os.getenv("AZURE_RESOURCE_GROUP", "rg-placement")
WORKSPACE_NAME   = os.getenv("AZURE_WORKSPACE_NAME", "mlw-placement-dev")

ENDPOINT_NAME    = f"placement-endpoint-{int(time.time())}"  # Endpoints require globally unique names
DEPLOYMENT_NAME  = "blue"

print("=" * 75)
print("AZURE MACHINE LEARNING SDK v2 - AUTOMATED DEPLOYMENT")
print("=" * 75)

# -----------------------------------------------------------------------------
# STEP 1: AUTHENTICATION AND WORKSPACE CONNECTION
# -----------------------------------------------------------------------------
print("\n[Step 1/6] Connecting to Azure ML Workspace...")
try:
    # First attempt automatic authentication (Azure CLI session or environment vars)
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME
    )
    # Trigger a lightweight call to verify connectivity
    ws = ml_client.workspaces.get(WORKSPACE_NAME)
    print(f"Connected successfully to Workspace: '{ws.name}' in Region: '{ws.location}'")
except Exception as e:
    print(f"Default credential check failed ({e}). Attempting interactive browser login...")
    credential = InteractiveBrowserCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME
    )

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# -----------------------------------------------------------------------------
# STEP 2: REGISTER DATASET AS A VERSIONED DATA ASSET
# -----------------------------------------------------------------------------
print("\n[Step 2/6] Registering Data Asset in Azure ML Datastore...")
dataset_local_path = os.path.join(base_dir, "data", "placement_data.csv")

placement_data_asset = Data(
    name="placement_students_dataset",
    version="1",
    description="Student Academic and Placement records for binary classification (AI-900).",
    path=dataset_local_path,
    type=AssetTypes.URI_FILE
)

data_asset_created = ml_client.data.create_or_update(placement_data_asset)
print(f"Data Asset created: Name='{data_asset_created.name}', Version={data_asset_created.version}")

# -----------------------------------------------------------------------------
# STEP 3: REGISTER TRAINED MODEL ARTIFACT
# -----------------------------------------------------------------------------
print("\n[Step 3/6] Registering Model in Azure ML Model Registry...")
model_local_path = os.path.join(base_dir, "models", "model.pkl")

placement_model_asset = Model(
    name="placement_prediction_model",
    version="1",
    description="Scikit-Learn (v1.9.1) Pipeline including Imputer, Scaler, and Classifier.",
    path=model_local_path,
    type=AssetTypes.CUSTOM_MODEL
)

model_asset_created = ml_client.models.create_or_update(placement_model_asset)
print(f"Model Registered: Name='{model_asset_created.name}', Version={model_asset_created.version}")

# -----------------------------------------------------------------------------
# STEP 4: CREATE MANAGED ONLINE ENDPOINT
# -----------------------------------------------------------------------------
print(f"\n[Step 4/6] Creating Managed Online Endpoint: '{ENDPOINT_NAME}'...")
endpoint = ManagedOnlineEndpoint(
    name=ENDPOINT_NAME,
    description="Real-time HTTP inference endpoint for Student Placement Classification",
    auth_mode="key"
)

endpoint_poller = ml_client.online_endpoints.begin_create_or_update(endpoint)
endpoint_result = endpoint_poller.result()
print(f"Managed Online Endpoint '{endpoint_result.name}' successfully provisioned.")

# -----------------------------------------------------------------------------
# STEP 5: DEPLOY MODEL TO MANAGED ONLINE ENDPOINT
# -----------------------------------------------------------------------------
print(f"\n[Step 5/6] Deploying Model to Deployment '{DEPLOYMENT_NAME}' (Standard_DS2_v2)...")
print("NOTE: Cloud VM provisioning and container building typically takes 6-10 minutes.")

# Reference Azure ML Curated Scikit-Learn Environment
# (or define custom conda environment)
curated_env_name = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:1"

deployment = ManagedOnlineDeployment(
    name=DEPLOYMENT_NAME,
    endpoint_name=ENDPOINT_NAME,
    model=model_asset_created,
    code_configuration=CodeConfiguration(
        code=os.path.join(base_dir, "azure_ml"),
        scoring_script="score.py"
    ),
    environment=curated_env_name,
    instance_type="Standard_DS2_v2",
    instance_count=1
)

deployment_poller = ml_client.online_deployments.begin_create_or_update(deployment)
deployment_result = deployment_poller.result()
print(f"Deployment '{deployment_result.name}' successfully created.")

# Route 100% of endpoint traffic to this deployment
endpoint.traffic = {DEPLOYMENT_NAME: 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
print("100% incoming traffic allocated to deployment.")

# -----------------------------------------------------------------------------
# STEP 6: TEST LIVE INFERENCE VIA ENDPOINT INVOCATION
# -----------------------------------------------------------------------------
print("\n[Step 6/6] Testing Managed Online Endpoint with sample student payload...")
test_request_json = os.path.join(base_dir, "azure_ml", "sample_request.json")
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
        }
    ]
}

with open(test_request_json, "w") as f:
    json.dump(sample_payload, f, indent=2)

response = ml_client.online_endpoints.invoke(
    endpoint_name=ENDPOINT_NAME,
    request_file=test_request_json
)
print("Inference Response from Azure ML Endpoint:")
print(response)

# =============================================================================
# CRITICAL COST ADVISORY & TEARDOWN
# =============================================================================
print("\n" + "!" * 75)
print("IMPORTANT COST WARNING: AZURE ML MANAGED ONLINE ENDPOINTS")
print("Azure Managed Online Endpoints use dedicated Virtual Machines (Standard_DS2_v2)")
print("which accrue HOURLY CHARGES as long as they exist, even if idle!")
print("\nTo delete the endpoint and stop all billing, run:")
print(f"  az ml online-endpoint delete --name {ENDPOINT_NAME} --resource-group {RESOURCE_GROUP} --workspace-name {WORKSPACE_NAME} --yes")
print("Or use Python:")
print(f"  ml_client.online_endpoints.begin_delete(name='{ENDPOINT_NAME}')")
print("!" * 75)
