"""
Logging utilities for Rosecrypt.

Provides category-based filtering and consistent formatting across
file and console log outputs. Console logging supports colored output
using the `colorlog` module.

Usage:
    from rosecrypt.logger import setup_logger
    log = setup_logger(__name__, category="Rendering")
"""

import logging
from typing import Optional
import colorlog

# pylint: disable=too-few-public-methods
class CategoryFilter(logging.Filter):
    """
    A logging filter that restricts log messages to a specific category.

    Attributes:
        category (Optional[str]): The category to filter by. If None, all records are allowed.
    """
    def __init__(self, category: Optional[str] = None):
        """
        A logging filter that restricts log messages to a specific category.

        Attributes:
            category (Optional[str]): The category to filter by. If None, all records are allowed.
        """
        super().__init__()
        self.category = category

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Determines whether a log record should be emitted based on its category.

        :param record: The log record to evaluate.
        :type record: logging.LogRecord
        :return: True if the record matches the category or if no category is set.
        :rtype: bool
        """
        if self.category is None:
            return True
        return getattr(record, "category", None) == self.category

def setup_logger(name: str, category: str = "General") -> logging.Logger:
    """
    Sets up a logger with colored console output and category-aware formatting.

    This logger logs all messages to a file (debug and above) and outputs
    info-level and above to the console using colored formatting.
    The `category` is injected into each log record.

    :param name: The name of the logger, usually `__name__`.
    :type name: str
    :param category: The category label to associate with log messages.
    :type category: str
    :return: A configured logger instance.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger  # Prevent duplicate handlers

    logger.setLevel(logging.DEBUG)  # Master level (can be filtered per handler)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(category)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # === File handler ===
    file_handler = logging.FileHandler("rosecrypt.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # === Console handler with colorlog ===
    color_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s] [%(levelname)s] [%(category)s] %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
    )

    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Console shows less than file
    console_handler.setFormatter(color_formatter)

    # Attach
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Inject category into logs automatically
    def inject_category(record):
        record.category = category
        return True

    logger.addFilter(inject_category)

    return logger
