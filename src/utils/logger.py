"""
Logging system for debugging and information messages

Provides colored and formatted logging output.
"""

import logging
import sys
from pathlib import Path

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


class Logger:
    """Application logger with color support"""
    
    _loggers = {}
    _log_file = None
    
    @classmethod
    def get_logger(cls, name: str = "G-Code-Radio") -> logging.Logger:
        """
        Get or create logger instance
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """
        Create a new logger instance
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        # Only configure if not already configured
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            
            # Console handler with color support
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            if HAS_COLORLOG:
                formatter = colorlog.ColoredFormatter(
                    '%(log_color)s[%(levelname)-8s]%(reset)s %(name)s - %(message)s',
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                )
            else:
                formatter = logging.Formatter(
                    '[%(levelname)-8s] %(name)s - %(message)s'
                )
            
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # File handler (optional)
            if cls._log_file:
                file_handler = logging.FileHandler(cls._log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    '%(asctime)s [%(levelname)-8s] %(name)s - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
        
        return logger
    
    @classmethod
    def setup_logging(cls, level: str = "INFO", log_file: str = None):
        """
        Setup logging configuration
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
        """
        # Update log file
        if log_file:
            cls._log_file = log_file
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Update root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Reconfigure all existing loggers
        for logger in cls._loggers.values():
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))
            
            # Add file handler if needed
            if log_file and not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    '%(asctime)s [%(levelname)-8s] %(name)s - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
