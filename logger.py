# In a file called logger.py
import logging
import os
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[93m',  # YELLOW
        'ERROR': '\033[91m',  # RED
        'WARNING': '\033[93m',  # YELLOW
        'CRITICAL': '\033[91m',  # RED
        'DEBUG': '\033[94m',  # BLUE
        'RESET': '\033[0m'    # RESET
    }

    def format(self, record):
        log_message = super().format(record)
        levelname = record.levelname
        if levelname in self.COLORS:
            return f"{self.COLORS[levelname]}{log_message}{self.COLORS['RESET']}"
        return log_message

def setup_logger():
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler("bot.log")
    file_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(asctime)s - %(message)s',
        '%d-%m %H:%M'
    ))
    
    # Create console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(
        '%(levelname)s - %(asctime)s - %(message)s',
        '%d-%m %H:%M'
    ))
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create a global logger instance
logger = setup_logger()