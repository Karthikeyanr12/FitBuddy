@echo off
echo Starting FitBuddy Server...
python -m uvicorn app.main:app --reload --port 8000
pause
