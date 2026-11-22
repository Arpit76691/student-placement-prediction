# Step-by-Step Azure Deployment Guide

This guide provides copy-paste Azure CLI commands and instructions to deploy the **Student Placement Prediction API (FastAPI)** and optional **Streamlit Frontend** to **Microsoft Azure App Service** (Linux).

---

## Prerequisites

1. **Azure Subscription**: Active subscription (e.g., Azure Free Trial, Azure for Students, or Pay-As-You-Go).
2. **Azure CLI**: Installed locally ([Download Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)). Verify with `az --version`.
3. **Local Git / Terminal**: PowerShell or Bash.

---

## Architecture on Azure

```
[Student / Placement Officer]
           │
           ▼
[Azure App Service: Streamlit Frontend] (Optional Web UI)
           │ HTTP POST /predict
           ▼
[Azure App Service: FastAPI Backend]   <── [model.pkl (Scikit-Learn 1.9.1)]
   (gunicorn + uvicorn workers)
```

---

## Step 1: Login and Create Resource Group

Open your terminal, authenticate with Azure, and create a unified Resource Group:

```bash
# 1. Sign in to your Azure Account in the default web browser
az login

# 2. (Optional) List and set your target subscription ID if you have multiple
az account list --output table
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# 3. Create a Resource Group in Central India (or eastus / westeurope)
az group create --name rg-placement --location centralindia
```

---

## Step 2: Deploy FastAPI Backend to Azure App Service

Navigate into the `backend/` directory and use `az webapp up` to automatically provision an App Service Plan and deploy the code:

```bash
# 1. Change directory to the backend folder
cd d:\gglobal\placement-project\backend

# 2. Deploy to Azure App Service (Choose a unique app name, e.g., placement-api-student101)
az webapp up \
  --name placement-api-student101 \
  --resource-group rg-placement \
  --runtime "PYTHON:3.11" \
  --sku B1
```

> **Note on SKU**:
> - `B1` (Basic) is recommended for fast deployment and consistent custom startup commands without cold-start restrictions.
> - `F1` (Free) can also be used if quota permits.

---

## Step 3: Configure Linux Startup Command

Azure App Service Linux containers for Python use Gunicorn. Configure the container to launch FastAPI via Uvicorn workers:

```bash
# Set the custom startup command
az webapp config set \
  --resource-group rg-placement \
  --name placement-api-student101 \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"
```

Restart the Web App to apply the new configuration:

```bash
az webapp restart --name placement-api-student101 --resource-group rg-placement
```

---

## Step 4: Stream and View Application Logs

If the application takes a minute to initialize, stream the live container logs:

```bash
az webapp log tail --name placement-api-student101 --resource-group rg-placement
```

*Look for:* `Application startup complete` and `Uvicorn running on http://0.0.0.0:8000`.

---

## Step 5: Test the Live Cloud API

Once the app is running, test the endpoints using your browser or curl/Python:

1. **Swagger Interactive Documentation**:
   ```
   https://placement-api-student101.azurewebsites.net/docs
   ```
2. **Health Check Probe**:
   ```
   https://placement-api-student101.azurewebsites.net/health
   ```
3. **Execute Integration Test Suite against Azure**:
   ```bash
   cd d:\gglobal\placement-project
   python tests/test_api.py --url https://placement-api-student101.azurewebsites.net
   ```

---

## Step 6: (Optional) Deploy Streamlit Frontend to Azure App Service

If you also wish to host the interactive Streamlit user interface in the cloud:

```bash
# 1. Navigate to the frontend directory
cd d:\gglobal\placement-project\frontend

# 2. Deploy Streamlit app to a separate App Service
az webapp up \
  --name placement-ui-student101 \
  --resource-group rg-placement \
  --runtime "PYTHON:3.11" \
  --sku B1

# 3. Configure startup command for Streamlit
az webapp config set \
  --resource-group rg-placement \
  --name placement-ui-student101 \
  --startup-file "python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0"

# 4. Set the environment variable pointing to your backend API
az webapp config appsettings set \
  --resource-group rg-placement \
  --name placement-ui-student101 \
  --settings API_URL="https://placement-api-student101.azurewebsites.net"
```

Access the frontend at: `https://placement-ui-student101.azurewebsites.net`

---

## Step 7: Clean Up Azure Resources (Avoid Unwanted Charges!)

After finishing your viva demonstration and taking required screenshots, delete the resource group to immediately stop all billing:

```bash
az group delete --name rg-placement --yes --no-wait
```

---

## Troubleshooting & Common Azure Issues

### 1. `scikit-learn` Version Mismatch
- **Symptoms**: `ModuleNotFoundError: No module named 'sklearn'` or `InconsistentVersionWarning` when deserializing `model.pkl`.
- **Cause**: The model was pickled with a different scikit-learn version than installed on Azure.
- **Fix**: Check `models/metrics.json` (pinned to `scikit-learn==1.9.1`). Ensure `backend/requirements.txt` has the exact same version `scikit-learn==1.9.1`.

### 2. Cold Start on F1 (Free Tier)
- **Symptoms**: First request takes 30-60 seconds or returns HTTP 504 Gateway Timeout.
- **Cause**: Free tier instances spin down after 20 minutes of inactivity.
- **Fix**: Send a `GET /health` request to wake the container, or use `B1` (Basic) plan with `Always On` enabled:
  ```bash
  az webapp config set --resource-group rg-placement --name placement-api-student101 --always-on true
  ```

### 3. HTTP 502 Bad Gateway / Application Error
- **Symptoms**: Azure displays "Application Error: :( An error occurred while processing your request."
- **Diagnosis**: View logs with `az webapp log tail`.
- **Fix**: Often caused by port mismatch or incorrect startup command. Ensure `--bind 0.0.0.0:8000` is present. Azure App Service automatically routes external port 80/443 traffic to port 8000.

### 4. File Not Found (`model.pkl`)
- **Symptoms**: `FileNotFoundError: Model file not found at: .../model.pkl`.
- **Fix**: Verify that `backend/model.pkl` is committed and deployed in the root of the backend folder.
