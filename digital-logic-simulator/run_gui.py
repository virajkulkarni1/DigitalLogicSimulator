#!/usr/bin/env python3
"""
Launcher script for Digital Logic Simulator GUI.
Tries to find a Python installation with tkinter support.
"""

import sys
import subprocess
import shutil

def find_python_with_tkinter():
    """Find a Python executable that has tkinter support."""
    python_candidates = [
        'python3.12',
        '/usr/bin/python3',
        'python3.11',
        'python3.10',
        'python3.9',
        'python3',
    ]
    
    for python_cmd in python_candidates:
        if shutil.which(python_cmd):
            try:
                # Test if tkinter is available
                result = subprocess.run(
                    [python_cmd, '-c', 'import tkinter'],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return python_cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
    
    return None

def main():
    """Main function to launch the GUI."""
    python_cmd = find_python_with_tkinter()
    
    if not python_cmd:
        print("Error: No Python installation with tkinter support found.")
        print("\nSolutions:")
        print("1. Install Python with tkinter: brew install python-tk@3.13")
        print("2. Use system Python: /usr/bin/python3 app_gui.py")
        print("3. Install Python with tkinter support: brew install python-tk")
        sys.exit(1)
    
    print(f"Using {python_cmd} to run the GUI...")
    
    # Run the GUI application
    try:
        subprocess.run([python_cmd, 'app_gui.py'])
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


