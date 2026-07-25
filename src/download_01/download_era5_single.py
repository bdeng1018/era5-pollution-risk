"""
Stage 1: Branch 2 Single‑Variable ERA5 Downloader
=================================================

Purpose
-------
This module downloads single‑variable ERA5 GRIB files directly from CDSAPI
using the Branch 2 ingestion architecture. It is designed to be deterministic,
monkeypatch‑friendly for testing, and fully aligned with config.yml‑driven
multi‑year ingestion.

Variable Naming Model
---------------------
Stage 1 downloads ERA5 GRIB files using **long descriptive variable names**
(e.g., `2m_temperature`, `convective_inhibition`, `surface_pressure`) because
these are the names required by CDSAPI.

However, Stage 2 and all downstream stages operate exclusively on ERA5
**shortName** codes (e.g., `t2m`, `cin`, `sp`). Therefore, a normalization step
occurs *after* Stage 1 download and *before* Stage 1 metadata building:

    long descriptive names → short ERA5 codes

This normalization ensures that Stage 2 can locate GRIB files deterministically
using shortName‑based directory and filename patterns.

Key Behaviors
-------------
- Downloads GRIB files under: raw/era5/<year>/<month>/<variable>/
  (where <variable> is the long descriptive name from config.yml)
- A normalization step later rewrites these directories and filenames to
  shortNames for Stage 2 compatibility.
- Validates environment (CDS credentials) and config.yml
- Supports multi‑year, multi‑month, multi‑variable ingestion
- Implements skip logic for existing GRIB files
- Retries failed downloads with exponential backoff
- Writes per‑variable metadata JSON for Stage 2

Why GRIB‑Only?
--------------
Branch 2 removes the legacy ZIP ingestion path and downloads GRIB files
directly. This is faster, simpler, and avoids ZIP normalization steps in
Stage 2. The directory layout (after normalization) is consumed by Stage 2
preprocessing and Stage 3 chunking.
"""

import json
import os
import time
from pathlib import Path

import cdsapi  # required for monkeypatching

from src.download_01.paths import Paths
from src.utils.config import (
    load_config_yaml,
    load_months,
    load_region,
    load_variables,
    load_years,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------------------
# Mapping of long descriptive variable names → short ERA5 codes
# ------------------------------------------------------------------------------

SHORTNAME_MAP = {
    "10m_u_component_of_wind": "u10",
    "10m_v_component_of_wind": "v10",
    "2m_dewpoint_temperature": "d2m",
    "2m_temperature": "t2m",
    "mean_sea_level_pressure": "msl",
    "surface_pressure": "sp",
    "total_precipitation": "tp",
    "surface_latent_heat_flux": "slhf",
    "surface_net_solar_radiation": "ssr",
    "surface_net_thermal_radiation": "str",
    "surface_sensible_heat_flux": "sshf",
    "surface_solar_radiation_downward_clear_sky": "ssrdc",
    "surface_solar_radiation_downwards": "ssrd",
    "total_cloud_cover": "tcc",
    "evaporation": "e",
    "boundary_layer_height": "blh",
    "convective_available_potential_energy": "cape",
    "convective_inhibition": "cin",
    "land_sea_mask": "lsm",
    "total_column_ozone": "tco3",
    "total_column_water_vapour": "tcwv",
}


# ------------------------------------------------------------------------------
# Module‑level CDSAPI client
# Required for Stage 1 monkeypatching in tests.
# ------------------------------------------------------------------------------

client = cdsapi.Client(timeout=300)

# ------------------------------------------------------------------------------
# Directory helpers
# Ensure raw/era5/<year>/<month>/<variable>/ exists before download.
# ------------------------------------------------------------------------------


def ensure_month_variable_dir(
    paths: Paths, year: str, month: str, variable: str
) -> Path:
    """
    Create raw/era5/<year>/<month>/<variable>/ directory.
    """
    target = Path(paths.raw_dir) / year / month / variable
    target.mkdir(parents=True, exist_ok=True)
    return target


def validate_directories(paths: Paths) -> None:
    """
    Validate top-level directories only.
    """
    for d in [
        paths.raw_dir,
        paths.metadata_dir,
        paths.config_dir,
    ]:
        Path(d).mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------------------
# Environment validation
# Ensures CDSAPI_URL and CDSAPI_KEY are present.
# ------------------------------------------------------------------------------


def validate_environment(paths: Paths) -> None:
    validate_directories(paths)

    if "CDSAPI_URL" not in os.environ or "CDSAPI_KEY" not in os.environ:
        raise OSError("Missing CDS credentials")


# ------------------------------------------------------------------------------
# Config validation (Branch 2 YAML)
# Ensures years, months, and variables are present in config.yml.
# ------------------------------------------------------------------------------


def validate_config(paths: Paths) -> bool:
    config_file = Path(paths.config_dir) / "config.yml"

    if not config_file.exists():
        logger.warning(f"[stage1] Missing config.yml at {config_file}")
        return False

    try:
        cfg = load_config_yaml(config_file)

        # Multi-year ingestion validation
        if not cfg.get("years") or not cfg.get("months") or not cfg.get("variables"):
            raise ValueError("Config missing years/months/variables")

        return True

    except Exception as e:
        logger.warning(f"[stage1] Invalid config.yml: {e}")
        return False


# ------------------------------------------------------------------------------
# Retry wrapper for CDSAPI downloads
# Retries up to 3 times with exponential backoff.
# ------------------------------------------------------------------------------


def download_with_retry(request: dict, outfile: Path) -> Path | None:
    max_attempts = 3
    delay = 1

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"[stage1] Attempt {attempt}: downloading → {outfile}")
            client.retrieve("reanalysis-era5-single-levels", request, str(outfile))
            return outfile
        except Exception as e:
            logger.error(f"[stage1] Download failed (attempt {attempt}): {e}")
            time.sleep(delay)
            delay *= 2

    logger.error(f"[stage1] Exhausted retries for {outfile}")
    return None


