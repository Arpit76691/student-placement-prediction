#!/bin/bash
# Startup script for Azure App Service (Linux)
# Launches FastAPI using Gunicorn with Uvicorn worker processes
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
