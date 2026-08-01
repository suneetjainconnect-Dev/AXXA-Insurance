@echo off
echo CertifyAI-Pro - Starting Setup...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python detected...
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
) else (
    echo [2/5] Virtual environment already exists...
    echo.
)

REM Activate virtual environment and install dependencies
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [4/5] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo Try running: pip install -r requirements.txt
) else (
    echo Dependencies installed successfully!
)

echo.
echo [5/5] Starting application...
echo.
echo Application will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Set environment variables (replace with your actual values)
set GOOGLE_CLIENT_ID=your-google-client-id-here
set GOOGLE_CLIENT_SECRET=your-google-client-secret-here

python app.py

REM If virtual environment was created by this script, deactivate it
if exist "venv\Scripts\activate.bat" (
    deactivate
)