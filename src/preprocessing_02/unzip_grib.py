"""
Unzip an ERA5 monthly ZIP file and extract the GRIB file inside.

Branch 1 note:
    This module is included for completeness but is *not* used in the
    Branch 1 pipeline. Branch 1 preprocessing operates only on the
    single-variable GRIB file downloaded directly by download_era5_single.py.
    Monthly ZIP ingestion will be activated in Branch 2.

Branch 1 functionality (placeholder):
    - Accept era5_YYYY_MM.zip from data/raw/era5/
    - Extract the single .grib file inside
    - Save it to the same directory
    - Log the action

Branch 2 will add:
    - validation (file exists, non-empty)
    - metadata tracking
    - parallel extraction
    - checksum verification
    - multi-variable ZIP ingestion
"""

import zipfile
from pathlib import Path

from src.utils.paths import Paths
from src.utils.logging import get_logger

logger = get_logger(__name__)


def unzip_grib(zip_path: Path) -> Path:
    """
    Extract the GRIB file from a monthly ERA5 ZIP archive.

    Parameters
    ----------
    zip_path : Path
        Path to era5_YYYY_MM.zip

    Returns
    -------
    Path
        Path to the extracted .grib file
    """

    logger.info(f"Unzipping GRIB file from {zip_path}")

    # Resolve ERA5 directory
    paths = Paths()
    era5_dir = paths.raw_dir
    era5_dir.mkdir(parents=True, exist_ok=True)

    # Extract
    with zipfile.ZipFile(zip_path, "r") as z:
        members = z.namelist()

        # Branch 1 assumption: exactly one GRIB file inside
        grib_name = next(m for m in members if m.endswith(".grib"))

        extracted_path = era5_dir / grib_name
        z.extract(grib_name, era5_dir)

    # Normalize filename: rename "data.grib" → "era5_YYYY_MM.grib"
    parts = zip_path.stem.split("_")
    year = parts[1]
    month = parts[2]
    normalized_name = f"era5_{year}_{month}.grib"
    normalized_path = era5_dir / normalized_name

    if extracted_path != normalized_path:
        extracted_path.rename(normalized_path)

    logger.info(f"Extracted GRIB file → {normalized_path}")
    return normalized_path


def main():
    """
    Optional CLI entrypoint for manual testing.

    Branch 1 note:
        This CLI is not used in the Branch 1 pipeline. It is provided only
        for manual debugging and will be expanded in Branch 2.
    """
    paths = Paths()
    era5_dir = paths.raw_dir

    for zip_file in era5_dir.glob("*.zip"):
        unzip_grib(zip_file)


if __name__ == "__main__":
    main()