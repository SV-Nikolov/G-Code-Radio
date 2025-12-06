"""
Generate G-code commands from movement instructions

Converts movement data to actual G-code format.
"""

import os
from datetime import datetime
from src.utils.logger import Logger
from src.utils.error_handler import GCodeGenerationError

logger = Logger.get_logger(__name__)


class GCodeGenerator:
    """Generates G-code from movement instructions"""
    
    def __init__(self, printer_config):
        """
        Initialize the G-code generator
        
        Args:
            printer_config: Printer configuration object
        """
        self.printer_config = printer_config
    
    def generate_gcode_header(self, title: str = "G-Code Radio Song") -> str:
        """
        Generate G-code file header with safety settings
        
        Args:
            title: Song or file title
            
        Returns:
            G-code header string
        """
        try:
            header = f"""; G-Code Radio - 3D Printer Music Player
; Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
; Title: {title}
;
; SAFETY NOTICE:
; - This is a movement-only file (NO EXTRUSION)
; - NO heating commands (bed or hotend)
; - Movement limited to printer bounds
; - Safe for Moment S1 (2014) printer
;

; Reset all systems
G90                                    ; Set to absolute positioning
G28                                    ; Home all axes
G92 X100 Y100 Z100                     ; Set home position

; Disable motors after homing
M18                                    ; Disable steppers (optional)
G04 P1000                              ; Wait 1 second

; Start movement sequence
"""
            return header
        
        except Exception as e:
            error_msg = f"Failed to generate header: {str(e)}"
            logger.error(error_msg)
            raise GCodeGenerationError(error_msg)
    
    def movement_to_gcode(self, movement: dict, current_pos: list) -> str:
        """
        Convert single movement instruction to G-code
        
        Args:
            movement: Movement instruction dictionary
            current_pos: Current position [x, y, z]
            
        Returns:
            G-code command string
        """
        try:
            axis = movement.get('axis', 'X')
            distance = movement.get('distance', 0)
            feedrate = movement.get('feedrate', 1000)
            duration = movement.get('duration', 0)
            
            # Calculate new position
            axis_index = {'X': 0, 'Y': 1, 'Z': 2}.get(axis, 0)
            new_pos = current_pos.copy()
            new_pos[axis_index] += distance
            
            # Clamp to bounds
            bounds = self.printer_config.get_safe_bounds()
            axis_name = ['x', 'y', 'z'][axis_index]
            new_pos[axis_index] = max(
                bounds[axis_name]['min'],
                min(bounds[axis_name]['max'], new_pos[axis_index])
            )
            
            # Generate G1 move command
            gcode = f"G1 {axis}{new_pos[axis_index]:.2f} F{feedrate:.0f}"
            
            return gcode
        
        except Exception as e:
            error_msg = f"Failed to convert movement to G-code: {str(e)}"
            logger.error(error_msg)
            raise GCodeGenerationError(error_msg)
    
    def movements_to_gcode(self, movements: list, title: str = "Song") -> str:
        """
        Convert all movements to G-code file content
        
        Args:
            movements: List of movement instructions
            title: Song title
            
        Returns:
            Complete G-code file content
            
        Raises:
            GCodeGenerationError: If generation fails
        """
        try:
            logger.info(f"Generating G-code for {len(movements)} movements")
            
            gcode = self.generate_gcode_header(title)
            
            current_pos = list(self.printer_config.get_home_position())
            
            for i, movement in enumerate(movements):
                try:
                    gcode_line = self.movement_to_gcode(movement, current_pos)
                    gcode += gcode_line + "\n"
                    
                    # Update position tracking
                    axis = movement.get('axis', 'X')
                    axis_index = {'X': 0, 'Y': 1, 'Z': 2}.get(axis, 0)
                    distance = movement.get('distance', 0)
                    current_pos[axis_index] += distance
                    
                except Exception as e:
                    logger.warning(f"Failed to generate G-code for movement {i}: {str(e)}")
                    continue
            
            gcode += self.generate_gcode_footer()
            
            logger.info(f"G-code generation complete: {len(gcode)} characters")
            return gcode
        
        except Exception as e:
            error_msg = f"Failed to generate G-code: {str(e)}"
            logger.error(error_msg)
            raise GCodeGenerationError(error_msg)
    
    def generate_gcode_footer(self) -> str:
        """
        Generate G-code file footer (reset commands)
        
        Returns:
            G-code footer string
        """
        try:
            footer = f"""
; End of movement sequence
G28                                    ; Return home
M18                                    ; Disable steppers
; Song complete!
"""
            return footer
        
        except Exception as e:
            error_msg = f"Failed to generate footer: {str(e)}"
            logger.error(error_msg)
            raise GCodeGenerationError(error_msg)
    
    def write_gcode_file(self, movements: list, output_path: str, title: str = "Song") -> str:
        """
        Write G-code to file
        
        Args:
            movements: List of movement instructions
            output_path: Path to output G-code file
            title: Song title
            
        Returns:
            Path to written file
            
        Raises:
            GCodeGenerationError: If writing fails
        """
        try:
            logger.info(f"Writing G-code to: {output_path}")
            
            # Generate G-code
            gcode = self.movements_to_gcode(movements, title)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write(gcode)
            
            file_size = os.path.getsize(output_path)
            logger.info(f"G-code file written: {file_size} bytes")
            
            return output_path
        
        except Exception as e:
            error_msg = f"Failed to write G-code file: {str(e)}"
            logger.error(error_msg)
            raise GCodeGenerationError(error_msg)
