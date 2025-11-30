# Auto Type Windows - Executable Version

## Installation

The Auto Type application for Windows is available as a standalone executable. You don't need to install Python or any dependencies to run it.

### How to Run the Executable

1. **Download** the `AutoType-Windows.exe` file from the `dist` folder
2. **Double-click** the executable to run the application
3. For best results, **run as administrator** (right-click and select "Run as administrator")

### Security Warnings

When you run the executable for the first time, Windows might show security warnings because the application isn't signed with a certificate. This is normal for free/open-source applications.

To run the application:
1. Click on **"More info"** in the warning dialog
2. Click on **"Run anyway"**

### Building the Executable Yourself

If you prefer to build the executable from source:

1. Ensure you have Python 3.7 or higher installed
2. Run `build_exe_windows.bat` to create the executable
3. The resulting exe will be in the `dist` folder

## Using Auto Type

1. Click **"Set Position"** and click anywhere on your screen where you want text to be typed
2. Enter the text you want to type in the text box
3. Adjust the typing speed with the slider (higher WPM = faster typing)
4. Click **"Start Typing"** to begin the typing process
5. The app will minimize and start typing after a 5-second countdown
6. Use the **"Stop"** button to immediately halt typing

## Troubleshooting

**If typing doesn't work:**
- Make sure to run the application as administrator
- Ensure no application is blocking input simulation
- Try clicking the target area manually before typing starts

**If the application won't start:**
- Install the Visual C++ Redistributable for Visual Studio 2015-2019
- Ensure Windows Defender isn't blocking the application
- Try running in compatibility mode for Windows 10

## Technical Information

This executable was created using PyInstaller and contains:
- Auto Type Windows application
- Python interpreter
- All required libraries and dependencies

No installation is required, and the application doesn't modify system settings or the registry.
