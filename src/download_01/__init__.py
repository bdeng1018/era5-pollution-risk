"""
ERA5 Download Stage (Branch 1)

This package contains the modules responsible for retrieving ERA5 GRIB
files from the Copernicus Data Store (CDS). It provides the minimal
monthly download logic required for Branch 1 of the pipeline.

Branch 1 responsibilities:
- build ERA5 API requests
- download monthly GRIB files for selected variables/years/months
- apply lightweight logging and basic validation
- write raw GRIBs into data/raw/era5/

Branch 2 will expand this stage with:
- retry logic and exponential backoff
- parallel and batched downloads
- metadata tracking (timestamps, hashes, run IDs)
- structured logging to file
- multi-year ingestion

Modules:
- download_era5_monthly.py   — main Branch 1 download entrypoint
- download_era5_single.py    — optional debugging helper (not used in pipeline)
"""