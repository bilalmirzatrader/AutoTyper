import threading
import time
import random
import platform
import os
import ctypes
import json
from dataclasses import dataclass
from typing import Optional, Tuple, Callable

# Try to import requests for password validation
try:
    import requests
except ImportError as e:
    raise ImportError(
        "Missing dependency 'requests'. Install with: pip install requests"
    ) from e

# Make sure we're running on Windows
if platform.system() != "Windows":
    raise RuntimeError("This application is designed to run only on Windows systems.")

# Modern UI toolkit
try:
    import customtkinter as ctk
    from customtkinter import ThemeManager
except ImportError as e:
    raise ImportError(
        "Missing dependency 'customtkinter'. Install with: pip install customtkinter"
    ) from e

# Standard Tkinter for some components
try:
    import tkinter as tk
    from tkinter import messagebox
except Exception as e:
    raise RuntimeError("Tkinter is required but not available.")

# PyAutoGUI for keyboard and mouse control
try:
    import pyautogui
    
    # Prevent accidental edge triggering
    pyautogui.FAILSAFE = False
    
    # Make PyAutoGUI operations faster with minimal pauses
    pyautogui.PAUSE = 0.01
    
except ImportError as e:
    raise ImportError(
        "Missing dependency 'pyautogui'. Install with: pip install pyautogui"
    ) from e

# Import PIL for image handling
try:
    from PIL import Image, ImageTk
except ImportError:
    raise ImportError(
        "Missing dependency 'pillow'. Install with: pip install pillow"
    )

# Windows-specific imports
try:
    import win32api
    import win32con
    import win32gui
    HAVE_WIN32API = True
except ImportError:
    print("Warning: pywin32 not found. Some Windows-specific features will be disabled.")
    print("Install with: pip install pywin32")
    HAVE_WIN32API = False

@dataclass
class TypingConfig:
    """Configuration for typing behavior"""
    wpm: float = 40.0           # words per minute (5 chars per word convention)
    humanize: bool = True       # Add human-like randomness to typing
    countdown_sec: int = 5      # Countdown before starting to type
    windows_focus: bool = True  # Use Windows-specific focus methods
    
    
class AppColors:
    """Color scheme for the application"""
    BG_COLOR = "#1E1E2E"  # Dark background
    PRIMARY = "#89B4FA"   # Blue accent
    SECONDARY = "#F5C2E7" # Pink accent
    TEXT = "#CDD6F4"      # Light text
    SUCCESS = "#A6E3A1"   # Green for success
    WARNING = "#FAB387"   # Orange for warnings
    ERROR = "#F38BA8"     # Red for errors
    SURFACE = "#313244"   # Surface color for elements


