"""
ERA5 Monthly Downloader (Branch 1)

Downloads ERA5 Single-Level reanalysis data for the LA Basin region,
one month at a time, saving each month as a ZIP file in data/raw/era5/.

Branch 2 will add:
- retries
- parallelization
- metadata tracking
- full environment validation
"""

import cdsapi
from pathlib import Path

from src.utils.paths import Paths
from src.utils.config import load_variables, load_years, load_months
from src.utils.logging import get_logger

logger = get_logger(__name__)
client = cdsapi.Client()


# ------------------------------------------------------------------------------
# Branch 1 monthly downloader
# ------------------------------------------------------------------------------

def download_month(year: str, month: str):
    """
    Download ERA5 data for a single month (all variables).

    Parameters
    ----------
    year : str
    month : str

    Returns
    -------
    Path or None
        Path to the saved ZIP file, or None if skipped.
    """

    paths = Paths()
    raw_dir = paths.raw_dir

    variables = load_variables()

    # Output file
    outfile = raw_dir / f"era5_{year}_{month}.zip"
    outfile.parent.mkdir(parents=True, exist_ok=True)

    # Skip logic
    if outfile.exists():
        logger.info(f"Skipping {year}-{month}: file already exists → {outfile}")
        return None

    logger.info(f"Requesting ERA5 monthly data for {year}-{month} → {outfile}")

    request = {
        "product_type": ["reanalysis"],
        "variable": variables,
        "year": year,
        "month": month,
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "data_format": "grib",
        "download_format": "zip",
        "area": [35, -120, 33, -116],  # LA Basin bounding box
    }

    client.retrieve("reanalysis-era5-single-levels", request).download(str(outfile))

    logger.info(f"Saved ERA5 monthly ZIP → {outfile}")
    return outfile


def main():
    """
    Main loop for Branch 1 monthly downloads.
    """

    logger.info("Starting Branch 1 ERA5 monthly downloads...")

    years = load_years()
    months = load_months()

    for year in years:
        for month in months:
            download_month(year, month)

    logger.info("All monthly downloads complete.")


if __name__ == "__main__":
    main()