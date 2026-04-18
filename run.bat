@echo off
title EV Charge Optimizer
echo ========================================
echo   EV Charge Optimizer - Launcher
echo ========================================
echo.

:: Activate virtual environment
call "%~dp0.venv\Scripts\activate.bat"

:: Install dependencies
echo [1/3] Checking dependencies...
pip install -r "%~dp0requirements.txt" --quiet
echo       Done!
echo.

:: Run unit tests
echo [2/3] Running unit tests...
python -m pytest "%~dp0tests" -v
echo.

:: Launch Flask server
echo [3/3] Starting server...
echo       Open http://localhost:5000 in your browser
echo       Press Ctrl+C to stop.
echo.
python "%~dp0server.py"

pause
