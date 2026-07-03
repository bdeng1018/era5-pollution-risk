"""
Inspect ERA5 GRIB files (Branch 1 + Branch 2)

Overview
--------
This module provides two inspection paths:

1. Branch 1 (single-variable GRIBs)
    - Safe to open with cfgrib
    - Produced by download_era5_single.py
    - Naming convention: <variable_name>_<year>_<month>.grib
    - Used for early smoke tests and simple pipelines

2. Branch 2 (multi-variable monthly GRIBs)
    - Produced by unzip_grib.py from monthly ZIPs
    - May contain multiple variables and conflicting time coordinates
    - Cannot always be opened directly with cfgrib
    - Requires lightweight metadata extraction instead of full dataset loading

Branch 2 adds:
    - Multi-variable GRIB inspection
    - Schema + variable presence checks
    - Metadata extraction (variables, dims, coords, file size)
    - Robust error handling
    - Unified inspection entrypoint for Stage 2 preprocessing
"""

from pathlib import Path

import xarray as xr

from src.utils.logging import get_logger

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

    Examples:
        2m_temperature_2023_09.grib      → valid
        u_component_of_wind_2022_12.grib → valid
        data.grib                        → invalid
        era5_2023_09.grib                → invalid (monthly ZIP extraction)
    """

    parts = path.stem.split("_")
    if len(parts) < 3:
        return False

    year = parts[-2]
    month = parts[-1]

    return year.isdigit() and month.isdigit()


# ------------------------------------------------------------------------------
# Branch 1: Single-variable GRIB inspection
# ------------------------------------------------------------------------------

def inspect_grib_single(grib_path: Path):
    """
    Branch 1: Open and inspect a single-variable GRIB file.

    Returns
    -------
    xarray.Dataset or None
        The opened dataset, or None if the file is not single-variable.
    """

    if not is_single_variable_grib(grib_path):
        logger.warning(f"[inspect] Skipping non-single-variable GRIB (Branch 1): {grib_path.name}")
        return None

    logger.info(f"[inspect] Opening single-variable GRIB: {grib_path}")

    try:
        ds = xr.open_dataset(grib_path, engine="cfgrib")
    except Exception as e:
        logger.error(f"[inspect] Failed to open {grib_path}: {e}")
        return None

    logger.info("[inspect] GRIB opened successfully.")
    logger.info(f"[inspect] Dimensions: {ds.dims}")
    logger.info(f"[inspect] Variables: {list(ds.data_vars)}")

    return ds


# ------------------------------------------------------------------------------
# Branch 2: Multi-variable GRIB inspection
# ------------------------------------------------------------------------------

def inspect_grib_multi(grib_path: Path) -> dict:
    """
    Branch 2: Inspect multi-variable monthly GRIBs.

    Returns lightweight metadata:
        - variables
        - dimensions
        - coordinates
        - file size
        - error (if any)

    Returns
    -------
    dict
        Metadata describing the GRIB file.
    """

    logger.info(f"[inspect] Inspecting multi-variable GRIB: {grib_path}")

    try:
        ds = xr.open_dataset(grib_path, engine="cfgrib")
    except Exception as e:
        logger.error(f"[inspect] Failed to open multi-variable GRIB {grib_path}: {e}")
        return {
            "path": str(grib_path),
            "error": str(e),
            "variables": [],
            "dims": {},
            "coords": [],
            "size_bytes": grib_path.stat().st_size,
        }

    metadata = {
        "path": str(grib_path),
        "variables": list(ds.data_vars),
        "dims": dict(ds.dims),
        "coords": list(ds.coords),
        "size_bytes": grib_path.stat().st_size,
    }

    logger.info(f"[inspect] Variables: {metadata['variables']}")
    return metadata


# ------------------------------------------------------------------------------
# Unified Branch 2 entrypoint
# ------------------------------------------------------------------------------

def inspect_all_gribs(raw_dir: Path | str) -> list[dict]:
    """
    Inspect ALL GRIB files in a directory (Branch 2 unified entrypoint).

    This function supports BOTH Branch 1 and Branch 2 GRIB formats:

    Branch 1 (single-variable GRIBs)
    --------------------------------
    - Naming convention: <variable_name>_<year>_<month>.grib
    - Safe to open with cfgrib
    - Used for early smoke tests and simple pipelines
    - We attempt full dataset loading via inspect_grib_single()

    Branch 2 (multi-variable monthly GRIBs)
    ---------------------------------------
    - Naming convention: era5_<year>_<month>.grib
    - Produced by unzip_grib.py
    - May contain multiple variables and conflicting time coordinates
    - Cannot always be opened with cfgrib
    - We extract lightweight metadata via inspect_grib_multi()

    Stage 2 Contract
    ----------------
    - raw_dir may be a STRING (Paths.raw_dir) or a Path object
    - We MUST convert to Path before filesystem operations
    - Tests expect returned metadata to contain string paths

    Parameters
    ----------
    raw_dir : Path or str
        Directory containing GRIB files. May come from Paths.raw_dir (string).

    Returns
    -------
    list[dict]
        A list of metadata dictionaries describing each GRIB file.
        For single-variable GRIBs:
            {
                "path": "...",
                "single_var": True,
                "opened": True/False
            }
        For multi-variable GRIBs:
            {
                "path": "...",
                "variables": [...],
                "dims": {...},
                "coords": [...],
                "size_bytes": int,
                "error": None or str
            }
    """

    # ⭐ Stage 2 contract: raw_dir may be a string → convert to Path
    raw_dir = Path(raw_dir)

    # Discover all GRIB files
    grib_files = sorted(raw_dir.glob("*.grib"))
    logger.info(f"[inspect] Found {len(grib_files)} GRIB files in {raw_dir}")

    results = []

    for grib_path in grib_files:

        # Branch 1 path: single-variable GRIBs
        if is_single_variable_grib(grib_path):
            ds = inspect_grib_single(grib_path)
            results.append({
                "path": str(grib_path),
                "single_var": True,
                "opened": ds is not None,
            })
            continue

        # Branch 2 path: multi-variable GRIBs
        meta = inspect_grib_multi(grib_path)
        results.append(meta)

    return results


# ------------------------------------------------------------------------------
# CLI (Branch 1 behavior preserved)
# ------------------------------------------------------------------------------

def main():
    """
    Branch 1 CLI: inspect only single-variable GRIB files.

    Multi-variable monthly GRIBs contain conflicting time coordinates
    and cannot be inspected in Branch 1.
    """

    era5_dir = Path("data/raw/era5")

    if not era5_dir.exists():
        logger.error("ERA5 directory not found: data/raw/era5")
        return

    single_var_gribs = sorted(
        p for p in era5_dir.glob("*.grib")
        if is_single_variable_grib(p)
    )

    if not single_var_gribs:
        logger.warning("No single-variable GRIB files found for inspection.")
        return

    logger.info(f"Found {len(single_var_gribs)} single-variable GRIB file(s).")

    for grib_path in single_var_gribs:
        logger.info(f"--- Inspecting {grib_path.name} ---")
        inspect_grib_single(grib_path)


if __name__ == "__main__":
    main()
