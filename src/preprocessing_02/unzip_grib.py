"""
Stage 2: Unzip ERA5 Monthly ZIP Bundles (Branch 2)
==================================================

Purpose
-------
This module performs the optional ZIP → GRIB extraction step for Stage 2.
Although Branch 2 Stage 1 now produces GRIB-only files, Stage 2 retains ZIP
support for backward compatibility, regression stability, and future ZIP-based
ingestion workflows.

Behavior
--------
- Recursively scan data/raw/era5/** for monthly ERA5 ZIP archives.
- Extract contained GRIB files into:
      data/raw/era5/<year>/<month>/<variable>/
- Normalize filenames to:
      <variable>_<year>_<month>.grib
- Safe no-op when no ZIP files are present.
- Extraction is idempotent and restart-safe.

IR Boundary
-----------
ZIP extraction operates at the GRIB (IR₀) layer. Extracted GRIB files are
diagnostic inputs for:
    - GRIB inspection (grib_metadata.json)
    - GRIB → Parquet conversion (IR₁)

ZIP extraction does *not* influence canonical Parquet metadata (metadata.json),
which is built exclusively from IR₁ Parquet files.
"""

import zipfile
from pathlib import Path

from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Extract a single ZIP → GRIB
# ------------------------------------------------------------------------------


def unzip_grib(zip_path: Path) -> Path:
    logger.info(f"[unzip] Extracting GRIB from {zip_path}")

    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    if zip_path.stat().st_size == 0:
        raise ValueError(f"ZIP file is empty: {zip_path}")

    # raw/era5/<year>/<month>/<variable>/<variable>_<year>_<month>.zip
    year = zip_path.parents[2].name
    month = zip_path.parents[1].name
    variable = zip_path.parents[0].name

    paths = Paths()
    out_dir = paths.raw_dir / year / month / variable
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        members = z.namelist()

        try:
            grib_name = next(m for m in members if m.endswith(".grib"))
        except StopIteration:
            raise ValueError(f"No GRIB file found inside ZIP: {zip_path}")

        extracted_path = out_dir / grib_name
        z.extract(grib_name, out_dir)

    normalized_name = f"{variable}_{year}_{month}.grib"
    normalized_path = out_dir / normalized_name

    if extracted_path != normalized_path:
        extracted_path.rename(normalized_path)

    logger.info(f"[unzip] GRIB extracted → {normalized_path}")
    return normalized_path


# ------------------------------------------------------------------------------
# Extract all ZIP files recursively under raw_dir
# ------------------------------------------------------------------------------


def unzip_all_months() -> list[Path]:
    paths = Paths()
    era5_dir = paths.raw_dir

    zip_files = sorted(era5_dir.rglob("*.zip"))
    logger.info(f"[unzip] Found {len(zip_files)} ZIP files")

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
# Stage 2 public API entrypoint
# ------------------------------------------------------------------------------


def main():
    try:
        unzip_all_months()
    except Exception as e:
        logger.error(f"[unzip] main() failed: {e}")
        raise


if __name__ == "__main__":
    main()
