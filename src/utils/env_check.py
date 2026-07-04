"""
Environment validation utilities for the ERA5 pipeline (Branch 2).

This module performs lightweight, fail‑fast checks to ensure the runtime
environment is correctly configured for ingestion and preprocessing:

- Python version (3.10+ required for cfgrib/eccodes compatibility)
- Required packages (xarray, cfgrib, pyarrow, pandas, numpy)
- Minimal directory checks (configs/, raw/)

Branch 2 intentionally keeps environment validation minimal. Heavy validation
(e.g., GRIB schema checks, parquet integrity checks, extended directory
structure) is handled inside Stage 2 modules, not here.
"""

import logging
import sys
from importlib.util import find_spec
from pathlib import Path

logger = logging.getLogger(__name__)


def check_python_version(min_major: int = 3, min_minor: int = 10):
    """
    Validate that the active Python interpreter meets the minimum version.

    Raises
    ------
    RuntimeError
        If the interpreter version is below the required minimum.
    """
    if sys.version_info < (min_major, min_minor):
        raise RuntimeError(
            f"Python {min_major}.{min_minor}+ required. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
        )


def check_package(pkg: str):
    """
    Validate that a required package is installed and importable.

    Parameters
    ----------
    pkg : str
        The package name to check.

    Raises
    ------
    ImportError
        If the package cannot be found.
    """
    if find_spec(pkg) is None:
        raise ImportError(f"Required package not installed: {pkg}")


def check_directory(path: str | Path):
    """
    Validate that a required directory exists and is accessible.

    Parameters
    ----------
    path : str or Path
        Directory path to validate.

    Raises
    ------
    FileNotFoundError
        If the directory does not exist.
    NotADirectoryError
        If the path exists but is not a directory.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Required directory missing: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Expected a directory but found a file: {p}")


def validate_environment():
    """
    Run all environment checks required for Branch 1.

    Checks:
    - Python version
    - Required packages
    - Required directories
    """
    check_python_version()

    required_packages = [
        "xarray",
        "cfgrib",
        "pyarrow",
        "pandas",
        "numpy",
    ]

    for pkg in required_packages:
        check_package(pkg)

    check_directory("data/raw/era5")
    check_directory("configs")


if __name__ == "__main__":
    # Prevent duplicate handlers if env_check is run multiple times
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    validate_environment()
    logger.info("Environment validation passed.")
