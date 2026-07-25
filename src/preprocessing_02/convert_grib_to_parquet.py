"""
Convert a GRIB file to Parquet using xarray + pandas.

Branch 1 functionality:
    - Open single-variable GRIBs with xarray (cfgrib engine)
    - Convert to pandas DataFrame
    - Save to Parquet in data/intermediate/
    - Log basic metadata

Branch 1 note:
    Only the single-variable GRIB produced by download_era5_single.py is
    safe to convert in Branch 1. Multi-variable monthly GRIBs contain
    conflicting time coordinates and cannot be opened by cfgrib.

Branch 2 will add:
    - schema validation
    - metadata extraction
    - multi-file batching
    - parallel conversion
    - error handling and retries
"""

import xarray as xr
from pathlib import Path

from src.utils.logging import get_logger
from src.utils.paths import Paths

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


def convert_grib_to_parquet(grib_path: Path) -> Path | None:
    """
    Convert a GRIB file to Parquet.

    Parameters
    ----------
    grib_path : Path
        Path to a .grib file

    Returns
    -------
    Path or None
        Path to the saved Parquet file, or None if skipped.
    """

    logger.info(f"Converting GRIB → Parquet: {grib_path}")

    # Branch 1: enforce single-variable rule
    if not is_single_variable_grib(grib_path):
        logger.warning(
            f"Skipping non-single-variable GRIB (Branch 1): {grib_path.name}"
        )
        return None

    # Resolve intermediate directory
    paths = Paths()
    intermediate_dir = paths.intermediate_dir
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    # Open GRIB file
    ds = xr.open_dataset(grib_path, engine="cfgrib")

    # Convert to pandas DataFrame
    df = ds.to_dataframe().reset_index()

    # Output file
    parquet_path = intermediate_dir / f"{grib_path.stem}.parquet"

    # Save Parquet
    df.to_parquet(parquet_path, index=False)

    logger.info(f"Saved Parquet file → {parquet_path}")
    logger.info(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    return parquet_path


def main():
    """
    Branch 1 CLI: convert only single-variable GRIBs.

    Multi-variable monthly GRIBs contain conflicting time coordinates
    and cannot be converted in Branch 1.
    """

    paths = Paths()
    era5_dir = paths.raw_dir

    # Find only single-variable GRIBs
    single_var_gribs = sorted(
        p for p in era5_dir.glob("*.grib") if is_single_variable_grib(p)
    )

    if not single_var_gribs:
        logger.warning("No single-variable GRIB files found for conversion.")
        return

    logger.info(f"Found {len(single_var_gribs)} single-variable GRIB file(s).")

    for grib_path in single_var_gribs:
        convert_grib_to_parquet(grib_path)


if __name__ == "__main__":
    main()