def is_admin():
    """Check if the app is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
        
        
def validate_password(password):
    """Validates the password against the one stored in the pastebin URL"""
    url = "https://pastebin.com/raw/eKiZCNbX"
    
    try:
        # Try to fetch the password from Pastebin with a timeout
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            try:
                # Try to parse the JSON response
                data = json.loads(response.text)
                correct_password = data.get("access_code", "")
                if not correct_password:
                    # If the access_code key is missing or empty
                    print("Error: Missing 'access_code' in the password data")
                    messagebox.showerror(
                        "Authentication Error",
                        "The password verification data is invalid. Please contact the administrator."
                    )
                    return False
                    
                # Compare the passwords
                return password == correct_password
            except json.JSONDecodeError:
                # If the response is not valid JSON
                print("Error: Invalid JSON in password data")
                messagebox.showerror(
                    "Authentication Error",
                    "The password verification data is corrupted. Please contact the administrator."
                )
                return False
        else:
            # If the server returned an error code
            print(f"Server error: HTTP {response.status_code}")
            messagebox.showerror(
                "Authentication Error",
                f"Could not connect to the authentication server (HTTP {response.status_code}).\n"
                "Please check your internet connection and try again."
            )
            return False
    except requests.exceptions.Timeout:
        # If the request timed out
        print("Error: Request timed out")
        messagebox.showerror(
            "Authentication Error",
            "Connection to the authentication server timed out.\n"
            "Please check your internet connection and try again."
        )
        return False
    except requests.exceptions.ConnectionError:
        # If there was a connection error
        print("Error: Connection error")
        messagebox.showerror(
            "Authentication Error",
            "Could not connect to the authentication server.\n"
            "Please check your internet connection and try again."
        )
        return False
    except Exception as e:
        # Any other unexpected errors
        print(f"Unexpected error: {str(e)}")
        messagebox.showerror(
            "Authentication Error",
            f"An unexpected error occurred: {str(e)}\n"
            "Please contact the administrator."
        )
        return False


def human_typing(text: str, wpm: float, callback: Callable[[str], None] = None, 
             stop_event: threading.Event = None) -> None:
    """
    Type text with human-like timing variations, optimized for Windows.
    
    Args:
        text: Text to type
        wpm: Words per minute (based on 5 chars = 1 word)
        callback: Optional callback for status updates
        stop_event: Event to check for stop requests
    """
    if not text:
        return
        
    # Check for stop request
    if stop_event and stop_event.is_set():
        if callback:
            callback("Typing stopped")
        return
        
    # Base timing calculation - with speed boost
    chars_per_second = (wpm * 6.0) / 60.0  # Increased from 5.0 to 6.0 for speed boost
    base_delay = 1.0 / chars_per_second
    
    # Batch size for faster typing (Windows optimization)
    batch_size = 3  # Process more characters at once for faster typing
    
    # Type character by character
    i = 0
    while i < len(text):
        # Check for stop request
        if stop_event and stop_event.is_set():
            if callback:
                callback("Typing stopped")
            return
            
        # Update status periodically
        if callback and i % 10 == 0:
            callback(f"Typing character {i+1}/{len(text)}")
        
        try:
            # Get current character
            char = text[i]
            
            # Check for stop request again
            if stop_event and stop_event.is_set():
                if callback:
                    callback("Typing stopped")
                return
                
            # Handle special characters separately
            if char in ["\n", "\t", "\r"]:
                if char == "\n" or char == "\r":
                    pyautogui.press("enter")
                elif char == "\t":
                    pyautogui.press("tab")
                
                # Apply longer delay after special characters
                delay = calculate_human_delay(base_delay * 2, char)
                time.sleep(delay)
                i += 1
            else:
                # Determine how many regular characters to batch together
                end_idx = min(i + batch_size, len(text))
                while end_idx > i and text[end_idx-1] in ["\n", "\t", "\r"]:
                    end_idx -= 1  # Don't include special chars in batch
                    
                if end_idx > i:
                    # Type the batch of characters
                    chunk = text[i:end_idx]
                    pyautogui.write(chunk, interval=0.01)  # Small interval between keys
                    
                    # Apply human-like delays between batches
                    delay = calculate_human_delay(base_delay, ".")
                    time.sleep(delay)
                    
                    i = end_idx
                else:
                    i += 1  # Shouldn't happen but prevents infinite loop
            
        except Exception as e:
            if callback:
                callback(f"Error typing at position {i}: {str(e)}")
            i += 1  # Move on despite error
            time.sleep(0.5)  # Pause after error
    
    if callback:
        callback("Typing complete")


def calculate_human_delay(base_delay: float, char: str) -> float:
    """Calculate a human-like delay for the given character"""
    # Add reduced randomness (70-120% of base speed) for faster typing
    jitter = random.uniform(0.7, 1.2)
    delay = base_delay * jitter
    
    # Add reduced extra pauses for punctuation and spaces
    if char in {" ", "\t"}:
        delay += random.uniform(0.01, 0.05)  # Reduced delay
    elif char in {",", ".", ";", ":", "-", "—", "?", "!", ")"}:
        delay += random.uniform(0.03, 0.12)  # Reduced delay
    elif char in {"\n"}:
        delay += random.uniform(0.05, 0.15)  # Reduced delay
        
    return max(0.005, delay)  # Lower minimum delay for faster typing


class AutoTyperApp(ctk.CTk):
    """Modern UI for auto typing application using CustomTkinter"""
    
    def __init__(self):
        super().__init__()
        
        # Configure the window
        self.title("Auto Type - Windows Edition")
        self.geometry("900x700")  # Larger default window size
        self.minsize(800, 600)    # Larger minimum window size
        
        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Set Windows-specific icon if available
        try:
            self.iconbitmap(default=os.path.join(os.path.dirname(__file__), "icon.ico"))
        except:
            pass  # Skip if icon isn't available
        
        # App state
        self.cursor_position = None
        self.stop_event = threading.Event()
        self.typing_thread = None
        
        # Windows-specific flags
        self.admin_mode = is_admin()
        
        # Build the UI
        self._build_ui()
        
    def _build_ui(self):
        """Create the user interface"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # ===== Header =====
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_text = "Auto Type - Windows Edition"
        if self.admin_mode:
            title_text += " (Admin)"
            
        ctk.CTkLabel(
            header_frame, 
            text=title_text, 
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=15)
        
        # ===== Instructions =====
        instructions = (
            "1. Click 'Set Position' and then click anywhere on screen to select typing position\n"
            "2. Enter text and set typing speed (WPM)\n"
            "3. Click 'Start Typing' to begin"
        )
        
        instr_frame = ctk.CTkFrame(self)
        instr_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        instr_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            instr_frame,
            text=instructions,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # ===== Main content area =====
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Position selector
        pos_frame = ctk.CTkFrame(content_frame)
        pos_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        pos_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            pos_frame, 
            text="Cursor Position:",
            width=110,
            anchor="w"
        ).grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")
        
        self.position_var = tk.StringVar(value="Not set")
        pos_label = ctk.CTkLabel(
            pos_frame, 
            textvariable=self.position_var,
            anchor="w"
        )
        pos_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.set_pos_btn = ctk.CTkButton(
            pos_frame,
            text="Set Position",
            command=self.on_set_position,
            width=120,
        )
        self.set_pos_btn.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")
        
        # Text input
        text_label = ctk.CTkLabel(content_frame, text="Text to type:", anchor="w")
        text_label.grid(row=1, column=0, padx=15, pady=(10, 0), sticky="nw")
        
        self.text_box = ctk.CTkTextbox(
            content_frame, 
            wrap="word",
            font=ctk.CTkFont(size=14),  # Slightly larger font
            height=350,  # Much taller text box
        )
        self.text_box.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        
        # ===== Bottom controls =====
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        controls_frame.grid_columnconfigure((0, 1), weight=1)
        controls_frame.grid_columnconfigure(2, weight=2)
        
        # Speed input
        speed_label = ctk.CTkLabel(controls_frame, text="Typing Speed (WPM):", anchor="w")
        speed_label.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
        
        self.speed_var = tk.IntVar(value=80)  # Default to higher speed
        self.speed_slider = ctk.CTkSlider(
            controls_frame, 
            from_=20,      # Higher minimum speed
            to=120,        # Maximum speed of 120 WPM
            number_of_steps=100,
            variable=self.speed_var,
            command=self._update_speed_display
        )
        self.speed_slider.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        self.speed_slider.set(80)  # Default to higher speed
        
        self.speed_display = ctk.CTkLabel(controls_frame, text="40 WPM")
        self.speed_display.grid(row=0, column=2, padx=(5, 15), pady=15, sticky="w")
        
        # Windows-specific options
        win_frame = ctk.CTkFrame(self)
        win_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        win_frame.grid_columnconfigure(1, weight=1)
        
        # Advanced Windows Options
        self.win_focus_var = tk.BooleanVar(value=True)
        win_focus_check = ctk.CTkCheckBox(
            win_frame,
            text="Use Windows-specific window focus method",
            variable=self.win_focus_var,
            onvalue=True,
            offvalue=False
        )
        win_focus_check.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Status area
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        status_frame.grid(row=5, column=0, sticky="ew", padx=0, pady=(0, 0))
        status_frame.grid_propagate(False)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.status_var,
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=15, sticky="w")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Start Typing",
            command=self.on_start,
            fg_color=AppColors.SUCCESS,
            hover_color="#85c190",  # Darker green
            text_color="#212121",  # Dark gray for better contrast
            height=35
        )
        self.start_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop",
            command=self.on_stop,
            fg_color=AppColors.ERROR,
            hover_color="#d47689",  # Darker red
            text_color="white",
            state="disabled",
            height=35
        )
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.quit_btn = ctk.CTkButton(
            btn_frame,
            text="Quit",
            command=self.on_quit,
            height=35
        )
        self.quit_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Show admin status warning if needed
        if not self.admin_mode:
            self.after(1000, lambda: messagebox.showinfo(
                "Non-Admin Mode",
                "Running without administrator privileges.\n"
                "Some applications with elevated privileges might not receive keystrokes."
            ))
    
    def _update_speed_display(self, value):
        """Update the WPM display when slider changes"""
        wpm = int(float(value))
        self.speed_var.set(wpm)
        self.speed_display.configure(text=f"{wpm} WPM")
    
    def on_set_position(self):
        """Start position selection mode"""
        # Already in positioning mode - cancel
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            self.overlay.destroy()
            self.status_var.set("Position selection cancelled")
            self.set_pos_btn.configure(text="Set Position")
            return
            
        # Create an overlay window
        self.status_var.set("Click anywhere on screen to set position...")
        self.set_pos_btn.configure(text="Cancel Selection")

        # Save the current mouse position before opening overlay
        try:
            self.pre_overlay_position = pyautogui.position()
        except:
            self.pre_overlay_position = None
        
        # Show a message to guide the user
        messagebox.showinfo(
            "Set Position",
            "Click at the position where you want the text to be typed.\n"
            "Press ESC to cancel."
        )
        
        # Create a semi-visible overlay (slightly visible for better usability)
        self.overlay = tk.Toplevel(self)
        self.overlay.attributes("-alpha", 0.15)  # Slightly visible so user can see it
        self.overlay.attributes("-topmost", True)
        
        # Make it fullscreen
        self.overlay.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.overlay.overrideredirect(True)  # No window decorations
        
        # Add click handler
        def on_click(event):
            # Get the exact screen coordinates
            x, y = event.x_root, event.y_root
            self.cursor_position = (x, y)
            self.position_var.set(f"({x}, {y})")
            self.status_var.set(f"Position set successfully at ({x}, {y})")
            self.overlay.destroy()
            self.set_pos_btn.configure(text="Set Position")
            
            # Double-check if position was set correctly
            if self.cursor_position:
                messagebox.showinfo(
                    "Position Set",
                    f"Position set successfully at coordinates: ({x}, {y})\n"
                    "Click 'Start Typing' when ready."
                )
            
        # Add escape key handler
        def on_escape(event):
            self.overlay.destroy()
            self.status_var.set("Position selection cancelled")
            self.set_pos_btn.configure(text="Set Position")
            
            # Restore original mouse position if possible
            if self.pre_overlay_position:
                try:
                    pyautogui.moveTo(self.pre_overlay_position[0], self.pre_overlay_position[1], duration=0.2)
                except:
                    pass
            
        self.overlay.bind("<Button-1>", on_click)
        self.overlay.bind("<Escape>", on_escape)
        self.overlay.focus_force()
        
    def windows_set_foreground_window(self, x, y):
        """Windows-specific method to set focus to the window under the given coordinates"""
        if not HAVE_WIN32API:
            return False
            
        try:
            # Get window handle at the position
            hwnd = win32gui.WindowFromPoint((x, y))
            if hwnd:
                # Make sure it's not our own window
                if hwnd != win32gui.FindWindow(None, self.title()):
                    # Try multiple focus methods for better reliability
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.SetActiveWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                    return True
        except Exception as e:
            print(f"Windows focus error: {str(e)}")
            
        return False
        
    def on_start(self):
        """Start typing process"""
        # Check if position is set
        if not self.cursor_position:
            self.show_error("No position set", "Please set a cursor position first.")
            return
            
        # Get the text
        text = self.text_box.get("0.0", "end").strip()
        if not text:
            self.show_error("No text", "Please enter some text to type.")
            return
            
        # Get typing speed
        try:
            wpm = float(self.speed_var.get())
            if wpm <= 0:
                raise ValueError("WPM must be positive")
        except ValueError:
            self.show_error("Invalid speed", "Please set a valid typing speed.")
            return
            
        # Check if already typing
        if self.typing_thread and self.typing_thread.is_alive():
            self.show_error("Already typing", "Typing is already in progress.")
            return
            
        # Create typing config
        config = TypingConfig(
            wpm=wpm, 
            humanize=True, 
            countdown_sec=5,
            windows_focus=self.win_focus_var.get()
        )
        
        # Start typing
        self.start_typing(text, config)
        
    def start_typing(self, text: str, config: TypingConfig):
        """Start the typing process in a separate thread"""
        # Reset stop event
        self.stop_event.clear()
        
        # Update UI
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set("Preparing to type...")
        
        # Show info dialog
        self.withdraw()  # Hide main window temporarily
        messagebox.showinfo(
            "Ready to Type",
            "The app will minimize while typing.\n"
            f"Typing will begin after a {config.countdown_sec} second countdown.\n\n"
            "DO NOT close the app until typing is complete."
        )
        self.deiconify()  # Show main window again
        
        # Start typing thread
        self.typing_thread = threading.Thread(
            target=self._typing_worker,
            args=(text, config),
            daemon=True
        )
        self.typing_thread.start()
        
    def on_stop(self):
        """Stop the typing process"""
        # Set the stop event flag
        self.stop_event.set()
        self.status_var.set("Stopping typing process...")
        
        # Force restore window immediately
        if self.winfo_exists():
            self.deiconify()
            self.lift()  # Bring window to front
            self.focus_force()  # Force focus
        
        # Forcefully terminate the typing thread if it doesn't respond quickly
        if self.typing_thread and self.typing_thread.is_alive():
            # First try to stop gracefully
            self.after(100, self._force_stop_typing)
            
        # Update UI immediately
        self._toggle_buttons(False)
        
    def on_quit(self):
        """Exit the application"""
        if self.typing_thread and self.typing_thread.is_alive():
            if messagebox.askyesno("Confirm Exit", "Typing is in progress. Are you sure you want to quit?"):
                self.stop_event.set()
                self.destroy()
        else:
            self.destroy()
            
    def show_error(self, title: str, message: str):
        """Show an error message box"""
        messagebox.showerror(title, message)
        
    def _update_status(self, status: str):
        """Thread-safe status update"""
        if self.winfo_exists():
            self.after(0, self.status_var.set, status)
            
    def _toggle_buttons(self, typing_active: bool):
        """Thread-safe button state update"""
        def update():
            if typing_active:
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
            else:
                self.start_btn.configure(state="normal") 
                self.stop_btn.configure(state="disabled")
                
        if self.winfo_exists():
            self.after(0, update)
            
    def _check_stop_status(self):
        """Check if typing has stopped and update UI accordingly"""
        if not self.typing_thread or not self.typing_thread.is_alive():
            self._toggle_buttons(False)
            self.status_var.set("Typing stopped")
        elif self.stop_event.is_set():
            # If thread is still alive but stop was requested, check again in a moment
            self.after(500, self._check_stop_status)
            
    def _force_stop_typing(self):
        """Forcefully terminate typing if stop event doesn't work"""
        if self.typing_thread and self.typing_thread.is_alive() and self.stop_event.is_set():
            # Try to interrupt any pyautogui operations
            try:
                # Move mouse to corner to trigger failsafe
                if not pyautogui.FAILSAFE:
                    pyautogui.FAILSAFE = True
                    
                # Reset pyautogui state
                pyautogui.mouseUp()
                pyautogui.keyUp()
                
                # Move mouse to a corner (trigger failsafe)
                screen_width, screen_height = pyautogui.size()
                pyautogui.moveTo(screen_width - 1, 0, duration=0.1)
            except:
                pass
                
            self.status_var.set("Typing stopped")
            self._toggle_buttons(False)
            
    def _typing_worker(self, text: str, config: TypingConfig):
        """Worker thread for typing process"""
        try:
            # Check if stop requested immediately
            if self.stop_event.is_set():
                self._update_status("Stopped")
                self._toggle_buttons(False)
                return
                
            # Countdown - with more frequent stop checks
            for remaining in range(config.countdown_sec, 0, -1):
                if self.stop_event.is_set():
                    self._update_status("Stopped before typing")
                    self._toggle_buttons(False)
                    return
                    
                self._update_status(f"Starting in {remaining} seconds...")
                
                # Check for stop event more frequently (4 times per second)
                for _ in range(4):
                    if self.stop_event.is_set():
                        self._update_status("Stopped before typing")
                        self._toggle_buttons(False)
                        return
                    time.sleep(0.25)
                
            # Minimize application during typing
            if self.winfo_exists():
                self.after(0, self.iconify)
                
            # Give time for window to minimize
            time.sleep(0.5)
            
            # Move to the target position and click
            if self.cursor_position:
                self._update_status("Moving cursor to position...")
                
                # Move mouse smoothly
                x, y = self.cursor_position
                
                # Try multiple approaches for better reliability
                try:
                    # First approach: Direct move
                    pyautogui.moveTo(x, y, duration=0.1)
                    
                    # Windows-specific focus if enabled
                    if config.windows_focus:
                        focus_success = self.windows_set_foreground_window(x, y)
                        # Give time for window to come to foreground
                        time.sleep(0.5)
                    
                    # Double-check position and click
                    pyautogui.moveTo(x, y, duration=0.1)  # Move again to ensure position
                    
                    # First click - to set focus
                    pyautogui.click()
                    time.sleep(0.3)
                    
                    # Second click - to ensure cursor position
                    pyautogui.click()
                    
                    # Small delay to ensure focus and cursor position
                    time.sleep(0.5)
                    
                except Exception as e:
                    self._update_status(f"Error positioning cursor: {str(e)}")
                    # Continue anyway, some errors are expected
            
            # Type the text with human-like timing
            self._update_status("Typing started...")
            
            # Check if stop requested before typing
            if self.stop_event.is_set():
                self._update_status("Typing stopped")
                return
                
            # Start typing with stop_event passed to the typing function
            human_typing(text, config.wpm, self._update_status, self.stop_event)
            
            # Done
            if not self.stop_event.is_set():
                self._update_status("Typing completed successfully")
            
            # Restore window
            if self.winfo_exists():
                self.after(0, self.deiconify)
                
            # Reset button states
            self._toggle_buttons(False)
            
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            if self.winfo_exists():
                self.after(0, self.deiconify)
            self._toggle_buttons(False)


