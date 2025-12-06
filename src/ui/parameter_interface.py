"""
Parameter interface for Speed, Pitch, and Complexity controls

Handles user input validation and parameter constraints.
"""

class ParameterInterface:
    """Manages user parameter input"""
    
    # Parameter constraints
    SPEED_MIN = 0.5
    SPEED_MAX = 3.0
    SPEED_DEFAULT = 1.0
    
    PITCH_MIN = -12
    PITCH_MAX = 12
    PITCH_DEFAULT = 0
    
    COMPLEXITY_MIN = 0
    COMPLEXITY_MAX = 100
    COMPLEXITY_DEFAULT = 50
    
    def __init__(self):
        """Initialize parameter interface"""
        pass
    
    def validate_speed(self, speed: float) -> bool:
        """
        Validate speed parameter
        
        Args:
            speed: Speed multiplier
            
        Returns:
            True if valid, False otherwise
        """
        # Implementation to follow
        pass
    
    def validate_pitch(self, pitch: int) -> bool:
        """
        Validate pitch parameter
        
        Args:
            pitch: Pitch shift in semitones
            
        Returns:
            True if valid, False otherwise
        """
        # Implementation to follow
        pass
    
    def validate_complexity(self, complexity: int) -> bool:
        """
        Validate complexity parameter
        
        Args:
            complexity: Complexity level (0-100)
            
        Returns:
            True if valid, False otherwise
        """
        # Implementation to follow
        pass
    
    def get_parameters_with_defaults(self, speed=None, pitch=None, complexity=None) -> dict:
        """
        Get parameters with defaults for None values
        
        Args:
            speed: Speed multiplier or None
            pitch: Pitch shift or None
            complexity: Complexity level or None
            
        Returns:
            Dictionary of validated parameters
        """
        # Implementation to follow
        pass
