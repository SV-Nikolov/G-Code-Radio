#!/usr/bin/env python3
"""
Quick test of G-Code Radio core components (no audio processing)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import Logger
from src.signal_processing.note_detection import NoteDetector
from src.mapping.note_mapper import NoteMapper
from src.mapping.parameter_controller import ParameterController
from src.mapping.bounds_validator import BoundsValidator
from src.printer.moment_s1_config import MomentS1Config
from src.gcode.gcode_generator import GCodeGenerator
from src.gcode.gcode_validator import GCodeValidator

# Setup logging
Logger.setup_logging(level="INFO")
logger = Logger.get_logger(__name__)


def test_all():
    """Run quick tests"""
    print("\n" + "=" * 60)
    print("G-Code Radio - Quick Component Test")
    print("=" * 60 + "\n")
    
    # Test 1: Note Detection
    print("✓ Testing note detection...")
    detector = NoteDetector()
    assert detector.pitch_to_midi(440.0) == 69, "A4 detection failed"
    assert detector.midi_to_note_name(69) == "A4", "MIDI to note name failed"
    print("  - MIDI conversion: ✓")
    
    # Test 2: Parameter Control
    print("\n✓ Testing parameter control...")
    notes = [
        {'midi': 60, 'duration': 1.0, 'start_time': 0.0},
        {'midi': 62, 'duration': 1.0, 'start_time': 1.0},
    ]
    
    controller = ParameterController()
    assert controller.validate_parameters(1.0, 0, 50), "Parameter validation failed"
    
    fast = controller.apply_speed(notes, 2.0)
    assert fast[0]['duration'] == 0.5, "Speed adjustment failed"
    print("  - Speed control: ✓")
    
    shifted = controller.apply_pitch_shift(notes, 5)
    assert shifted[0]['midi'] == 65, "Pitch shift failed"
    print("  - Pitch control: ✓")
    
    # Test 3: Note Mapper
    print("\n✓ Testing note mapper...")
    printer_config = MomentS1Config()
    mapper = NoteMapper(printer_config)
    
    freq = mapper.note_to_frequency(60)
    assert 260 < freq < 270, "Frequency conversion failed"
    print("  - Frequency conversion: ✓")
    
    movement = mapper.note_to_movement(60, 0.5)
    assert movement['midi'] == 60, "Movement creation failed"
    assert movement['distance'] > 0, "Movement distance invalid"
    print("  - Movement creation: ✓")
    
    # Test 4: Bounds Validator
    print("\n✓ Testing bounds validator...")
    validator = BoundsValidator(printer_config)
    
    assert validator.validate_movement(100, 100, 100), "Valid position rejected"
    assert not validator.validate_movement(-50, 100, 100), "Invalid position accepted"
    print("  - Bounds validation: ✓")
    
    clamped = validator.clamp_coordinates(300, 100, 100)
    assert clamped[0] < 200, "Clamping failed"
    print("  - Coordinate clamping: ✓")
    
    # Test 5: G-Code Generation
    print("\n✓ Testing G-code generation...")
    generator = GCodeGenerator(printer_config)
    
    movements = [
        {'axis': 'X', 'distance': 10, 'feedrate': 1000, 'duration': 0.5},
        {'axis': 'Y', 'distance': 5, 'feedrate': 1000, 'duration': 0.25},
    ]
    
    gcode = generator.movements_to_gcode(movements, "Test")
    assert 'G1' in gcode, "G-code generation failed"
    assert len(gcode) > 100, "G-code too short"
    print("  - G-code generation: ✓")
    
    # Test 6: G-Code Validation
    print("\n✓ Testing G-code validation...")
    gvalidator = GCodeValidator(printer_config)
    
    is_valid, report = gvalidator.validate_all(gcode)
    assert is_valid, "G-code validation failed"
    assert report['no_extrusion'], "Extrusion check failed"
    assert report['no_heating'], "Heating check failed"
    assert report['in_bounds'], "Bounds check failed"
    print("  - G-code validation: ✓")
    
    # Test 7: Save to file
    print("\n✓ Testing file output...")
    Path("output").mkdir(exist_ok=True)
    output_file = generator.write_gcode_file(movements, "output/test_quick.gcode", "Test")
    assert Path(output_file).exists(), "Output file not created"
    
    file_size = Path(output_file).stat().st_size
    print(f"  - File output: ✓ ({file_size} bytes)")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(test_all())
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
