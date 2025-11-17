#!/bin/bash

# Game Folder Renamer - Startup Script
# This script checks dependencies and starts the Streamlit app

echo "🎮 Game Folder Renamer - Starting..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.11 or higher from https://www.python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"

# Virtual environment directory
VENV_DIR="venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "   Please ensure python3-venv is installed: sudo apt install python3-venv"
        exit 1
    fi
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if streamlit is installed in the virtual environment
if ! python -c "import streamlit" &> /dev/null; then
    echo "📦 Installing dependencies in virtual environment..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed successfully"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "🚀 Starting Streamlit app..."
echo "   The app will open in your browser at http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Run the Streamlit app
streamlit run app.py
