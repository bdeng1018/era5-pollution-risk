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
import os

from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """
    Return a module‑specific logger with Rich formatting.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[RichHandler(rich_tracebacks=True)],
        )

    return logger


def add_file_logging(log_path: str) -> None:
    """
    Optional file logging for stages that require persistent logs.

    This does NOT modify the global logging configuration and does NOT
    violate Branch 2 invariants. It simply attaches a file handler to
    the existing logger hierarchy.

    Parameters
    ----------
    log_path : str
        Path to the log file.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
