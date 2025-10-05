"""
Logging configuration for the FastAPI application.
"""

import sys

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure logging for the application using loguru.
    """
    # Remove default logger
    logger.remove()

    # Add console logging
    logger.add(
        sys.stderr,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Add file logging for production
    if not settings.debug:
        logger.add(
            "logs/app.log",
            format=settings.log_format,
            level=settings.log_level,
            rotation="1 day",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=False,  # Don't log sensitive data in production
        )

    # Log startup message
    logger.info(f"Logging configured for {settings.app_name} v{settings.app_version}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Debug mode: {settings.debug}")


def get_logger(name: str = None):
    """
    Get a logger instance with optional name.

    Args:
        name: Optional logger name

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
