"""
Validate G-code for safety and correctness

Ensures no extrusion, heating, or dangerous commands.
"""

import re
from src.utils.logger import Logger
from src.utils.error_handler import ValidationError

logger = Logger.get_logger(__name__)


class GCodeValidator:
    """Validates G-code for safety and correctness"""
    
    def __init__(self, printer_config):
        """
        Initialize the G-code validator
        
        Args:
            printer_config: Printer configuration object
        """
        self.printer_config = printer_config
        
        # Forbidden commands that should never appear
        self.forbidden_commands = [
            'M104',  # Set hotend temperature
            'M109',  # Set hotend temperature and wait
            'M140',  # Set bed temperature
            'M190',  # Set bed temperature and wait
            'G10',   # Retract
            'G11',   # Unretract
            'M82',   # Set extruder absolute
            'M83',   # Set extruder relative
        ]
        
        # G-codes that might indicate extrusion
        self.extrusion_codes = [
            'G0',    # Rapid move with potential extrusion
            'G1',    # Linear move (OK if no E axis)
        ]
    
    def check_no_extrusion(self, gcode: str) -> bool:
        """
        Verify no E-axis extrusion commands
        
        Args:
            gcode: G-code file content
            
        Returns:
            True if no extrusion, False otherwise
        """
        try:
            logger.debug("Checking for extrusion commands")
            
            lines = gcode.split('\n')
            extrusion_found = False
            
            for i, line in enumerate(lines):
                # Remove comments
                if ';' in line:
                    line = line[:line.index(';')]
                
                # Check for E-axis moves
                if re.search(r'\bE[-+]?\d+\.?\d*', line, re.IGNORECASE):
                    logger.warning(f"Line {i+1}: Extrusion detected: {line.strip()}")
                    extrusion_found = True
            
            return not extrusion_found
        
        except Exception as e:
            logger.error(f"Failed to check extrusion: {str(e)}")
            return False
    
    def check_no_heating(self, gcode: str) -> bool:
        """
        Verify no heating commands
        
        Args:
            gcode: G-code file content
            
        Returns:
            True if no heating, False otherwise
        """
        try:
            logger.debug("Checking for heating commands")
            
            lines = gcode.split('\n')
            heating_found = False
            
            for i, line in enumerate(lines):
                # Remove comments
                if ';' in line:
                    line = line[:line.index(';')]
                
                # Check for heating commands
                for forbidden in self.forbidden_commands:
                    if re.search(rf'\b{forbidden}\b', line, re.IGNORECASE):
                        logger.warning(f"Line {i+1}: Forbidden command detected: {forbidden}")
                        heating_found = True
            
            return not heating_found
        
        except Exception as e:
            logger.error(f"Failed to check heating: {str(e)}")
            return False
    
    def check_bounds(self, gcode: str) -> bool:
        """
        Verify all coordinates within printer bounds
        
        Args:
            gcode: G-code file content
            
        Returns:
            True if all coordinates valid, False otherwise
        """
        try:
            logger.debug("Checking coordinate bounds")
            
            bounds = self.printer_config.get_safe_bounds()
            lines = gcode.split('\n')
            violations = 0
            
            for i, line in enumerate(lines):
                # Remove comments
                if ';' in line:
                    line = line[:line.index(';')]
                
                # Extract coordinates
                x_match = re.search(r'\bX([-+]?\d+\.?\d*)', line, re.IGNORECASE)
                y_match = re.search(r'\bY([-+]?\d+\.?\d*)', line, re.IGNORECASE)
                z_match = re.search(r'\bZ([-+]?\d+\.?\d*)', line, re.IGNORECASE)
                
                if x_match:
                    x = float(x_match.group(1))
                    if not (bounds['x']['min'] <= x <= bounds['x']['max']):
                        logger.warning(f"Line {i+1}: X coordinate out of bounds: {x}")
                        violations += 1
                
                if y_match:
                    y = float(y_match.group(1))
                    if not (bounds['y']['min'] <= y <= bounds['y']['max']):
                        logger.warning(f"Line {i+1}: Y coordinate out of bounds: {y}")
                        violations += 1
                
                if z_match:
                    z = float(z_match.group(1))
                    if not (bounds['z']['min'] <= z <= bounds['z']['max']):
                        logger.warning(f"Line {i+1}: Z coordinate out of bounds: {z}")
                        violations += 1
            
            return violations == 0
        
        except Exception as e:
            logger.error(f"Failed to check bounds: {str(e)}")
            return False
    
    def validate_all(self, gcode: str) -> tuple:
        """
        Run all validation checks
        
        Args:
            gcode: G-code file content
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        try:
            logger.info("Running all validation checks")
            
            no_extrusion = self.check_no_extrusion(gcode)
            no_heating = self.check_no_heating(gcode)
            in_bounds = self.check_bounds(gcode)
            
            is_valid = no_extrusion and no_heating and in_bounds
            
            report = {
                'valid': is_valid,
                'no_extrusion': no_extrusion,
                'no_heating': no_heating,
                'in_bounds': in_bounds,
                'checks_passed': sum([no_extrusion, no_heating, in_bounds]),
                'checks_total': 3,
            }
            
            if is_valid:
                logger.info("All validation checks passed ✓")
            else:
                logger.warning("Some validation checks failed")
            
            return is_valid, report
        
        except Exception as e:
            error_msg = f"Failed to validate G-code: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
