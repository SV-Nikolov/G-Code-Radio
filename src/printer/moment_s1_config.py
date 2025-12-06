"""
Moment S1 (2014) 3D Printer Configuration

Defines all specifications, bounds, and constraints for the printer.
"""

class MomentS1Config:
    """Configuration for Moment S1 (2014) 3D printer"""
    
    # Build volume (mm)
    BUILD_VOLUME_X_MIN = 0
    BUILD_VOLUME_X_MAX = 200
    BUILD_VOLUME_Y_MIN = 0
    BUILD_VOLUME_Y_MAX = 200
    BUILD_VOLUME_Z_MIN = 0
    BUILD_VOLUME_Z_MAX = 200
    
    # Safety margins (mm)
    SAFETY_MARGIN = 5
    
    # Movement constraints
    MAX_FEEDRATE_XY = 6000  # mm/min
    MAX_FEEDRATE_Z = 3000   # mm/min
    MIN_FEEDRATE = 10       # mm/min
    
    # Stepper motor characteristics
    STEPPER_FREQUENCY_MIN = 100   # Hz
    STEPPER_FREQUENCY_MAX = 10000  # Hz
    
    # Home position
    HOME_X = 100
    HOME_Y = 100
    HOME_Z = 100
    
    def __init__(self):
        """Initialize printer configuration"""
        pass
    
    def get_bounds(self) -> dict:
        """
        Get printer build volume bounds
        
        Returns:
            Dictionary with min/max for each axis
        """
        return {
            'x': {'min': self.BUILD_VOLUME_X_MIN, 'max': self.BUILD_VOLUME_X_MAX},
            'y': {'min': self.BUILD_VOLUME_Y_MIN, 'max': self.BUILD_VOLUME_Y_MAX},
            'z': {'min': self.BUILD_VOLUME_Z_MIN, 'max': self.BUILD_VOLUME_Z_MAX},
        }
    
    def get_safe_bounds(self) -> dict:
        """
        Get printer bounds with safety margin applied
        
        Returns:
            Dictionary with safe min/max for each axis
        """
        return {
            'x': {
                'min': self.BUILD_VOLUME_X_MIN + self.SAFETY_MARGIN,
                'max': self.BUILD_VOLUME_X_MAX - self.SAFETY_MARGIN
            },
            'y': {
                'min': self.BUILD_VOLUME_Y_MIN + self.SAFETY_MARGIN,
                'max': self.BUILD_VOLUME_Y_MAX - self.SAFETY_MARGIN
            },
            'z': {
                'min': self.BUILD_VOLUME_Z_MIN + self.SAFETY_MARGIN,
                'max': self.BUILD_VOLUME_Z_MAX - self.SAFETY_MARGIN
            },
        }
    
    def get_home_position(self) -> tuple:
        """
        Get printer home position
        
        Returns:
            Tuple of (x, y, z) home coordinates
        """
        return (self.HOME_X, self.HOME_Y, self.HOME_Z)
