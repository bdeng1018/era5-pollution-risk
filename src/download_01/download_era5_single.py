"""
Branch 2: Single-Variable ERA5 Downloader
-----------------------------------------

Used by Stage 1 tests. Must remain stable and monkeypatch-friendly.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

import cdsapi  # required for monkeypatching

from src.download_01.paths import Paths
from src.utils.config import load_variables
from src.utils.logging import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------------------
# Module-level client (required by Stage 1 monkeypatching)
# ------------------------------------------------------------------------------
client = cdsapi.Client()


# ------------------------------------------------------------------------------
# Directory validation (Stage 1 requires passing paths explicitly)
# ------------------------------------------------------------------------------

def validate_directories(paths: Paths) -> None:
    for d in [paths.raw_dir, paths.metadata_dir, paths.config_dir]:
        Path(d).mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------------------
# Environment validation
# ------------------------------------------------------------------------------

def validate_environment(paths: Paths) -> None:
    validate_directories(paths)

    if "CDSAPI_URL" not in os.environ or "CDSAPI_KEY" not in os.environ:
        raise EnvironmentError("Missing CDS credentials")


# ------------------------------------------------------------------------------
# Config validation
# ------------------------------------------------------------------------------

def validate_config(paths: Paths) -> bool:
    config_file = Path(paths.config_dir) / "config.json"

    if not config_file.exists():
        logger.warning(f"[stage1] Missing config.json at {config_file}")
        return False

    try:
        json.loads(config_file.read_text())
        return True
    except Exception:
        return False


# ------------------------------------------------------------------------------
# Retry wrapper
# ------------------------------------------------------------------------------

def download_with_retry(request: dict, outfile: Path) -> Optional[Path]:
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
# Single-variable download
# ------------------------------------------------------------------------------

def download_variable(variable: str, year: str, month: str) -> Optional[Path]:
    logger.info(f"[stage1] Branch 2 download start: {variable} {year}-{month}")

    # Monkeypatch-friendly: Paths() is replaced in tests
    paths = Paths()

    validate_environment(paths)
    validate_directories(paths)
    config_ok = validate_config(paths)

    outfile = Path(paths.raw_dir) / f"{variable}_{year}_{month}.grib"

    request = {
        "product_type": "reanalysis",
        "format": "grib",
        "variable": variable,
        "year": year,
        "month": month,
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
    }

    result = download_with_retry(request, outfile)

    metadata_path = Path(paths.metadata_dir) / f"metadata_{variable}_{year}_{month}.json"
    metadata_path.write_text(
        json.dumps(
            {
                "variable": variable,
                "year": year,
                "month": month,
                "success": result is not None,
                "config_valid": config_ok,
            }
        )
    )

    return result


# ------------------------------------------------------------------------------
# CLI entrypoint
# ------------------------------------------------------------------------------

def main():
    variables = load_variables()
    for variable in variables:
        download_variable(variable, "2023", "01")


if __name__ == "__main__":
    main()
