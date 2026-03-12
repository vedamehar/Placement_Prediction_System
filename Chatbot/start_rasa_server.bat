@echo off
REM ========================================
REM EduPlus PlaceMate AI - HTTP Server Mode
REM Starts Rasa as REST API + Action Server
REM ========================================

echo.
echo ========================================
echo EduPlus Chatbot - Starting HTTP Server
echo ========================================
echo.

REM Check virtual environment
if not exist "venv_rasa\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_improved.bat first.
    pause
    exit /b 1
)

echo [1] Activating virtual environment...
call venv_rasa\Scripts\activate.bat

REM Check trained model
if not exist "models" (
    echo.
    echo [WARN] No trained model found. Training now...
    python -m rasa train
    if %errorlevel% neq 0 (
        echo [ERROR] Training failed
        pause
        exit /b 1
    )
    echo [OK] Model trained
    echo.
)

echo [2] Starting Rasa Action Server on port 5055...
start "Rasa Action Server" cmd /k "cd /d %~dp0 && venv_rasa\Scripts\activate.bat && python -m rasa run actions --port 5055"

timeout /t 3 /nobreak > nul

echo [3] Starting Rasa HTTP Server on port 5005...
echo      Endpoint: http://localhost:5005/webhooks/rest/webhook
echo.
echo ========================================
echo Chatbot REST API is starting...
echo React frontend will connect automatically.
echo Press Ctrl+C to stop.
echo ========================================
echo.

python -m rasa run --enable-api --cors "*" --port 5005

echo.
echo Chatbot server stopped.
pause
