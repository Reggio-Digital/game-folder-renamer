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

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip is not installed"
    echo "Please install pip"
    exit 1
fi

# Check if streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
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
