"""
GUI Entry Point for G-Code Radio
Launches the graphical interface
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.ui.gui_modern import main

if __name__ == "__main__":
    main()
