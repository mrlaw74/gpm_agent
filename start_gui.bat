@echo off
REM GPM-Login Automation GUI Launcher for Windows
REM Author: mrlaw74
REM Date: July 20, 2025

title GPM-Login Automation GUI Launcher

echo.
echo =================================================
echo  GPM-Login Automation GUI Launcher
echo =================================================
echo  Author: mrlaw74
echo  Version: 1.1.0
echo  Date: July 20, 2025
echo =================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.9 or higher is required
    echo Current version:
    python --version
    echo.
    pause
    exit /b 1
)

echo Python version OK
echo.

REM Check if required files exist
echo Checking project files...
if not exist "gpm_automation_gui.py" (
    echo ERROR: gpm_automation_gui.py not found
    echo Please ensure all project files are in the same directory
    pause
    exit /b 1
)

if not exist "launch_gui.py" (
    echo ERROR: launch_gui.py not found
    echo Please ensure all project files are in the same directory
    pause
    exit /b 1
)

echo All project files found
echo.

REM Launch the application
echo Launching GPM-Login Automation GUI...
echo.
echo ^>^>^> You can close this window once the GUI opens ^<^<^<
echo.

python launch_gui.py

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo =================================================
    echo ERROR: Failed to launch the GUI application
    echo =================================================
    echo.
    echo Possible solutions:
    echo 1. Ensure GPM-Login is installed and running
    echo 2. Check that all project files are present
    echo 3. Try running: python launch_gui.py
    echo 4. Check the console output above for error details
    echo.
    pause
) else (
    echo.
    echo GUI application closed successfully
)

echo.
pause
