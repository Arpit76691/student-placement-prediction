# Restore Instructions

To completely revert any frontend UI redesign changes and restore the original working frontend:

### PowerShell:
```powershell
# 1. Restore the original frontend/app.py from backup
Copy-Item -Path "backup_before_ui_redesign\frontend\app.py" -Destination "frontend\app.py" -Force

# 2. Remove any newly created Streamlit config file (if created in root or frontend)
if (Test-Path ".streamlit\config.toml") { Remove-Item ".streamlit\config.toml" -Force }
if (Test-Path "frontend\.streamlit\config.toml") { Remove-Item "frontend\.streamlit\config.toml" -Force }

# 3. (Optional) Remove newly captured UI screenshots if needed
if (Test-Path "screenshots\ui_home.png") { Remove-Item "screenshots\ui_home.png" -Force }
if (Test-Path "screenshots\ui_result.png") { Remove-Item "screenshots\ui_result.png" -Force }
```

### Bash / Linux / macOS:
```bash
cp backup_before_ui_redesign/frontend/app.py frontend/app.py
rm -f .streamlit/config.toml frontend/.streamlit/config.toml
rm -f screenshots/ui_home.png screenshots/ui_result.png
```

The backup snapshot is preserved in `backup_before_ui_redesign/`.
