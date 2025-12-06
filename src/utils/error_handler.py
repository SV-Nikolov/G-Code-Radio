"""
Error handling and custom exceptions

Provides application-specific exception classes.
"""

from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


class GCodeRadioException(Exception):
    """Base exception for G-Code Radio"""
    pass


class AudioDownloadError(GCodeRadioException):
    """Error downloading audio from YouTube"""
    pass


class AudioProcessingError(GCodeRadioException):
    """Error processing audio file"""
    pass


class PitchDetectionError(GCodeRadioException):
    """Error detecting pitch from audio"""
    pass


class NoteDetectionError(GCodeRadioException):
    """Error converting pitch to notes"""
    pass


class GCodeGenerationError(GCodeRadioException):
    """Error generating G-code"""
    pass


class BoundsViolationError(GCodeRadioException):
    """Movement exceeds printer bounds"""
    pass


class ValidationError(GCodeRadioException):
    """Validation check failed"""
    pass


class InvalidParameterError(GCodeRadioException):
    """Invalid parameter value"""
    pass


def handle_error(error: Exception, user_message: str = None) -> str:
    """
    Handle exception and generate user-friendly message
    
    Args:
        error: Exception object
        user_message: Custom user message
        
    Returns:
        User-friendly error message
    """
    error_type = type(error).__name__
    error_details = str(error)
    
    # Log the error
    logger.error(f"{error_type}: {error_details}")
    
    # Generate user-friendly message
    if user_message:
        return f"{user_message}\nDetails: {error_details}"
    else:
        error_messages = {
            'AudioProcessingError': "Failed to process audio file. Please ensure the file is valid.",
            'PitchDetectionError': "Failed to detect pitch from audio.",
            'NoteDetectionError': "Failed to convert pitch to musical notes.",
            'GCodeGenerationError': "Failed to generate G-code.",
            'BoundsViolationError': "Movement exceeds printer bounds.",
            'ValidationError': "Validation failed. Please check your input.",
            'InvalidParameterError': "Invalid parameter value.",
        }
        
        base_message = error_messages.get(error_type, "An error occurred.")
        return f"{base_message}\nDetails: {error_details}"
