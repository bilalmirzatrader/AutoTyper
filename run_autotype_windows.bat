@echo off
title Auto Type - Windows Edition
echo Starting Auto Type - Windows Edition...
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

REM Check Python version
python --version 2>&1 | findstr /i /c:"Python 3" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: You might be using an outdated Python version.
    echo Auto Type works best with Python 3.7 or higher.
    echo.
    timeout /t 3 >nul
)

REM Check if virtual environment exists
IF EXIST venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment not found.
    echo Creating new virtual environment...
    python -m venv venv
    
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment. Try installing it manually:
        echo python -m pip install virtualenv
        echo python -m virtualenv venv
        echo.
        echo Press any key to exit...
        pause > nul
        exit /b 1
    )
    
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements_windows.txt
)

echo.
echo Running Auto Type - Windows Edition...
echo.
echo TIP: For best results, make sure to:
echo  - Run as Administrator (right-click, Run as Administrator)
echo  - Set position carefully by clicking directly where you want to type
echo  - Allow a moment after clicking before typing starts
echo.
timeout /t 3 >nul

python auto_type_windows.py

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running Auto Type.
    echo.
    echo Troubleshooting tips:
    echo 1. Make sure you have administrator privileges
    echo 2. Try reinstalling dependencies with: pip install -r requirements_windows.txt --force-reinstall
    echo 3. If you have issues with pywin32, try: python -m pip install --upgrade pywin32
    echo.
    echo Press any key to exit...
    pause > nul
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat
