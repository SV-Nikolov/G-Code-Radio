"""
Apply Speed, Pitch, and Complexity parameter adjustments

Modulates the note sequence based on user parameters.
"""

from src.utils.logger import Logger
from src.utils.error_handler import InvalidParameterError

logger = Logger.get_logger(__name__)


class ParameterController:
    """Controls Speed, Pitch, and Complexity parameters"""
    
    def __init__(self):
        """Initialize the parameter controller"""
        pass
    
    def apply_speed(self, notes: list, speed_multiplier: float) -> list:
        """
        Apply speed adjustment to notes
        
        Args:
            notes: List of note dictionaries with durations
            speed_multiplier: Speed factor (0.5-3.0)
            
        Returns:
            Speed-adjusted note sequence
            
        Raises:
            InvalidParameterError: If multiplier is invalid
        """
        try:
            if not (0.5 <= speed_multiplier <= 3.0):
                raise InvalidParameterError(f"Speed must be between 0.5 and 3.0, got {speed_multiplier}")
            
            logger.info(f"Applying speed adjustment: {speed_multiplier}x")
            
            adjusted = []
            for note in notes:
                adjusted_note = note.copy()
                # Shorter duration = faster playback
                adjusted_note['duration'] = note['duration'] / speed_multiplier
                adjusted.append(adjusted_note)
            
            logger.debug(f"Speed adjustment complete")
            return adjusted
        
        except InvalidParameterError:
            raise
        except Exception as e:
            error_msg = f"Failed to apply speed: {str(e)}"
            logger.error(error_msg)
            raise InvalidParameterError(error_msg)
    
    def apply_pitch_shift(self, notes: list, semitone_shift: int) -> list:
        """
        Apply pitch shift to notes
        
        Args:
            notes: List of note dictionaries
            semitone_shift: Semitone shift (-12 to +12)
            
        Returns:
            Pitch-shifted note sequence
            
        Raises:
            InvalidParameterError: If shift is invalid
        """
        try:
            if not (-12 <= semitone_shift <= 12):
                raise InvalidParameterError(f"Pitch shift must be between -12 and +12, got {semitone_shift}")
            
            if semitone_shift == 0:
                return notes
            
            logger.info(f"Applying pitch shift: {semitone_shift:+d} semitones")
            
            adjusted = []
            for note in notes:
                adjusted_note = note.copy()
                # Shift MIDI note
                adjusted_note['midi'] = max(0, min(127, note['midi'] + semitone_shift))
                adjusted.append(adjusted_note)
            
            logger.debug(f"Pitch shift complete")
            return adjusted
        
        except InvalidParameterError:
            raise
        except Exception as e:
            error_msg = f"Failed to apply pitch shift: {str(e)}"
            logger.error(error_msg)
            raise InvalidParameterError(error_msg)
    
    def apply_complexity(self, notes: list, complexity_level: int):
        """
        Apply complexity adjustment (note reduction)
        
        Args:
            notes: List of note dictionaries
            complexity_level: Complexity level (0-100)
            
        Returns:
            Complexity-adjusted note sequence
            
        Raises:
            InvalidParameterError: If level is invalid
        """
        try:
            if not (0 <= complexity_level <= 100):
                raise InvalidParameterError(f"Complexity must be between 0 and 100, got {complexity_level}")
            
            from src.signal_processing.complexity_reducer import ComplexityReducer
            
            logger.info(f"Applying complexity adjustment: {complexity_level}%")
            
            reducer = ComplexityReducer()
            adjusted = reducer.reduce_complexity(notes, complexity_level)
            
            logger.debug(f"Complexity adjustment complete: {len(notes)} → {len(adjusted)} notes")
            return adjusted
        
        except InvalidParameterError:
            raise
        except Exception as e:
            error_msg = f"Failed to apply complexity: {str(e)}"
            logger.error(error_msg)
            raise InvalidParameterError(error_msg)
    
    def apply_all_parameters(self, notes: list, speed: float, pitch: int, complexity: int) -> list:
        """
        Apply all parameters in sequence
        
        Order: Complexity reduction → Pitch shift → Speed adjustment
        This order ensures we reduce notes first, then modify them
        
        Args:
            notes: List of note dictionaries
            speed: Speed multiplier (0.5-3.0)
            pitch: Pitch shift in semitones (-12 to +12)
            complexity: Complexity level (0-100)
            
        Returns:
            Fully adjusted note sequence
            
        Raises:
            InvalidParameterError: If any parameter is invalid
        """
        try:
            logger.info(f"Applying all parameters: speed={speed}x, pitch={pitch:+d}, complexity={complexity}%")
            
            # Order matters: complexity first, then pitch, then speed
            result = notes
            
            # 1. Reduce complexity
            result = self.apply_complexity(result, complexity)
            
            # 2. Shift pitch
            result = self.apply_pitch_shift(result, pitch)
            
            # 3. Adjust speed
            result = self.apply_speed(result, speed)
            
            logger.info(f"All parameters applied successfully")
            return result
        
        except InvalidParameterError:
            raise
        except Exception as e:
            error_msg = f"Failed to apply parameters: {str(e)}"
            logger.error(error_msg)
            raise InvalidParameterError(error_msg)
    
    def validate_parameters(self, speed: float = None, pitch: int = None, complexity: int = None) -> bool:
        """
        Validate all parameters
        
        Args:
            speed: Speed multiplier or None
            pitch: Pitch shift or None
            complexity: Complexity level or None
            
        Returns:
            True if all parameters are valid
            
        Raises:
            InvalidParameterError: If any parameter is invalid
        """
        try:
            if speed is not None and not (0.5 <= speed <= 3.0):
                raise InvalidParameterError(f"Speed {speed} out of range [0.5, 3.0]")
            
            if pitch is not None and not (-12 <= pitch <= 12):
                raise InvalidParameterError(f"Pitch {pitch} out of range [-12, 12]")
            
            if complexity is not None and not (0 <= complexity <= 100):
                raise InvalidParameterError(f"Complexity {complexity} out of range [0, 100]")
            
            return True
        
        except InvalidParameterError:
            raise
        except Exception as e:
            error_msg = f"Parameter validation failed: {str(e)}"
            logger.error(error_msg)
            raise InvalidParameterError(error_msg)
