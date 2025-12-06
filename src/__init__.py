"""
G-Code Radio - Main Entry Point

Transforms YouTube audio into G-code for 3D printer stepper motor music.
"""

__version__ = "0.1.0"
__author__ = "G-Code Radio Contributors"

import sys
from pathlib import Path

# Add src to path
SRC_PATH = Path(__file__).parent
sys.path.insert(0, str(SRC_PATH))

# Module imports will be added as implementation progresses
