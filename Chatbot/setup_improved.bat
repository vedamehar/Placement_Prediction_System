@echo off
REM ========================================
REM EduPlus PlaceMate AI - Smart Setup Script
REM ========================================
REM This script sets up the Rasa chatbot project
REM Requirement: Python 3.10 (or 3.8/3.9)

setlocal enabledelayedexpansion

echo.
echo ========================================
echo EduPlus PlaceMate AI - Setup Wizard
echo ========================================
echo.

REM ===== STEP 1: Check Python Version =====
echo [STEP 1] Checking Python version...
echo.

set PYTHON_CMD=
set PYTHON_VERSION=

REM Try Python 3.10 using Python Launcher
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.10
    for /f "tokens=2" %%i in ('py -3.10 --version') do set PYTHON_VERSION=%%i
    echo [OK] Found Python 3.10: !PYTHON_VERSION!
    goto PYTHON_FOUND
)

REM Try Python 3.9
py -3.9 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.9
    for /f "tokens=2" %%i in ('py -3.9 --version') do set PYTHON_VERSION=%%i
    echo [OK] Found Python 3.9: !PYTHON_VERSION!
    goto PYTHON_FOUND
)

REM Try Python 3.8
py -3.8 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.8
    for /f "tokens=2" %%i in ('py -3.8 --version') do set PYTHON_VERSION=%%i
    echo [OK] Found Python 3.8: !PYTHON_VERSION!
    goto PYTHON_FOUND
)

echo [ERROR] Python 3.8, 3.9, or 3.10 not found!
echo.
echo Required: Python 3.8, 3.9, or 3.10 (Rasa 3.6.13 requirement)
echo.
echo SOLUTION:
echo 1. Install Python 3.10 from: https://www.python.org/downloads/release/python-3100/
echo 2. Make sure Python Launcher is installed
echo 3. Run: py -0  (to verify installation)
echo 4. Run this script again
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [OK] Using Python: !PYTHON_VERSION! with command: !PYTHON_CMD!
echo.

REM ===== STEP 2: Create Virtual Environment =====
echo [STEP 2] Creating virtual environment...

if exist "venv_rasa" (
    echo [WARN] Virtual environment already exists, removing...
    rmdir /s /q venv_rasa
)

!PYTHON_CMD! -m venv venv_rasa
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM ===== STEP 3: Activate Virtual Environment =====
echo [STEP 3] Activating virtual environment...
call venv_rasa\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM ===== STEP 4: Upgrade pip =====
echo [STEP 4] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel --quiet
echo [OK] pip tools upgraded
echo.

REM ===== STEP 5: Install Dependencies =====
echo [STEP 5] Installing Rasa and dependencies...
echo Installing: rasa 3.6.13, rasa-sdk 3.6.1, pandas, fuzzywuzzy, python-Levenshtein
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo - Ensure internet connection
    echo - Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM ===== STEP 6: Validate Rasa Install =====
echo [STEP 6] Validating Rasa installation...
python -m rasa --version
if %errorlevel% neq 0 (
    echo [ERROR] Rasa validation failed
    pause
    exit /b 1
)
echo [OK] Rasa successfully installed
echo.

REM ===== STEP 7: Validate Project Structure =====
echo [STEP 7] Validating Rasa project structure...
python -m rasa data validate
echo [OK] Project structure validated
echo.

REM ===== STEP 8: Check CSV Data =====
echo [STEP 8] Checking data files...
if not exist "data\company_placement_db.csv" (
    echo [ERROR] company_placement_db.csv not found
    pause
    exit /b 1
)
echo [OK] CSV data file found
echo.

REM ===== STEP 9: Train Model =====
echo [STEP 9] Training Rasa model (this may take 2-5 minutes)...
echo.
python -m rasa train
if %errorlevel% neq 0 (
    echo [ERROR] Model training failed
    pause
    exit /b 1
)
echo [OK] Model trained successfully
echo.

echo ========================================
echo SUCCESS! Setup Complete
echo ========================================
echo.
echo Next Steps:
echo 1. Run the chatbot with: run.bat
echo 2. Or manually:
echo    - Terminal 1: venv_rasa\Scripts\activate.bat ^&^& python -m rasa run actions
echo    - Terminal 2: venv_rasa\Scripts\activate.bat ^&^& rasa shell
echo.
echo To deactivate venv: deactivate
echo.
pause
exit /b 0