"""
Stage 1: ERA5 Download Pipeline (Branch 2)
==========================================

Purpose
-------
Implements Stage 1 of the ERA5 ingestion pipeline. This stage retrieves raw
ERA5 Single‑Level GRIB files directly from the Copernicus Data Store (CDS)
and writes them into a deterministic directory layout:

    raw/era5/<year>/<month>/<variable>/<variable>_<year>_<month>.grib

Stage 1 produces the complete GRIB dataset consumed by Stage 2 preprocessing
and Stage 3 chunking.

Branch 1 Responsibilities (Baseline)
------------------------------------
- Build CDSAPI requests for ERA5 single‑level variables.
- Download monthly GRIB files for configured variables/years/months.
- Apply lightweight validation and logging.
- Write raw GRIBs into data/raw/era5/.

Branch 2 Enhancements
---------------------
- Multi‑year ingestion across all configured years/months.
- Config‑driven execution via variables.yml, years.yml, months.yml.
- Retry logic with exponential backoff for transient CDSAPI failures.
- Metadata tracking (success flag, config validity, GRIB file path).
- Environment validation (CDS credentials, directory structure).
- Structured logging for reproducibility and debugging.
- Long‑form ERA5 variable naming for consistency across CDSAPI, raw layout,
  metadata, and downstream processing stages.

Intentional Branch 2 Scope Limits
---------------------------------
- Single‑variable ingestion handled in download_era5_single.py.
- Monthly orchestration handled in download_era5_monthly.py.
- No parallelization (added in Branch 3).
- No global ingestion; region/variable scope defined strictly by configs.
- No heavy MLOps stack (MLflow/Docker optional in later stages).

Stage 1 Contract (Design Guarantees)
------------------------------------
- Deterministic directory layout for all GRIB outputs.
- Metadata JSON is always written (success or failure).
- No partial or corrupted GRIB files on failure.
- Idempotent execution: re‑running Stage 1 never overwrites existing GRIBs.
- GRIB‑only ingestion (ZIP ingestion removed in Branch 2).

Modules
-------
- download_era5_monthly.py   — Branch 2 monthly ingestion orchestrator.
- download_era5_single.py    — Single‑variable ingestion with retries and metadata.
"""

# ------------------------------------------------------------------------------
# Stage 1: Branch 2 ERA5 Downloader Package
# Provides GRIB-only ingestion for all configured variables/years/months.
# ------------------------------------------------------------------------------
