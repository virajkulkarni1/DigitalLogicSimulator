#!/bin/bash
# Launcher script for Digital Logic Simulator GUI
# This script tries to find a Python installation with tkinter support

# Try Python 3.12 first (if available)
if command -v python3.12 &> /dev/null; then
    if python3.12 -c "import tkinter" 2>/dev/null; then
        echo "Running with Python 3.12..."
        python3.12 app_gui.py
        exit 0
    fi
fi

# Try system Python
if /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
    echo "Running with system Python..."
    /usr/bin/python3 app_gui.py
    exit 0
fi

# Try default python3
if python3 -c "import tkinter" 2>/dev/null; then
    echo "Running with default Python 3..."
    python3 app_gui.py
    exit 0
fi

# If we get here, no Python with tkinter was found
echo "Error: No Python installation with tkinter support found."
echo ""
echo "Solutions:"
echo "1. Use Python 3.12: python3.12 app_gui.py"
echo "2. Use system Python: /usr/bin/python3 app_gui.py"
echo "3. Install tkinter for Python 3.13: brew install python-tk@3.13"
echo "4. Install Python with tkinter: brew install python-tk"
exit 1


