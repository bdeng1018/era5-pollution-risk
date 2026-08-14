"""
Environment validation utilities for the ERA5 pipeline (Branch 1).

This module performs lightweight, fail-fast checks to ensure the runtime
environment is correctly configured:

- Python version (3.10+ required for cfgrib/eccodes compatibility)
- Required packages (xarray, cfgrib, pyarrow, pandas, numpy, netCDF4, scipy)
- Required directories (data/raw/era5, configs)
- Interpreter is the project .venv (recommended)
- Warn if a Conda environment is active

These checks are intentionally minimal for Branch 1.
"""

import importlib.util
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


# ==============================================================================
# Python version check
# ==============================================================================
def check_python_version(min_major: int = 3, min_minor: int = 10):
    if sys.version_info < (min_major, min_minor):
        raise RuntimeError(
            f"Python {min_major}.{min_minor}+ required. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
        )


# ==============================================================================
# Package import check
# ==============================================================================
def check_package(pkg: str):
    if importlib.util.find_spec(pkg) is None:
        raise ImportError(f"Required package not installed: {pkg}")


# ==============================================================================
# Directory existence check
# ==============================================================================
def check_directory(path: str | Path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Required directory missing: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Expected a directory but found a file: {p}")


# ==============================================================================
# Virtual environment check
# ==============================================================================
def check_venv(expected: str = ".venv"):
    # Skip venv enforcement in CI
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return

    interpreter = Path(sys.executable).resolve()
    if expected not in interpreter.as_posix():
        raise RuntimeError(
            f"Active interpreter is not the project venv: {interpreter}\n"
            f"Activate it first:\n\n    source {expected}/bin/activate\n"
        )


# ==============================================================================
# Conda warning (non-fatal)
# ==============================================================================
def warn_if_conda():
    if "CONDA_PREFIX" in os.environ:
        logger.warning(
            "Conda environment detected. ERA5 Branch 1 uses a local .venv.\n"
            "Deactivate conda and activate the project venv:\n\n"
            "    conda deactivate\n"
            "    source .venv/bin/activate\n"
        )


# ==============================================================================
# Main validation routine
# ==============================================================================
def validate_environment():
    logger.info("Validating Python version...")
    check_python_version()

    logger.info("Checking required Python packages...")

    required_packages = [
        # Core scientific stack
        "numpy",
        "pandas",
        "xarray",
        "netCDF4",
        "scipy",
        # ERA5 + climate tools
        "cfgrib",
        "eccodes",
        # Parquet
        "pyarrow",
        # Utilities
        "tqdm",
        "requests",
        "rich",
    ]

    for pkg in required_packages:
        check_package(pkg)

    logger.info("Checking directory structure...")

    required_dirs = [
        "data/raw/era5",
        "configs",
    ]

    for d in required_dirs:
        check_directory(d)

    warn_if_conda()
    check_venv()

    logger.info("Environment validation passed.")

    warn_if_conda()
    check_venv()


# ==============================================================================
# Script entrypoint
# ==============================================================================
if __name__ == "__main__":
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    validate_environment()
