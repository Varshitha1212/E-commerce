@echo off
REM E-Commerce Analytics Platform - Quick Start Script
REM This script starts the web application

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  E-Commerce Customer Analytics Platform              ║
echo ║  Starting Web Application...                          ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Change to correct directory
cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies if needed
echo Installing dependencies...
pip install -q flask flask-cors pandas numpy matplotlib seaborn scikit-learn

REM Check if data exists
if not exist "ecommerce_data.csv" (
    echo Generating sample data...
    python generate_data.py
)

REM Start the application
echo.
echo ✅ Starting Flask Application...
echo.
echo 🌐 Dashboard available at: http://localhost:5000
echo 📊 API available at: http://localhost:5000/api
echo ✅ Health check: http://localhost:5000/health
echo.
echo Press CTRL+C to stop the server
echo.

python app.py

pause
