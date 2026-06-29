"""
Lightweight data validation utilities for the ERA5 Branch 1 pipeline.

Branch 1 keeps validation intentionally minimal:
- file exists
- file is non‑empty
- basic GRIB and Parquet checks (no schema validation)

This module is designed for quick, fail‑fast checks during ingestion and
conversion steps. Branch 2 will introduce richer validation such as:
- GRIB variable/schema checks
- Parquet column/type validation
- batch validation for multi‑variable ingestion
"""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_file_exists(path: str | Path) -> None:
    """
    Ensure a file exists before attempting to read it.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the path exists but is not a file.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing required file: {p}")
    if not p.is_file():
        raise ValueError(f"Expected a file but found a directory: {p}")
    logger.debug(f"Validated file exists: {p}")


def validate_nonempty(path: str | Path) -> None:
    """
    Ensure a file is not empty (common issue with failed downloads).

    Raises
    ------
    ValueError
        If the file is empty.
    """
    p = Path(path)
    if p.stat().st_size == 0:
        raise ValueError(f"File is empty: {p}")
    logger.debug(f"Validated file non-empty: {p}")


def validate_grib(path: str | Path) -> None:
    """
    Basic GRIB validation for Branch 1:
    - file exists
    - file is non-empty

    (Full GRIB readability checks are introduced in Branch 2.)
    """
    validate_file_exists(path)
    validate_nonempty(path)


def validate_parquet(path: str | Path) -> None:
    """
    Basic Parquet validation for Branch 1:
    - file exists
    - file is non-empty

    (Full Parquet schema validation is introduced in Branch 2.)
    """
    validate_file_exists(path)
    validate_nonempty(path)


def validate(path: str | Path) -> None:
    """
    Unified validator for Branch 1.

    Determines file type by extension and applies the appropriate checks.

    Supported:
    - .grib / .grb
    - .parquet

    Raises
    ------
    ValueError
        If the file extension is unsupported.
    """
    suffix = Path(path).suffix.lower()

    if suffix in [".grib", ".grb"]:
        validate_grib(path)
    elif suffix == ".parquet":
        validate_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Validate a GRIB or Parquet file.")
    parser.add_argument("path", nargs="?", help="Path to file to validate")

    args = parser.parse_args()

    if args.path is None:
        logger.info("No file provided. Nothing to validate.")
        sys.exit(0)

    validate(args.path)
    logger.info("Validation passed.")