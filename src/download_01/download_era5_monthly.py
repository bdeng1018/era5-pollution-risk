"""
Stage 1: Branch 2 Monthly ERA5 Downloader
=========================================

Purpose
-------
Coordinates multi‑variable, multi‑year, multi‑month ingestion by delegating
each (variable, year, month) request to the single‑variable GRIB downloader
(download_era5_single.py). This module does NOT download multi‑variable ZIP
bundles; Branch 2 uses direct GRIB ingestion exclusively.

Variable Naming Model
---------------------
Stage 1 downloads ERA5 variables using **long descriptive names** (as required
by CDSAPI). The single‑variable downloader performs a normalization step:

    long descriptive names → short ERA5 codes

This ensures that all GRIB files ultimately reside under:

    raw/era5/<year>/<month>/<shortName>/<shortName>_<year>_<month>.grib

This normalized layout is consumed by Stage 1 metadata building, Stage 2
preprocessing, and Stage 3 chunking.

Directory Layout
----------------
After normalization, each downloaded GRIB file is written to:

    raw/era5/<year>/<month>/<shortName>/<shortName>_<year>_<month>.grib

Key Behaviors
-------------
- Loads variables, years, and months from config.yml
- Validates CDS credentials and directory structure
- Delegates all downloads to download_era5_single.py
- Monkeypatch‑friendly for Stage 1 tests
- Deterministic and restart‑safe

Public API Contract
-------------------
Stage 1 tests require:
    - main() must exist
    - main() must iterate over variables × years × months
    - main() must call download_variable()
"""

import os
from pathlib import Path

# Single-variable ingestion (Branch 2 core)
from src.download_01.download_era5_single import download_variable
from src.download_01.paths import Paths
from src.utils.config import (
    load_months,
    load_region,
    load_variables,
    load_years,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------------------
# Directory + Environment Validation
# Ensures top-level directories exist and CDS credentials are present.
# Stage 1 tests monkeypatch Paths(), so this must remain filesystem‑agnostic.
# ------------------------------------------------------------------------------

def validate_directories(paths: Paths) -> None:
    """
    Ensure top-level directories exist.
    Stage 1 tests monkeypatch Paths(), so this must not assume real filesystem.
    """
    for d in [paths.raw_dir, paths.metadata_dir, paths.config_dir]:
        Path(d).mkdir(parents=True, exist_ok=True)


def validate_environment(paths: Paths) -> None:
    """
    Validate CDS credentials and directory structure.
    """
    validate_directories(paths)

    if "CDSAPI_URL" not in os.environ or "CDSAPI_KEY" not in os.environ:
        raise EnvironmentError("Missing CDS credentials")

# ------------------------------------------------------------------------------
# Monthly Orchestrator (Branch 2)
# Loads variables/years/months from YAML config and delegates each download
# to the single‑variable downloader. This module performs no GRIB processing
# itself; it only coordinates ingestion.
# ------------------------------------------------------------------------------

def main():
    """
    Branch 2 monthly ingestion:
    - Loads variables, years, months from YAML configs
    - Validates environment
    - Delegates each (variable, year, month) to download_era5_single.py
    """
    paths = Paths()
    validate_environment(paths)

    variables = load_variables()
    years = load_years()
    months = load_months()

    logger.info(
        f"[stage1] Branch 2 monthly ingestion: "
        f"{len(variables)} variables, {len(years)} years, {len(months)} months"
    )

    for variable in variables:
        for year in years:
            for month in months:
                month_str = f"{int(month):02d}"
                download_variable(variable, str(year), month_str)

# ------------------------------------------------------------------------------
# Entrypoint
# Required for Stage 1 public API stability and CLI execution.
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