# ------------------------------------------------------------------------------
# Single‑variable GRIB download
# Downloads one variable for one year‑month pair.
# Writes metadata JSON regardless of success.
# ------------------------------------------------------------------------------


def download_variable(variable: str, year: str, month: str) -> Path | None:
    logger.info(f"[stage1] Branch 2 download start: {variable} {year}-{month}")

    paths = Paths()

    validate_environment(paths)
    validate_directories(paths)
    config_ok = validate_config(paths)

    # Create raw/era5/<year>/<month>/<variable>/
    target_dir = ensure_month_variable_dir(paths, year, month, variable)

    outfile = target_dir / f"{variable}_{year}_{month}.grib"

    # Skip logic
    if outfile.exists():
        logger.info(f"[stage1] Skipping existing file: {outfile}")
        return outfile

    region = load_region()
    area = [
        region["north"],
        region["west"],
        region["south"],
        region["east"],
    ]

    request = {
        "product_type": "reanalysis",
        "format": "grib",
        "variable": variable,
        "year": year,
        "month": month,
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "area": area,
    }

    result = download_with_retry(request, outfile)

    # Normalize longName → shortName
    short = SHORTNAME_MAP.get(variable, variable)

    # Create shortName directory
    short_dir = Path(paths.raw_dir) / year / month / short
    short_dir.mkdir(parents=True, exist_ok=True)

    # ShortName file path
    short_file = short_dir / f"{short}_{year}_{month}.grib"

    # If download succeeded, rename longName file → shortName file
    if result is not None:
        try:
            outfile.rename(short_file)
            logger.info(f"[stage1] Normalized {outfile} → {short_file}")
        except Exception as e:
            logger.error(f"[stage1] Failed to normalize filename: {e}")

    # Write metadata using shortName
    metadata_path = Path(paths.metadata_dir) / f"metadata_{short}_{year}_{month}.json"
    metadata_path.write_text(
        json.dumps(
            {
                "variable": short,
                "year": year,
                "month": month,
                "success": result is not None,
                "config_valid": config_ok,
                "outfile": str(short_file if result is not None else outfile),
            },
            indent=2,
        )
    )

    return short_file if result is not None else None


# ------------------------------------------------------------------------------
# CLI entrypoint
# Iterates over variables × years × months from config.yml.
# ------------------------------------------------------------------------------


def main():
    variables = load_variables()
    years = load_years()
    months = load_months()

    logger.info(
        f"[stage1] Starting Branch 2 ingestion: {len(variables)} variables, {len(years)} years, {len(months)} months"
    )

    for variable in variables:
        for year in years:
            for month in months:
                month_str = f"{int(month):02d}"
                download_variable(variable, str(year), month_str)


if __name__ == "__main__":
    main()
