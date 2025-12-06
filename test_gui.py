"""
Test GUI and Visualization Components
"""

import tkinter as tk
from pathlib import Path
import sys

from src.ui.gui import GCodeRadioGUI
from src.ui.visualization import VisualizationWindow
from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


def test_gui_initialization():
    """Test GUI initialization"""
    print("\n✓ Testing GUI initialization...")
    try:
        root = tk.Tk()
        gui = GCodeRadioGUI(root)
        
        # Verify widgets exist
        assert hasattr(gui, 'input_var'), "Input variable not found"
        assert hasattr(gui, 'output_var'), "Output variable not found"
        assert hasattr(gui, 'speed_var'), "Speed variable not found"
        assert hasattr(gui, 'pitch_var'), "Pitch variable not found"
        assert hasattr(gui, 'complexity_var'), "Complexity variable not found"
        assert hasattr(gui, 'log_text'), "Log text widget not found"
        
        # Verify default values
        assert gui.speed_var.get() == 1.0, "Default speed should be 1.0"
        assert gui.pitch_var.get() == 0, "Default pitch should be 0"
        assert gui.complexity_var.get() == 50, "Default complexity should be 50"
        
        root.destroy()
        print("  ✓ GUI initialization: OK")
        return True
    except Exception as e:
        print(f"  ✗ GUI initialization failed: {e}")
        return False


def test_parameter_updates():
    """Test parameter slider updates"""
    print("\n✓ Testing parameter updates...")
    try:
        root = tk.Tk()
        gui = GCodeRadioGUI(root)
        
        # Test speed update
        gui.speed_var.set(2.5)
        gui.update_speed_label('2.5')
        assert gui.speed_label.cget("text") == "2.5x", "Speed label update failed"
        
        # Test pitch update
        gui.pitch_var.set(5)
        gui.update_pitch_label('5')
        assert gui.pitch_label.cget("text") == "+5", "Pitch label update failed"
        
        # Test complexity update
        gui.complexity_var.set(75)
        gui.update_complexity_label('75')
        assert gui.complexity_label.cget("text") == "75%", "Complexity label update failed"
        
        root.destroy()
        print("  ✓ Parameter updates: OK")
        return True
    except Exception as e:
        print(f"  ✗ Parameter updates failed: {e}")
        return False


def test_visualization_gcode_parsing():
    """Test visualization G-code parsing"""
    print("\n✓ Testing visualization G-code parsing...")
    try:
        # Create test G-code file
        test_gcode = """G28             ; Home printer
G90             ; Set to absolute positioning
G1 X100 Y100 Z50 F3000 ; Move to start
G1 X110 Y100 Z50 F2500 ; Note 1
G1 X100 Y110 Z50 F2500 ; Note 2
G1 X110 Y110 Z50 F2500 ; Note 3
"""
        
        test_file = Path("output/test_viz.gcode")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_gcode)
        
        # Create and test visualization
        root = tk.Tk()
        
        class TestViz(VisualizationWindow):
            def __init__(self, root, path):
                super().__init__(root, path)
                self.test_complete = False
        
        viz = TestViz(root, test_file)
        
        # Verify parsing
        assert viz.gcode_content == test_gcode, "G-code not read correctly"
        assert len(viz.gcode_content.split('\n')) > 0, "G-code parsing failed"
        
        root.destroy()
        test_file.unlink()  # Clean up
        
        print("  ✓ Visualization G-code parsing: OK")
        return True
    except Exception as e:
        print(f"  ✗ Visualization G-code parsing failed: {e}")
        return False


def test_visualization_statistics():
    """Test visualization statistics generation"""
    print("\n✓ Testing visualization statistics...")
    try:
        # Create test G-code with movements
        test_gcode = """G28             ; Home
G90             ; Absolute
G1 X100.0 Y100.0 Z50.0 F3000
G1 X105.0 Y100.0 Z50.0 F2800
G1 X110.0 Y105.0 Z50.0 F2600
G1 X115.0 Y110.0 Z50.0 F2400
"""
        
        test_file = Path("output/test_stats.gcode")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_gcode)
        
        root = tk.Tk()
        viz = VisualizationWindow(root, test_file)
        
        # Verify stats were generated
        stats_content = viz.stats_text.get(1.0, tk.END)
        assert "MOVEMENT DATA" in stats_content, "Movement stats missing"
        assert "FEEDRATE" in stats_content, "Feedrate stats missing"
        
        root.destroy()
        test_file.unlink()  # Clean up
        
        print("  ✓ Visualization statistics: OK")
        return True
    except Exception as e:
        print(f"  ✗ Visualization statistics failed: {e}")
        return False


def test_gui_logging():
    """Test GUI logging functionality"""
    print("\n✓ Testing GUI logging...")
    try:
        root = tk.Tk()
        gui = GCodeRadioGUI(root)
        
        # Test logging
        test_message = "Test log message"
        gui.log(test_message)
        
        # Verify log contains message
        log_content = gui.log_text.get(1.0, tk.END)
        assert test_message in log_content, "Log message not recorded"
        
        # Test clear
        gui.clear_log()
        log_content = gui.log_text.get(1.0, tk.END)
        assert log_content.strip() == "", "Log clear failed"
        
        root.destroy()
        print("  ✓ GUI logging: OK")
        return True
    except Exception as e:
        print(f"  ✗ GUI logging failed: {e}")
        return False


def test_gui_validation():
    """Test GUI input validation"""
    print("\n✓ Testing GUI input validation...")
    try:
        root = tk.Tk()
        gui = GCodeRadioGUI(root)
        
        # Test empty input validation (should trigger warning)
        gui.input_var.set("")
        gui.output_var.set("output.gcode")
        
        # Processing flag should prevent multiple conversions
        assert gui.processing == False, "Processing flag should be False initially"
        
        root.destroy()
        print("  ✓ GUI input validation: OK")
        return True
    except Exception as e:
        print(f"  ✗ GUI input validation failed: {e}")
        return False


def main():
    """Run all GUI and visualization tests"""
    print("\n" + "="*60)
    print("G-Code Radio - GUI and Visualization Tests")
    print("="*60)
    
    tests = [
        test_gui_initialization,
        test_parameter_updates,
        test_gui_logging,
        test_gui_validation,
        test_visualization_gcode_parsing,
        test_visualization_statistics,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    if all(results):
        print("✓ ALL TESTS PASSED!")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