def show_password_dialog():
    """Shows a password dialog and validates the entered password"""
    # Create a root window first, but don't show it
    root = ctk.CTk()
    root.withdraw()  # Hide the root window
    
    # Make sure we're using dark mode for the dialog
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create a small dialog window
    dialog = ctk.CTkToplevel(root)
    dialog.title("Authentication Required")
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    
    # Make it modal
    dialog.grab_set()
    dialog.focus_force()
    
    # Center on screen
    width = 400
    height = 200
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    # Configure grid
    dialog.grid_columnconfigure(0, weight=1)
    
    # Result variable
    result = {"authenticated": False}
    
    # Add message
    ctk.CTkLabel(
        dialog,
        text="Please enter the application password:",
        font=ctk.CTkFont(size=14, weight="bold")
    ).grid(row=0, column=0, padx=20, pady=(20, 10))
    
    # Add password field
    password_var = tk.StringVar()
    password_entry = ctk.CTkEntry(dialog, show="*", width=300, textvariable=password_var)
    password_entry.grid(row=1, column=0, padx=20, pady=(10, 20))
    password_entry.focus_set()
    
    # Status label
    status_var = tk.StringVar(value="")
    status_label = ctk.CTkLabel(
        dialog,
        textvariable=status_var,
        text_color=AppColors.ERROR
    )
    status_label.grid(row=2, column=0, padx=20, pady=(0, 10))
    
    # Add buttons
    button_frame = ctk.CTkFrame(dialog)
    button_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
    button_frame.grid_columnconfigure((0, 1), weight=1)
    
    def on_cancel():
        result["authenticated"] = False
        dialog.destroy()
        root.destroy()
    
    def on_login():
        password = password_var.get()
        status_var.set("Verifying password...")
        dialog.update()
        
        if validate_password(password):
            result["authenticated"] = True
            dialog.destroy()
            root.destroy()
        else:
            status_var.set("Invalid password. Please try again.")
            password_entry.delete(0, tk.END)
            password_entry.focus_set()
    
    # Handle enter key
    dialog.bind("<Return>", lambda event: on_login())
    dialog.bind("<Escape>", lambda event: on_cancel())
    
    ctk.CTkButton(
        button_frame,
        text="Login",
        command=on_login,
        fg_color=AppColors.SUCCESS,
        text_color="#212121"
    ).grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")
    
    ctk.CTkButton(
        button_frame,
        text="Cancel",
        command=on_cancel,
        fg_color=AppColors.ERROR
    ).grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")
    
    # Run the dialog main loop
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)  # Handle window close button
    root.wait_window(dialog)
    
    return result["authenticated"]


