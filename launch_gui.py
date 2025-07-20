"""
GPM-Login Automation GUI Launcher

Simple launcher script for the GPM-Login Automation GUI Application
Handles dependency checks and provides user-friendly error messages.

Author: mrlaw74
Date: July 20, 2025
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'tkinter',
        'requests',
        'selenium'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def check_project_files():
    """Check if all required project files are present"""
    required_files = [
        'gpm_client.py',
        'gpm_selenium.py',
        'utils.py',
        'gpm_automation_gui.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return missing_files

def show_error_dialog(title, message):
    """Show error dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(title, message)
    root.destroy()

def show_info_dialog(title, message):
    """Show info dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(title, message)
    root.destroy()

def install_dependencies():
    """Install missing dependencies"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', 'selenium'])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function"""
    print("🎬 GPM-Login Automation Launcher")
    print("=" * 50)
    
    # Check project files
    print("Checking project files...")
    missing_files = check_project_files()
    if missing_files:
        error_msg = f"Missing required files:\n\n" + "\n".join(f"• {file}" for file in missing_files)
        error_msg += "\n\nPlease ensure all project files are in the same directory."
        show_error_dialog("Missing Files", error_msg)
        return
    
    print("✅ All project files found")
    
    # Check dependencies
    print("Checking dependencies...")
    missing_modules = check_dependencies()
    
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        
        if 'tkinter' in missing_modules:
            error_msg = "tkinter is not available. This is usually included with Python.\n\n"
            error_msg += "Please ensure you have a complete Python installation."
            show_error_dialog("Missing tkinter", error_msg)
            return
        
        # Try to install missing modules (except tkinter)
        installable_modules = [m for m in missing_modules if m != 'tkinter']
        if installable_modules:
            print(f"Attempting to install: {', '.join(installable_modules)}")
            if install_dependencies():
                print("✅ Dependencies installed successfully")
            else:
                error_msg = f"Failed to install dependencies:\n\n" + "\n".join(f"• {module}" for module in installable_modules)
                error_msg += "\n\nPlease install them manually using:\n"
                error_msg += f"pip install {' '.join(installable_modules)}"
                show_error_dialog("Installation Failed", error_msg)
                return
    else:
        print("✅ All dependencies available")
    
    # Check GPM-Login connection (optional)
    print("Checking GPM-Login connection...")
    try:
        from gpm_client import GPMClient
        client = GPMClient()
        profiles = client.list_profiles(per_page=1)
        print("✅ GPM-Login connected")
    except Exception as e:
        print(f"⚠️  GPM-Login not available: {str(e)}")
        print("   (You can still use the GUI to configure connection)")
    
    # Launch the GUI
    print("\n🚀 Launching GPM-Login Automation GUI...")
    try:
        from gpm_automation_gui import main as gui_main
        gui_main()
    except Exception as e:
        error_msg = f"Failed to launch GUI application:\n\n{str(e)}"
        error_msg += "\n\nPlease check that all files are present and try again."
        show_error_dialog("Launch Error", error_msg)
        print(f"❌ Launch failed: {str(e)}")

if __name__ == "__main__":
    main()
