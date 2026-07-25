"""
Logging utilities for the ERA5 pipeline.

Provides a unified logger configured with RichHandler for readable,
color‑enhanced console output. All pipeline modules should obtain their
logger via `get_logger(__name__)` to ensure consistent formatting and
log‑level behavior across Branch 1 and future branches.

This module intentionally configures only console logging. File logging,
JSON logging, and cloud logging will be introduced in later branches
once pipeline stability and artifact requirements are established.
"""

import logging
from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """
    Return a module‑specific logger with Rich formatting.

    Ensures:
    - consistent log formatting across all pipeline modules
    - readable, colorized output via RichHandler
    - no duplicate handlers when called multiple times

    Parameters
    ----------
    name : str
        The logger name, typically `__name__`.

    Returns
    -------
    logging.Logger
        A configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if get_logger() is called repeatedly
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[RichHandler(rich_tracebacks=True)],
        )

    return logger
