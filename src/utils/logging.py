"""
Logging utilities for the ERA5 pipeline (Branch 2)

Provides a unified logger configured with RichHandler for readable,
color‑enhanced console output. All deterministic pipeline modules should
obtain their logger via `get_logger(__name__)` to ensure consistent
formatting and log‑level behavior across Branch 2 and future branches.

Branch 2 Note
-------------
Logging is intentionally minimal and console‑only. This keeps ingestion,
preprocessing, chunking, and IR₄ compilation free of side effects and
safe during pytest collection.

Branch 3 Note
-------------
Future AI/LLM/RAG components may introduce optional file logging, JSON
logging, or cloud logging. These will live in separate modules to avoid
changing deterministic logging behavior for Branch 2.

Invariant
---------
This initializer must remain side‑effect‑free:
- no global logging configuration beyond RichHandler
- no file I/O
- no heavy imports
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
