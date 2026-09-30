"""
logger.py
Sets up a simple logger that writes execution info, warnings, and
errors to app.log. Used by every other module in the project.
"""

import logging

LOG_FILE = "app.log"


def setup_logger():
    """
    Creates and returns a logger object.
    Logs go to app.log (file) and also print WARNING+ to console.
    """
    logger = logging.getLogger("flight_eval")
    logger.setLevel(logging.DEBUG)

    # avoid adding duplicate handlers if setup_logger() is called twice
    if logger.handlers:
        return logger

    # file handler - logs everything (DEBUG and up)
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # console handler - only show warnings/errors so terminal stays clean
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_format = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
