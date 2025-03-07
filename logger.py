# In a file called logger.py
import logging
import os
from datetime import datetime

def setup_logger():
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(asctime)s - %(message)s',
        datefmt='%d-%m %H:%M',
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )
    
    # Return the logger
    return logging.getLogger()

# Create a global logger instance
logger = setup_logger()