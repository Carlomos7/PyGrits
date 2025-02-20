import logging
import sys
from pathlib import Path
from typing import Optional
from colorama import init, Fore, Style

# Initialize colorama
init()


class ColoredFormatter(logging.Formatter):
    """Custom logging formatter that adds color to log messages."""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):

        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
            )
        return super().format(record)


def setup_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """Set up and configure logger instance.

    Args:
        name: Logger name
        log_file: Optional path to log file

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    console_formatter = ColoredFormatter("%(levelname)s - %(message)s")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


# Create default logger
logger = setup_logger("pygrits")
