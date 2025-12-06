"""
Map musical notes to stepper motor movement patterns

Converts MIDI notes to X/Y/Z movements that produce specific frequencies.
"""

import numpy as np
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
            
            # Convert frequency to feedrate
            feedrate = self.frequency_to_feedrate(frequency)
            
            # Calculate movement distance based on duration and feedrate
            distance = (feedrate / 60) * duration  # Convert mm/min to mm/s
            
            movement = {
                'midi': midi_note,
                'frequency': frequency,
                'axis': self._select_axis(midi_note),
                'distance': distance,
                'feedrate': feedrate,
                'duration': duration,
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
    
    def frequency_to_feedrate(self, frequency: float) -> float:
        """
        Convert frequency to printer feedrate
        
        Stepper motors produce sound by moving at specific frequencies.
        We map musical frequencies to movement frequencies/feedrates.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Feedrate in mm/min
        """
        try:
            # Frequency range for stepper motors
            min_freq = self.printer_config.STEPPER_FREQUENCY_MIN
            max_freq = self.printer_config.STEPPER_FREQUENCY_MAX
            
            # Clamp frequency to valid range
            freq_clamped = max(min_freq, min(max_freq, frequency))
            
            # Map frequency to feedrate
            # Using a scaling factor: each Hz = feedrate mm/min
            # This is a heuristic - adjust based on actual printer behavior
            feedrate = freq_clamped * 60  # Convert Hz to cycles per minute
            
            # Clamp to printer limits
            feedrate = max(self.printer_config.MIN_FEEDRATE, 
                         min(self.printer_config.MAX_FEEDRATE_XY, feedrate))
            
            return feedrate
        
        except Exception as e:
            logger.error(f"Failed to convert frequency to feedrate: {str(e)}")
            raise ValidationError(f"Frequency to feedrate conversion failed: {str(e)}")
    
    def _select_axis(self, midi_note: int) -> str:
        """
        Select which axis (X, Y, or Z) to use for a note
        
        Lower notes use Z axis (slower), middle use X, higher use Y
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Axis character ('X', 'Y', or 'Z')
        """
        # Divide MIDI range into thirds
        if midi_note < 43:  # C2
            return 'Z'
        elif midi_note < 86:  # C6
            return 'X'
        else:
            return 'Y'
    
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
