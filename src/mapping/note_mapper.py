"""Map musical notes to stepper motor movement patterns

Converts MIDI notes to X/Y/Z movements that produce specific frequencies.
"""

import numpy as np
import random
from src.utils.logger import Logger
from src.utils.error_handler import ValidationError

logger = Logger.get_logger(__name__)


class NoteMapper:
    """Maps musical notes to printer movements"""
    
    # MIDI reference
    A4_MIDI = 69
    A4_FREQ = 440.0
    
    def __init__(self, printer_config):
        """
        Initialize the note mapper
        
        Args:
            printer_config: Printer configuration object
        """
        self.printer_config = printer_config
        self.sr = 22050
        self.hop_length = 512
        # Track a small oscillation window around home to avoid runaway travel
        self._axis_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
        self._axis_dir = {'X': 1.0, 'Y': -1.0, 'Z': 1.0}
        self._max_travel_per_note = 25.0  # mm window to stay near home
    
    def note_to_movement(self, midi_note: int, duration: float) -> dict:
        """
        Convert MIDI note to movement instruction
        
        Args:
            midi_note: MIDI note number (0-127)
            duration: Note duration in seconds
            
        Returns:
            Movement instruction dictionary with axis, distance, feedrate, time
            
        Raises:
            ValidationError: If note is invalid
        """
        try:
            if not (0 <= midi_note <= 127):
                raise ValidationError(f"Invalid MIDI note: {midi_note}")
            
            if duration <= 0:
                raise ValidationError(f"Invalid duration: {duration}")
            
            # Convert MIDI to frequency
            frequency = self.note_to_frequency(midi_note)

            # Select axis first (affects steps-per-mm and feed caps)
            axis = self._select_axis(midi_note)

            # Convert frequency to feedrate using axis-specific steps/mm
            feedrate, step_freq = self.frequency_to_feedrate(frequency, axis)

            # Desired travel to honor the note duration at this feedrate
            desired_distance = (feedrate / 60.0) * duration  # mm

            # Keep motion within a small window around virtual home per axis
            window = self._max_travel_per_note
            dir_sign = self._axis_dir.get(axis, 1.0)
            next_pos = self._axis_pos[axis] + dir_sign * desired_distance

            # If exceeding window, flip direction and recompute
            if abs(next_pos) > window:
                dir_sign *= -1.0
                self._axis_dir[axis] = dir_sign
                next_pos = self._axis_pos[axis] + dir_sign * desired_distance
                # If still too large, clamp to window edge
                if abs(next_pos) > window:
                    next_pos = window * (1 if next_pos > 0 else -1)

            distance = next_pos - self._axis_pos[axis]
            self._axis_pos[axis] = next_pos

            movement = {
                'midi': midi_note,
                'frequency': frequency,
                'axis': axis,
                'distance': distance,
                'feedrate': feedrate,
                'duration': duration,
                'step_frequency_target': step_freq,
            }
            
            return movement
        
        except ValidationError:
            raise
        except Exception as e:
            error_msg = f"Failed to convert note to movement: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
    
    def note_to_frequency(self, midi_note: int) -> float:
        """
        Convert MIDI note to frequency in Hz
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Frequency in Hz
        """
        try:
            # Formula: f = 440 * 2^((m-69)/12)
            frequency = self.A4_FREQ * (2.0 ** ((midi_note - self.A4_MIDI) / 12.0))
            return frequency
        
        except Exception as e:
            logger.error(f"Failed to convert MIDI to frequency: {str(e)}")
            raise ValidationError(f"MIDI to frequency conversion failed: {str(e)}")
    
    def frequency_to_feedrate(self, frequency: float, axis: str) -> tuple:
        """
        Convert frequency to printer feedrate
        
        Stepper motors produce sound by moving at specific frequencies.
        We map musical frequencies to movement frequencies/feedrates.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            (feedrate mm/min, target_step_frequency Hz)
        """
        try:
            # Frequency range for stepper motors
            min_freq = self.printer_config.STEPPER_FREQUENCY_MIN
            max_freq = self.printer_config.STEPPER_FREQUENCY_MAX
            
            # Clamp frequency to valid range
            freq_clamped = max(min_freq, min(max_freq, frequency))
            
            # Axis-specific steps/mm and feed caps
            steps_per_mm = self.printer_config.get_steps_per_mm(axis)
            axis_max_feed = self.printer_config.MAX_FEEDRATE_Z if axis == 'Z' else self.printer_config.MAX_FEEDRATE_XY

            # Target feedrate that produces the desired step frequency
            feedrate = (freq_clamped * 60.0) / steps_per_mm  # mm/min

            # Clamp feedrate within printer limits
            feedrate = max(self.printer_config.MIN_FEEDRATE, min(axis_max_feed, feedrate))

            # Compute resulting step frequency after clamping (for reference)
            step_frequency = feedrate * steps_per_mm / 60.0
            
            return feedrate, step_frequency
        
        except Exception as e:
            logger.error(f"Failed to convert frequency to feedrate: {str(e)}")
            raise ValidationError(f"Frequency to feedrate conversion failed: {str(e)}")
    
    def _select_axis(self, midi_note: int) -> str:
        """
        Select which axis (X, Y, or Z) to use for a note
        
        Randomly selects from X, Y, Z for varied movement visualization
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Axis character ('X', 'Y', or 'Z')
        """
        # Random axis selection for varied movement patterns
        return random.choice(['X', 'Y', 'Z'])
    
    def rotate_axis(self, movements: list) -> list:
        """
        Distribute movements across multiple axes to avoid saturation
        
        Args:
            movements: List of movement dictionaries
            
        Returns:
            Movements with distributed axes
        """
        try:
            axis_order = ['X', 'Y', 'Z']
            axis_index = 0
            
            for movement in movements:
                movement['axis'] = axis_order[axis_index % 3]
                axis_index += 1
            
            return movements
        
        except Exception as e:
            logger.error(f"Failed to rotate axes: {str(e)}")
            return movements
