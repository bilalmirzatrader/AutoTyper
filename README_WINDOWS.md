# Auto Type - Windows Edition

A modern Windows application that simulates realistic human typing at any screen position, optimized specifically for Windows operating systems.

## Features

- **Point-and-click position selection** - Click anywhere on screen to set the typing position
- **Modern and intuitive interface** - Using CustomTkinter for a clean, modern UI
- **Windows-specific optimizations** - Uses Windows API for improved window focusing and input handling
- **Realistic human-like typing** - Randomized delays between keystrokes with special handling for punctuation
- **Customizable typing speed** - Control typing speed in WPM (Words Per Minute)
- **5-second countdown** - Get ready before typing starts
- **Administrator mode detection** - Warns when not running as administrator (needed for typing into elevated applications)

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):

```batch
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```batch
pip install -r requirements_windows.txt
```

## System Requirements

- **Windows 10 or 11**
- **Python 3.7+**
- **Administrator privileges** recommended for typing into applications with elevated permissions

## Usage

1. Run the application:

```batch
python auto_type_windows.py
```

2. **Click "Set Position"** and then click anywhere on your screen to select where you want to type
3. **Enter text** in the text box that you want to be typed
4. **Adjust the typing speed** using the slider
5. **Click "Start Typing"** to begin the process
6. The app will countdown, minimize itself, and then begin typing at your selected position

## Windows-Specific Options

- **Use Windows-specific window focus method**: Uses the Windows API to properly focus the target window before typing (recommended)
- **Administrator mode**: Run the app as administrator to type into elevated applications

## Troubleshooting

- **Text not typing into admin applications?** Run Auto Type as administrator
- **Focus issues?** Make sure "Use Windows-specific window focus method" is checked
- **Performance issues?** Try reducing the typing speed (WPM)

## License

This project is licensed under the MIT License.
