@echo off
REM Game Folder Renamer - Startup Script for Windows
REM This script checks dependencies and starts the Streamlit app

echo.
echo Game Folder Renamer - Starting...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.11 or higher from https://www.python.org
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% found

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo Dependencies already installed
)

echo.
echo Starting Streamlit app...
echo    The app will open in your browser at http://localhost:8501
echo.
echo    Press Ctrl+C to stop the server
echo.

REM Run the Streamlit app
streamlit run app.py
