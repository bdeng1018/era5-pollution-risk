"""
ERA5 Download Stage (Branch 2)
------------------------------

This package contains the modules responsible for retrieving ERA5 GRIB
files from the Copernicus Data Store (CDS). Branch 2 expands the minimal
Branch 1 ingestion logic into a more robust, reproducible, and scalable
download stage suitable for multi-year climate pipelines.

Branch 1 responsibilities (baseline):
- Build ERA5 API requests
- Download monthly GRIB files for selected variables/years/months
- Apply lightweight logging and basic validation
- Write raw GRIBs into data/raw/era5/

Branch 2 enhancements:
- Multi-year ingestion across all configured years/months
- Retry logic with exponential backoff for transient CDS failures
- Metadata tracking (timestamps, file sizes, run status)
- Environment validation (CDS credentials, directory structure)
- Structured logging for reproducibility
- Config-driven execution via variables.yml, years.yml, months.yml

Intentional Branch 2 scope limits:
- Single-variable ingestion handled in download_era5_single.py
- Multi-variable monthly ingestion handled in download_era5_monthly.py
- No parallelization (added in Branch 3)
- No global ingestion; region/variable scope defined in configs
- No heavy MLOps stack (MLflow/Docker optional in later stages)

Modules:
- download_era5_monthly.py   — main Branch 2 monthly ingestion entrypoint
- download_era5_single.py    — single-variable ingestion with retries and metadata
"""
