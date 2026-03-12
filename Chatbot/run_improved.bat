@echo off
REM ========================================
REM EduPlus PlaceMate AI - Improved Run Script
REM ========================================
REM Starts all necessary components of the chatbot

echo.
echo ========================================
echo EduPlus PlaceMate AI - Starting System
echo ========================================
echo.

REM Check if venv exists
if not exist "venv_rasa\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup_improved.bat first to initialize the environment
    echo.
    pause
    exit /b 1
)

echo [1] Activating virtual environment...
call venv_rasa\Scripts\activate.bat

REM Check if model exists
if not exist "models" (
    echo.
    echo [WARN] No trained model found
    echo [ACTION] Training model now (this may take a few minutes)...
    echo.
    python -m rasa train
    if %errorlevel% neq 0 (
        echo [ERROR] Model training failed
        pause
        exit /b 1
    )
    echo [OK] Model trained successfully
    echo.
)

echo [2] Starting Rasa Action Server...
echo Opening new window for action server...
echo.
start "Rasa Actions" cmd /k "venv_rasa\Scripts\activate.bat && python -m rasa run actions --enable-api --cors *"

timeout /t 3 /nobreak

echo [3] Starting Rasa Chatbot Shell...
echo.
echo ========================================
echo Chatbot Ready!
echo ========================================
echo.
echo Try these commands:
echo   - hi
echo   - what's Google's package?
echo   - list tier-1 companies
echo   - what should I prepare for Microsoft?
echo   - goodbye
echo.
python -m rasa shell

echo.
echo ========================================
echo Chatbot Session Ended
echo ========================================
echo.
