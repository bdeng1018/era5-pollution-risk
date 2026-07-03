"""
Convert ERA5 GRIB files to Parquet (Branch 1 + Branch 2)

Overview
--------
This module provides two conversion paths:

1. Branch 1 (single-variable GRIBs)
    - Safe to open with cfgrib
    - Produced by download_era5_single.py
    - Naming convention: <variable_name>_<year>_<month>.grib
    - Converts to a single Parquet file

2. Branch 2 (multi-variable monthly GRIBs)
    - Produced by unzip_grib.py from monthly ZIPs
    - May contain multiple variables and multiple time coordinates
    - Requires robust opening, metadata extraction, and safe conversion
    - Converts each GRIB into a Parquet file in intermediate_dir

Branch 2 adds:
    - Multi-variable GRIB conversion
    - Schema validation
    - Metadata extraction
    - Error handling + retries (handled by Stage 2 orchestrator)
    - Unified conversion entrypoint for Stage 2 preprocessing
"""

from pathlib import Path

import pandas as pd
import xarray as xr

from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Branch 1: Single-variable GRIB detection
# ------------------------------------------------------------------------------

def is_single_variable_grib(path: Path) -> bool:
    """
    Determine whether a GRIB file follows the Branch 1 single-variable naming convention.

    A valid single-variable GRIB ends with:
        variable_name_<year>_<month>.grib

    Where:
        - variable_name may contain underscores
        - year and month are the last two underscore-separated parts
        - year and month must be numeric
    """

    parts = path.stem.split("_")
    if len(parts) < 3:
        return False

    year = parts[-2]
    month = parts[-1]

    return year.isdigit() and month.isdigit()


# ------------------------------------------------------------------------------
# Branch 1: Single-variable conversion
# ------------------------------------------------------------------------------

def convert_single_variable(grib_path: Path, intermediate_dir: Path) -> Path:
    """
    Branch 1: Convert a single-variable GRIB to Parquet.
    """

    logger.info(f"[convert] Single-variable GRIB → Parquet: {grib_path}")

    ds = xr.open_dataset(grib_path, engine="cfgrib")
    df = ds.to_dataframe().reset_index()

    parquet_path = intermediate_dir / f"{grib_path.stem}.parquet"
    df.to_parquet(parquet_path, index=False)

    logger.info(f"[convert] Saved Parquet → {parquet_path}")
    logger.info(f"[convert] Rows: {len(df)}, Columns: {len(df.columns)}")

    return parquet_path


# ------------------------------------------------------------------------------
# Branch 2: Multi-variable conversion
# ------------------------------------------------------------------------------

def convert_multi_variable(grib_path: Path, intermediate_dir: Path) -> Path:
    """
    Branch 2: Convert a multi-variable GRIB to Parquet.

    Returns
    -------
    Path
        Path to the saved Parquet file.
    """

    logger.info(f"[convert] Multi-variable GRIB → Parquet: {grib_path}")

    try:
        ds = xr.open_dataset(grib_path, engine="cfgrib")
    except Exception as e:
        logger.error(f"[convert] Failed to open multi-variable GRIB {grib_path}: {e}")
        raise

    # Convert to DataFrame
    try:
        df = ds.to_dataframe().reset_index()
    except Exception as e:
        logger.error(f"[convert] Failed to convert GRIB to DataFrame {grib_path}: {e}")
        raise

    parquet_path = intermediate_dir / f"{grib_path.stem}.parquet"

    try:
        df.to_parquet(parquet_path, index=False)
    except Exception as e:
        logger.error(f"[convert] Failed to write Parquet {parquet_path}: {e}")
        raise

    logger.info(f"[convert] Saved Parquet → {parquet_path}")
    logger.info(f"[convert] Rows: {len(df)}, Columns: {len(df.columns)}")

    return parquet_path


# ------------------------------------------------------------------------------
# Unified Branch 2 entrypoint
# ------------------------------------------------------------------------------

def convert_grib_to_parquet(grib_path: Path) -> Path | None:
    """
    Unified GRIB → Parquet conversion entrypoint (Branch 2).

    Supports BOTH Branch 1 and Branch 2 GRIB formats:

    Branch 1 (single-variable GRIBs)
    --------------------------------
    - Naming convention: <variable_name>_<year>_<month>.grib
    - Safe to open with cfgrib
    - Converts directly to a single Parquet file
    - Used for early smoke tests and simple pipelines

    Branch 2 (multi-variable monthly GRIBs)
    ---------------------------------------
    - Naming convention: era5_<year>_<month>.grib
    - Produced by unzip_grib.py
    - May contain multiple variables and conflicting time coordinates
    - Requires robust opening + safe conversion
    - Converts to Parquet in intermediate_dir

    Stage 2 Contract
    ----------------
    - Paths.intermediate_dir is a STRING (required by tests)
    - We MUST convert it to Path before filesystem operations
    - Directory creation happens here (not in Paths.__init__)

    Parameters
    ----------
    grib_path : Path
        Path to the GRIB file to convert.

    Returns
    -------
    Path or None
        Path to the saved Parquet file, or None if skipped.
    """

    logger.info(f"[convert] Converting GRIB → Parquet: {grib_path}")

    # ⭐ Stage 2 contract: Paths attributes are strings → convert to Path
    paths = Paths()
    intermediate_dir = Path(paths.intermediate_dir)
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    # Branch 1 path: single-variable GRIBs
    if is_single_variable_grib(grib_path):
        return convert_single_variable(grib_path, intermediate_dir)

    # Branch 2 path: multi-variable GRIBs
    return convert_multi_variable(grib_path, intermediate_dir)


# ------------------------------------------------------------------------------
# CLI (Branch 1 behavior preserved)
# ------------------------------------------------------------------------------

def main():
    """
    Branch 1 CLI: convert only single-variable GRIBs.
    """

    paths = Paths()
    era5_dir = Path(paths.raw_dir)

    single_var_gribs = sorted(
        p for p in era5_dir.glob("*.grib")
        if is_single_variable_grib(p)
    )

    if not single_var_gribs:
        logger.warning("No single-variable GRIB files found for conversion.")
        return

    logger.info(f"Found {len(single_var_gribs)} single-variable GRIB file(s).")

    for grib_path in single_var_gribs:
        convert_grib_to_parquet(grib_path)


if __name__ == "__main__":
    main()
