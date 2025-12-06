"""
Validate that all movements stay within printer bounds

Ensures no axis exceeds safe limits.
"""

from src.utils.logger import Logger
from src.utils.error_handler import BoundsViolationError

logger = Logger.get_logger(__name__)


class BoundsValidator:
    """Validates movements against printer bounds"""
    
    def __init__(self, printer_config):
        """
        Initialize the bounds validator
        
        Args:
            printer_config: Printer configuration object
        """
        self.printer_config = printer_config
        self.safe_bounds = printer_config.get_safe_bounds()
        self.home_position = printer_config.get_home_position()
    
    def validate_movement(self, x: float, y: float, z: float) -> bool:
        """
        Check if movement is within safe bounds
        
        Args:
            x, y, z: Coordinates in mm
            
        Returns:
            True if within bounds, False otherwise
        """
        try:
            bounds = self.safe_bounds
            
            x_valid = bounds['x']['min'] <= x <= bounds['x']['max']
            y_valid = bounds['y']['min'] <= y <= bounds['y']['max']
            z_valid = bounds['z']['min'] <= z <= bounds['z']['max']
            
            return x_valid and y_valid and z_valid
        
        except Exception as e:
            logger.error(f"Failed to validate movement: {str(e)}")
            return False
    
    def clamp_coordinates(self, x: float, y: float, z: float):
        """
        Clamp coordinates to safe bounds
        
        Args:
            x, y, z: Coordinates in mm
            
        Returns:
            Tuple of clamped coordinates (x, y, z)
        """
        try:
            bounds = self.safe_bounds
            
            x_clamped = max(bounds['x']['min'], min(bounds['x']['max'], x))
            y_clamped = max(bounds['y']['min'], min(bounds['y']['max'], y))
            z_clamped = max(bounds['z']['min'], min(bounds['z']['max'], z))
            
            if x != x_clamped or y != y_clamped or z != z_clamped:
                logger.debug(f"Clamped coordinates: ({x}, {y}, {z}) → ({x_clamped}, {y_clamped}, {z_clamped})")
            
            return x_clamped, y_clamped, z_clamped
        
        except Exception as e:
            logger.error(f"Failed to clamp coordinates: {str(e)}")
            return x, y, z
    
    def validate_all_movements(self, movements: list, start_pos: tuple = None) -> list:
        """
        Validate and adjust all movements in sequence
        
        Args:
            movements: List of movement dictionaries
            start_pos: Starting position (x, y, z), uses home if None
            
        Returns:
            List of validated movements
            
        Raises:
            BoundsViolationError: If movements cannot be made safe
        """
        try:
            if start_pos is None:
                start_pos = self.home_position
            
            current_pos = list(start_pos)
            validated_movements = []
            violations = 0
            
            for i, movement in enumerate(movements):
                try:
                    # Generate next position based on movement
                    axis = movement.get('axis', 'X')
                    distance = movement.get('distance', 0)
                    
                    next_pos = current_pos.copy()
                    axis_index = {'X': 0, 'Y': 1, 'Z': 2}.get(axis, 0)
                    next_pos[axis_index] += distance
                    
                    # Clamp to bounds
                    clamped_pos = self.clamp_coordinates(*next_pos)
                    
                    # Check if clamping changed position
                    if clamped_pos != tuple(next_pos):
                        violations += 1
                        logger.warning(f"Movement {i} exceeded bounds, clamping applied")
                    
                    # Update movement with actual endpoint
                    validated_movement = movement.copy()
                    validated_movement['end_position'] = clamped_pos
                    validated_movement['start_position'] = tuple(current_pos)
                    
                    validated_movements.append(validated_movement)
                    current_pos = list(clamped_pos)
                
                except Exception as e:
                    logger.error(f"Failed to validate movement {i}: {str(e)}")
                    violations += 1
            
            if violations > 0:
                logger.warning(f"Total bound violations: {violations}")
            
            logger.info(f"Validated {len(movements)} movements")
            return validated_movements
        
        except Exception as e:
            error_msg = f"Failed to validate all movements: {str(e)}"
            logger.error(error_msg)
            raise BoundsViolationError(error_msg)
    
    def get_bounds_info(self) -> dict:
        """
        Get information about printer bounds
        
        Returns:
            Dictionary with bounds information
        """
        try:
            bounds = self.safe_bounds
            return {
                'x_min': bounds['x']['min'],
                'x_max': bounds['x']['max'],
                'y_min': bounds['y']['min'],
                'y_max': bounds['y']['max'],
                'z_min': bounds['z']['min'],
                'z_max': bounds['z']['max'],
                'home': self.home_position,
            }
        
        except Exception as e:
            logger.error(f"Failed to get bounds info: {str(e)}")
            return {}
