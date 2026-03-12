@echo off
REM EduPlus PlaceMate AI - Setup Script
REM Run this ONCE to set up the project
REM Fixed for multi-Python Windows systems

echo ========================================
echo EduPlus PlaceMate AI - Setup
echo ========================================
echo.

REM ===== STEP 1: Check Python 3.10 =====
py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10 not found!
    echo.
    echo Please install Python 3.10 from:
    echo https://www.python.org/downloads/release/python-3100/
    echo.
    echo After installing, verify with: py -0
    pause
    exit /b 1
)

echo [OK] Python 3.10 detected

REM ===== STEP 2: Remove old venv if exists =====
if exist "venv_rasa" (
    echo Removing old virtual environment...
    rmdir /s /q venv_rasa
)

echo [1/4] Creating virtual environment using Python 3.10...
py -3.10 -m venv venv_rasa
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv_rasa\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Training Rasa model...
python -m rasa train
if errorlevel 1 (
    echo [ERROR] Failed to train model
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Setup complete!
echo ========================================
echo.
echo To run the chatbot:
echo 1. Open two terminals
echo 2. Terminal 1:
echo    venv_rasa\Scripts\activate.bat ^&^& python -m rasa run actions
echo 3. Terminal 2:
echo    venv_rasa\Scripts\activate.bat ^&^& rasa shell
echo.
pause