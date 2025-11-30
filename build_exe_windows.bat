@echo off
title Build Auto Type Windows EXE
echo ===== Auto Type - Windows Executable Builder =====
echo.
echo This script will create a standalone .exe file for Auto Type Windows.
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

REM Check if virtual environment exists
IF EXIST venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment not found.
    echo Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -r requirements_windows.txt
)

REM Install PyInstaller if not already installed
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Starting build process...
echo This may take a few minutes...
echo.

REM Run the build script
python build_windows_exe.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed! See error message above.
    echo.
    echo Troubleshooting tips:
    echo 1. Make sure all dependencies are properly installed
    echo 2. Run 'pip install -r requirements_windows.txt' to reinstall dependencies
    echo 3. Check for any error messages
    echo.
) else (
    echo.
    echo Build completed successfully!
    echo.
    echo The executable file is located in the 'dist' folder.
    echo You can now distribute 'dist\AutoType-Windows.exe' to any Windows computer.
    echo.
)

echo Press any key to exit...
pause > nul

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat
