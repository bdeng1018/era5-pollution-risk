"""
Download a single ERA5 variable for a given year and month.

This module provides the minimal Branch 1 functionality:
- Build a CDS API request for one variable
- Download one GRIB file
- Save it to the raw ERA5 directory

Branch 2 will expand this with:
- retries
- metadata tracking
- parallelization
- environment validation
"""

import cdsapi
from src.utils.config import load_variables, load_years, load_months
from src.utils.paths import Paths
from src.utils.logging import get_logger

logger = get_logger(__name__)
client = cdsapi.Client()


def download_variable(variable: str, year: str, month: str):
    """
    Download a single ERA5 variable for a specific year and month.

    Parameters
    ----------
    variable : str
        ERA5 variable name (e.g., "2m_temperature")
    year : str
        Year as a string (e.g., "2023")
    month : str
        Month as a string (e.g., "09")

    Returns
    -------
    Path or None
        Path to the saved GRIB file, or None if skipped.
    """
    logger.info(
        f"Starting Branch 1 single-variable download: {variable} {year}-{month}"
    )

    # Validate inputs
    variables = load_variables()
    years = load_years()
    months = load_months()

    if variable not in variables:
        raise ValueError(f"Variable '{variable}' not found in variables.yml")

    if year not in years:
        raise ValueError(f"Year '{year}' not in years.yml")

    if month not in months:
        raise ValueError(f"Month '{month}' not in months.yml")

    # Resolve output path
    paths = Paths()
    raw_dir = paths.raw_dir
    raw_dir.mkdir(parents=True, exist_ok=True)

    outfile = raw_dir / f"{variable}_{year}_{month}.grib"

    # Skip logic
    if outfile.exists():
        logger.info(
            f"Skipping {variable} {year}-{month}: file already exists → {outfile}"
        )
        return None

    logger.info(f"Requesting ERA5 {variable} for {year}-{month} → {outfile}")

    # Minimal Branch 1 request
    request = {
        "product_type": "reanalysis",
        "variable": variable,
        "year": year,
        "month": month,
        "day": ["01"],  # minimal Branch 1 request
        "time": ["00:00"],  # minimal Branch 1 request
        "format": "grib",
    }

    client.retrieve("reanalysis-era5-single-levels", request).download(str(outfile))
    logger.info(f"Saved GRIB file → {outfile}")

    return outfile


def main():
    """
    Optional CLI entrypoint for manual testing.
    """
    logger.info("Running Branch 1 single-variable downloader via CLI...")

    # Hard-coded Branch 1 example
    variable = "2m_temperature"
    year = "2023"
    month = "09"

    download_variable(variable, year, month)

    logger.info("Single-variable download complete.")


if __name__ == "__main__":
    main()
