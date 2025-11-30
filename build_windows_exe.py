"""
Auto Type Windows - Build Script
This script creates an executable (.exe) file for the Auto Type Windows application
using PyInstaller.
"""
import os
import sys
import shutil
import subprocess
import platform

# Make sure we're generating for Windows
if not (platform.system() == "Windows" or "--force" in sys.argv):
    print("This build script is intended for Windows.")
    print("If you're cross-compiling or want to proceed anyway, use --force")
    sys.exit(1)

print("=== Auto Type - Windows EXE Build Script ===")

# Check if PyInstaller is installed
try:
    import PyInstaller
    print("✓ PyInstaller is installed")
except ImportError:
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller installed successfully")

# Define paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_PATH, "auto_type_windows.py")
DIST_PATH = os.path.join(SCRIPT_PATH, "dist")
BUILD_PATH = os.path.join(SCRIPT_PATH, "build")
ICON_PATH = os.path.join(SCRIPT_PATH, "icon.ico")

# Create icon file if it doesn't exist
if not os.path.exists(ICON_PATH):
    print("Icon file not found. Creating a placeholder icon...")
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple colored square icon
        img = Image.new('RGB', (256, 256), color=(137, 180, 250))
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [(50, 50), (206, 206)],
            fill=(30, 30, 46)
        )
        img.save(ICON_PATH)
        print("✓ Created placeholder icon")
    except Exception as e:
        print(f"Failed to create icon: {e}")
        print("Continuing without an icon...")

# Clean up any previous build files
print("Cleaning up previous build files...")
if os.path.exists(DIST_PATH):
    shutil.rmtree(DIST_PATH)
if os.path.exists(BUILD_PATH):
    shutil.rmtree(BUILD_PATH)
if os.path.exists(os.path.join(SCRIPT_PATH, "auto_type_windows.spec")):
    os.remove(os.path.join(SCRIPT_PATH, "auto_type_windows.spec"))

# Build the executable
print("\nBuilding Auto Type Windows executable...")
print("This may take a few minutes...\n")

pyinstaller_command = [
    "pyinstaller",
    "--name=AutoType-Windows",
    "--onefile",  # Create a single executable file
    "--windowed",  # Don't show console window when app runs
    f"--icon={ICON_PATH}" if os.path.exists(ICON_PATH) else "",
    "--noupx",  # Skip UPX compression for better compatibility
    "--clean",  # Clean PyInstaller cache
    # Add all required packages
    "--hidden-import=customtkinter",
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    "--hidden-import=pyautogui",
    "--hidden-import=win32api",
    "--hidden-import=win32con",
    "--hidden-import=win32gui",
    "--hidden-import=requests",
    "--hidden-import=json",
    MAIN_SCRIPT
]

# Remove empty arguments
pyinstaller_command = [arg for arg in pyinstaller_command if arg]

try:
    # Run PyInstaller
    subprocess.check_call(pyinstaller_command)
    print("\n✓ Build successful!")
    
    # Check if the executable was created
    exe_path = os.path.join(DIST_PATH, "AutoType-Windows.exe")
    if os.path.exists(exe_path):
        print(f"\nExecutable created at: {exe_path}")
        
        # Create a launcher batch file
        launcher_path = os.path.join(SCRIPT_PATH, "Launch_AutoType.bat")
        with open(launcher_path, "w") as f:
            f.write('@echo off\n')
            f.write('echo Starting Auto Type Windows...\n')
            f.write('start "" "%~dp0dist\\AutoType-Windows.exe"\n')
        print(f"Launcher batch file created at: {launcher_path}")
        
        # Create a README for the executable
        readme_path = os.path.join(SCRIPT_PATH, "README_EXECUTABLE.txt")
        with open(readme_path, "w") as f:
            f.write("Auto Type - Windows Executable\n")
            f.write("===========================\n\n")
            f.write("This folder contains the executable version of Auto Type for Windows.\n\n")
            f.write("Usage:\n")
            f.write("1. Either double-click on 'dist\\AutoType-Windows.exe' directly\n")
            f.write("2. Or use the 'Launch_AutoType.bat' file for easier launching\n\n")
            f.write("Note: When running for the first time, Windows might show a security warning.\n")
            f.write("This is normal for non-signed executables. Click 'More info' and then 'Run anyway'\n")
            f.write("to proceed.\n\n")
            f.write("For best results, run as Administrator (right-click -> Run as Administrator)\n")
        print(f"README created at: {readme_path}")
        
    else:
        print("Error: Executable file not found. Build might have failed.")
        
except subprocess.CalledProcessError as e:
    print(f"\nError during build: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure all dependencies are installed: pip install -r requirements_windows.txt")
    print("2. Try running PyInstaller manually: pyinstaller --onefile auto_type_windows.py")
    print("3. Check for any import errors in your application")
    sys.exit(1)

print("\nBuild completed!")
