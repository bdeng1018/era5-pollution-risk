"""
Unzip ERA5 monthly ZIP files and extract GRIB files inside.

Branch 1:
    - Placeholder logic
    - Single GRIB inside each ZIP
    - No validation, no metadata

Branch 2:
    - Process ALL monthly ZIPs
    - Validate ZIP existence + non-empty
    - Extract GRIBs for every month
    - Normalize filenames (era5_YYYY_MM.grib)
    - Prepare for Stage 3 parallelization
"""

import zipfile
from pathlib import Path

from src.download_01.paths import Paths
from src.utils.logging import get_logger

logger = get_logger(__name__)


def unzip_grib(zip_path: Path) -> Path:
    logger.info(f"[unzip] Extracting GRIB from {zip_path}")

    zip_path = Path(zip_path)  # ⭐ ensure Path

    paths = Paths()
    era5_dir = Path(paths.raw_dir)  # ⭐ convert string → Path
    era5_dir.mkdir(parents=True, exist_ok=True)

    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    if zip_path.stat().st_size == 0:
        raise ValueError(f"ZIP file is empty: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as z:
        members = z.namelist()

        try:
            grib_name = next(m for m in members if m.endswith(".grib"))
        except StopIteration:
            raise ValueError(f"No GRIB file found inside ZIP: {zip_path}")

        extracted_path = era5_dir / grib_name
        z.extract(grib_name, era5_dir)

    parts = zip_path.stem.split("_")
    year = parts[1]
    month = parts[2]
    normalized_name = f"era5_{year}_{month}.grib"
    normalized_path = era5_dir / normalized_name

    if extracted_path != normalized_path:
        extracted_path.rename(normalized_path)

    logger.info(f"[unzip] GRIB extracted → {normalized_path}")
    return normalized_path


def unzip_all_months() -> list[Path]:
    paths = Paths()
    era5_dir = Path(paths.raw_dir)  # ⭐ convert string → Path

    zip_files = sorted(era5_dir.glob("era5_*.zip"))
    logger.info(f"[unzip] Found {len(zip_files)} monthly ZIP files")

    extracted = []

    for zip_file in zip_files:
        try:
            grib_path = unzip_grib(zip_file)
            extracted.append(grib_path)
        except Exception as e:
            logger.error(f"[unzip] Failed to extract {zip_file}: {e}")

    logger.info(f"[unzip] Successfully extracted {len(extracted)} GRIB files")
    return extracted


# ------------------------------------------------------------------------------
# ⭐ REQUIRED BY STAGE 2 PUBLIC API CONTRACT
# ------------------------------------------------------------------------------

def main():
    """
    Stage 2 required public API entrypoint.

    Tests require:
        - unzip_grib.main() must exist
        - unzip_grib.main() must be importable
        - unzip_grib.main() must call unzip_all_months()
        - unzip_grib.main() must not crash

    This is NOT a production CLI.
    It is a structural entrypoint required for Stage 2.
    """
    try:
        unzip_all_months()
    except Exception as e:
        logger.error(f"[unzip] main() failed: {e}")
        raise


if __name__ == "__main__":
    main()
