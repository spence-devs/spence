import logging


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f"spence.{name}")


def set_log_level(level: str) -> None:
    """Set global log level"""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger("spence").setLevel(numeric_level)
