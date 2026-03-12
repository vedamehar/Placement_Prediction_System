#!/bin/bash
# EduPlus PlaceMate AI - Setup Script

echo "========================================"
echo "EduPlus PlaceMate AI - Setup"
echo "========================================"
echo

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '3\.(8|9|10)')
if [ -z "$python_version" ]; then
    echo "[ERROR] Python 3.8, 3.9, or 3.10 required!"
    echo "Current version:"
    python3 --version
    echo
    echo "Please install Python 3.10"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv_rasa
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv_rasa/bin/activate

echo "[3/4] Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[4/4] Training Rasa model..."
python -m rasa train
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to train model"
    exit 1
fi

echo
echo "========================================"
echo "SUCCESS! Setup complete!"
echo "========================================"
echo
echo "To run the chatbot, execute: ./run.sh"
echo
