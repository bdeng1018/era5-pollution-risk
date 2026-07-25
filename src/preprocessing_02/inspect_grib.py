"""
Inspect a GRIB file using xarray + cfgrib.

Branch 1 functionality:
    - Open a single-variable GRIB file with xarray
    - Print basic metadata (dimensions, variables)
    - Log the action
    - Return the dataset object for downstream use

Branch 1 note:
    Only the single-variable GRIB produced by download_era5_single.py is
    safe to inspect in Branch 1. Multi-variable monthly GRIBs contain
    conflicting time coordinates and cannot be loaded by cfgrib.

Branch 2 will add:
    - schema validation
    - variable presence checks
    - metadata extraction
    - error handling and retries
    - multi-variable GRIB inspection
"""

import xarray as xr
from pathlib import Path

from src.utils.logging import get_logger

logger = get_logger(__name__)


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


def inspect_grib(grib_path: Path):
    """
    Open and inspect a GRIB file.

    Parameters
    ----------
    grib_path : Path
        Path to a .grib file

    Returns
    -------
    xarray.Dataset
        The opened dataset
    """

    logger.info(f"Inspecting GRIB file: {grib_path}")

    # Branch 1: enforce single-variable rule
    if not is_single_variable_grib(grib_path):
        logger.warning(
            f"Skipping non-single-variable GRIB (Branch 1): {grib_path.name}"
        )
        return None

    # Minimal open
    ds = xr.open_dataset(grib_path, engine="cfgrib")

    # Print basic metadata
    logger.info("GRIB file opened successfully.")
    logger.info(f"Dimensions: {ds.dims}")
    logger.info(f"Variables: {list(ds.data_vars)}")

    return ds


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

    # Find only single-variable GRIBs
    single_var_gribs = sorted(
        p for p in era5_dir.glob("*.grib") if is_single_variable_grib(p)
    )

    if not single_var_gribs:
        logger.warning("No single-variable GRIB files found for inspection.")
        return

    logger.info(f"Found {len(single_var_gribs)} single-variable GRIB file(s).")

    for grib_path in single_var_gribs:
        logger.info(f"--- Inspecting {grib_path.name} ---")
        inspect_grib(grib_path)


if __name__ == "__main__":
    main()
