#!/bin/bash
# EduPlus PlaceMate AI - Linux/Mac Run Script

echo "========================================"
echo "EduPlus PlaceMate AI - Starting..."
echo "========================================"
echo

# Check if venv exists
if [ ! -f "venv_rasa/bin/python" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv_rasa/bin/activate

# Check if model exists
if [ ! -d "models" ]; then
    echo "[INFO] No trained model found. Training now..."
    python -m rasa train
    echo
fi

echo "========================================"
echo "Starting Rasa Action Server..."
echo "========================================"
echo
gnome-terminal -- bash -c "source venv_rasa/bin/activate && python -m rasa run actions; exec bash" 2>/dev/null || \
xterm -e "source venv_rasa/bin/activate && python -m rasa run actions" 2>/dev/null || \
python -m rasa run actions &

sleep 3

echo "========================================"
echo "Starting Rasa Server..."
echo "========================================"
echo
gnome-terminal -- bash -c "source venv_rasa/bin/activate && python -m rasa run --enable-api --cors '*'; exec bash" 2>/dev/null || \
xterm -e "source venv_rasa/bin/activate && python -m rasa run --enable-api --cors '*'" 2>/dev/null || \
python -m rasa run --enable-api --cors '*' &

sleep 3

echo "========================================"
echo "Starting Web UI..."
echo "========================================"
echo
gnome-terminal -- bash -c "source venv_rasa/bin/activate && python -m http.server 8000 --directory ui; exec bash" 2>/dev/null || \
xterm -e "source venv_rasa/bin/activate && python -m http.server 8000 --directory ui" 2>/dev/null || \
python -m http.server 8000 --directory ui &

sleep 2

echo
echo "========================================"
echo "SUCCESS! Chatbot is running!"
echo "========================================"
echo
echo "Web UI: http://localhost:8000"
echo
echo "Press Ctrl+C to stop all servers"
wait