def main():
    """Main entry point for the application"""
    # Verify we're on Windows
    if platform.system() != "Windows":
        messagebox.showerror(
            "Incompatible System",
            "This application is designed to run only on Windows systems."
        )
        return
    
    # Set up error handling
    try:
        # Fix for Windows DPI scaling issues
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass  # If it fails, continue anyway
            
        # Fix for Windows key sending lag
        pyautogui.PAUSE = 0.01  # Faster key operations on Windows
        
        # Initialize CTk before showing the password dialog
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Show the password dialog - this creates its own Tk root window
        authenticated = show_password_dialog()
        
        if not authenticated:
            print("Authentication failed. Exiting.")
            return
            
        # Create and run the application (this creates a new CTk instance)
        app = AutoTyperApp()
        
        # Add a protocol for clean exit
        app.protocol("WM_DELETE_WINDOW", app.on_quit)
        
        # Start the main loop
        app.mainloop()
    except Exception as e:
        # Show error in a message box
        import traceback
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        
        try:
            from tkinter import messagebox
            messagebox.showerror("Application Error", error_msg)
        except:
            print(error_msg)
        
        # Don't re-raise, just exit
        import sys
        sys.exit(1)
        
    except Exception as e:
        # Show error in a message box
        import traceback
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        
        try:
            from tkinter import messagebox
            messagebox.showerror("Application Error", error_msg)
        except:
            print(error_msg)
        
        # Don't re-raise, just exit
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
