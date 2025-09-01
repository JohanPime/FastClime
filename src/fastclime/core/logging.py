import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

from fastclime.config import settings

# Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# Create logs directory if it doesn't exist
LOGS_DIR = settings.DIR_LOGS
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_console_handler():
    """Returns a console handler."""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return console_handler


def get_file_handler(log_file: Path):
    """Returns a file handler that rotates daily."""
    file_handler = TimedRotatingFileHandler(log_file, when="midnight")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return file_handler


def get_logger(
    logger_name: str, log_file_name: str = "fastclime.log"
) -> logging.Logger:
    """Configures and returns a logger."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)

    # Add handlers only if they haven't been added yet
    if not logger.handlers:
        logger.addHandler(get_console_handler())
        logger.addHandler(get_file_handler(LOGS_DIR / log_file_name))

    # Prevents log messages from being propagated to the root logger
    logger.propagate = False

    return logger


# Example of a default logger
log = get_logger(__name__)
