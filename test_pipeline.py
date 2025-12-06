#!/usr/bin/env python3
"""
Quick test script for G-Code Radio pipeline
Tests individual components without requiring YouTube or actual audio files
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import Logger
from src.utils.error_handler import GCodeRadioException
from src.signal_processing.note_detection import NoteDetector
from src.signal_processing.complexity_reducer import ComplexityReducer
from src.mapping.parameter_controller import ParameterController
from src.mapping.note_mapper import NoteMapper
from src.mapping.bounds_validator import BoundsValidator
from src.printer.moment_s1_config import MomentS1Config
from src.gcode.gcode_generator import GCodeGenerator
from src.gcode.gcode_validator import GCodeValidator

# Setup logging
Logger.setup_logging(level="INFO")
logger = Logger.get_logger(__name__)


def test_note_detection():
    """Test note detection"""
    print("\n" + "=" * 60)
    print("TEST: Note Detection")
    print("=" * 60)
    
    detector = NoteDetector()
    
    # Test frequency to MIDI conversion
    freq_test = 440.0
    midi = detector.pitch_to_midi(freq_test)
    note_name = detector.midi_to_note_name(midi)
    
    print(f"Frequency: {freq_test} Hz")
    print(f"MIDI Note: {midi}")
    print(f"Note Name: {note_name}")
    
    assert note_name == "A4", f"Expected A4, got {note_name}"
    print("✓ Note detection passed!")


def test_complexity_reducer():
    """Test complexity reduction"""
    print("\n" + "=" * 60)
    print("TEST: Complexity Reduction")
    print("=" * 60)
    
    # Create test notes
    notes = [
        {'midi': 60, 'duration': 0.5, 'start_time': 0.0},
        {'midi': 62, 'duration': 0.5, 'start_time': 0.5},
        {'midi': 64, 'duration': 0.5, 'start_time': 1.0},
        {'midi': 65, 'duration': 0.5, 'start_time': 1.5},
        {'midi': 67, 'duration': 0.5, 'start_time': 2.0},
    ]
    
    reducer = ComplexityReducer()
    
    # Test full complexity
    full = reducer.reduce_complexity(notes, 100)
    print(f"Complexity 100%: {len(full)} notes")
    assert len(full) == len(notes), "Expected all notes"
    
    # Test half complexity
    half = reducer.reduce_complexity(notes, 50)
    print(f"Complexity 50%: {len(half)} notes")
    
    # Test low complexity
    low = reducer.reduce_complexity(notes, 20)
    print(f"Complexity 20%: {len(low)} notes")
    
    print("✓ Complexity reduction passed!")


def test_parameter_controller():
    """Test parameter control"""
    print("\n" + "=" * 60)
    print("TEST: Parameter Control")
    print("=" * 60)
    
    notes = [
        {'midi': 60, 'duration': 1.0, 'start_time': 0.0},
        {'midi': 62, 'duration': 1.0, 'start_time': 1.0},
        {'midi': 64, 'duration': 1.0, 'start_time': 2.0},
    ]
    
    controller = ParameterController()
    
    # Validate parameters
    assert controller.validate_parameters(speed=1.0, pitch=0, complexity=50)
    print("✓ Parameter validation passed")
    
    # Apply speed
    fast_notes = controller.apply_speed(notes, 2.0)
    print(f"Original duration: {notes[0]['duration']}")
    print(f"Fast (2x) duration: {fast_notes[0]['duration']}")
    assert fast_notes[0]['duration'] == 0.5, "Expected halved duration"
    
    # Apply pitch shift
    shifted = controller.apply_pitch_shift(notes, 5)
    print(f"Original MIDI: {notes[0]['midi']}")
    print(f"Shifted (+5) MIDI: {shifted[0]['midi']}")
    assert shifted[0]['midi'] == 65, "Expected MIDI shift"
    
    print("✓ Parameter control passed!")


def test_note_mapper():
    """Test note mapping"""
    print("\n" + "=" * 60)
    print("TEST: Note Mapping")
    print("=" * 60)
    
    printer_config = MomentS1Config()
    mapper = NoteMapper(printer_config)
    
    # Test MIDI to frequency
    midi = 60  # C4
    freq = mapper.note_to_frequency(midi)
    print(f"MIDI {midi} → Frequency {freq:.2f} Hz")
    
    # Test frequency to feedrate
    feedrate = mapper.frequency_to_feedrate(freq)
    print(f"Frequency {freq:.2f} Hz → Feedrate {feedrate:.0f} mm/min")
    
    # Test note to movement
    movement = mapper.note_to_movement(60, 0.5)
    print(f"Movement: {movement['axis']} axis, distance={movement['distance']:.2f}mm, feedrate={movement['feedrate']:.0f}")
    
    print("✓ Note mapping passed!")


def test_bounds_validator():
    """Test bounds validation"""
    print("\n" + "=" * 60)
    print("TEST: Bounds Validation")
    print("=" * 60)
    
    printer_config = MomentS1Config()
    validator = BoundsValidator(printer_config)
    
    bounds = validator.get_bounds_info()
    print(f"Printer bounds:")
    print(f"  X: {bounds['x_min']:.0f} - {bounds['x_max']:.0f}")
    print(f"  Y: {bounds['y_min']:.0f} - {bounds['y_max']:.0f}")
    print(f"  Z: {bounds['z_min']:.0f} - {bounds['z_max']:.0f}")
    
    # Test valid movement
    valid = validator.validate_movement(100, 100, 100)
    print(f"Position (100, 100, 100) valid: {valid}")
    assert valid, "Center position should be valid"
    
    # Test invalid movement
    invalid = validator.validate_movement(-50, 100, 100)
    print(f"Position (-50, 100, 100) valid: {invalid}")
    assert not invalid, "Negative position should be invalid"
    
    # Test clamping
    clamped = validator.clamp_coordinates(300, 100, 100)
    print(f"Clamped (300, 100, 100) → {clamped}")
    assert clamped[0] == bounds['x_max'], "Should be clamped to max"
    
    print("✓ Bounds validation passed!")


def test_gcode_generation():
    """Test G-code generation"""
    print("\n" + "=" * 60)
    print("TEST: G-code Generation")
    print("=" * 60)
    
    printer_config = MomentS1Config()
    generator = GCodeGenerator(printer_config)
    
    # Create test movements
    movements = [
        {'axis': 'X', 'distance': 10, 'feedrate': 1000, 'duration': 0.5},
        {'axis': 'Y', 'distance': 5, 'feedrate': 1000, 'duration': 0.25},
        {'axis': 'Z', 'distance': 2, 'feedrate': 500, 'duration': 0.2},
    ]
    
    # Generate G-code
    gcode = generator.movements_to_gcode(movements, "Test Song")
    
    print(f"Generated G-code length: {len(gcode)} characters")
    print(f"Number of move commands: {gcode.count('G1')}")
    
    # Save to file
    Path("output").mkdir(exist_ok=True)
    output_file = generator.write_gcode_file(movements, "output/test.gcode", "Test")
    print(f"G-code written to: {output_file}")
    
    print("✓ G-code generation passed!")


def test_gcode_validation():
    """Test G-code validation"""
    print("\n" + "=" * 60)
    print("TEST: G-code Validation")
    print("=" * 60)
    
    printer_config = MomentS1Config()
    
    # Generate valid G-code
    generator = GCodeGenerator(printer_config)
    movements = [
        {'axis': 'X', 'distance': 10, 'feedrate': 1000, 'duration': 0.5},
    ]
    gcode = generator.movements_to_gcode(movements)
    
    # Validate
    validator = GCodeValidator(printer_config)
    is_valid, report = validator.validate_all(gcode)
    
    print(f"Valid: {is_valid}")
    print(f"Checks passed: {report['checks_passed']}/{report['checks_total']}")
    print(f"  - No extrusion: {report['no_extrusion']}")
    print(f"  - No heating: {report['no_heating']}")
    print(f"  - In bounds: {report['in_bounds']}")
    
    assert is_valid, "Generated G-code should be valid"
    
    print("✓ G-code validation passed!")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("G-Code Radio Component Tests")
    print("=" * 60)
    
    tests = [
        ("Note Detection", test_note_detection),
        ("Complexity Reduction", test_complexity_reducer),
        ("Parameter Control", test_parameter_controller),
        ("Note Mapping", test_note_mapper),
        ("Bounds Validation", test_bounds_validator),
        ("G-code Generation", test_gcode_generation),
        ("G-code Validation", test_gcode_validation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ {name} FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
