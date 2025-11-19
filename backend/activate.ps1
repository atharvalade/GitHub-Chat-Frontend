# Virtual Environment Activation Script for PowerShell
# Run this script: .\activate.ps1

Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

Write-Host "`nVirtual environment activated! ✅" -ForegroundColor Green
Write-Host "You can now run:" -ForegroundColor Cyan
Write-Host "  - uvicorn main:app --reload  (to start the server)" -ForegroundColor Yellow
Write-Host "  - python main.py             (to test the application)" -ForegroundColor Yellow
Write-Host "  - python test_api.py         (to run API tests)" -ForegroundColor Yellow
Write-Host "  - deactivate                 (to exit virtual environment)`n" -ForegroundColor Yellow

