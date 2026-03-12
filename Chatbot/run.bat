@echo off
title EduPlus PlaceMate AI

echo ========================================
echo EduPlus PlaceMate AI - Starting...
echo ========================================
echo.

REM -----------------------------
REM Check if virtual environment exists
REM -----------------------------
if not exist "venv_rasa\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

REM -----------------------------
REM Activate virtual environment
REM -----------------------------
call venv_rasa\Scripts\activate.bat

echo Virtual environment activated.
echo.

REM -----------------------------
REM Train model if missing
REM -----------------------------
if not exist "models" (
    echo ========================================
    echo No trained model found. Training now...
    echo ========================================
    echo.
    python -m rasa train
    echo.
)

REM -----------------------------
REM Start Action Server (Port 5055)
REM -----------------------------
echo ========================================
echo Starting Rasa Action Server...
echo ========================================
echo.
start "Rasa Actions" cmd /k "call venv_rasa\Scripts\activate.bat && rasa run actions --port 5055"

timeout /t 5 /nobreak >nul

REM -----------------------------
REM Start Rasa Server (Port 5005)
REM -----------------------------
echo ========================================
echo Starting Rasa Server...
echo ========================================
echo.
start "Rasa Server" cmd /k "call venv_rasa\Scripts\activate.bat && rasa run --enable-api --cors * --model models --port 5005"

timeout /t 8 /nobreak >nul

REM -----------------------------
REM Start Web UI (Port 8000)
REM -----------------------------
echo ========================================
echo Starting Web UI...
echo ========================================
echo.
start "Web UI" cmd /k "python -m http.server 8000 --directory ui"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo SUCCESS! Chatbot is running!
echo ========================================
echo.
echo Rasa Server : http://localhost:5005
echo Action Server : http://localhost:5055
echo Web UI : http://localhost:8000
echo.
echo Opening browser...
timeout /t 2 >nul
start http://localhost:8000

pause