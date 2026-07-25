"""
ERA5 Preprocessing Stage (Branch 1)

This package contains the modules responsible for preparing ERA5 GRIB files
for downstream feature engineering. In Branch 1, preprocessing operates
*only on the single-variable GRIB file* produced by the minimal downloader.
The full monthly ZIP ingestion workflow will be added in Branch 2.

Branch 1 responsibilities:
- unzip the single-variable GRIB (if applicable)
- perform lightweight GRIB inspection (structure, dimensions)
- convert the single-variable GRIB → Parquet for feature engineering

Branch 2 will expand this stage with:
- full multi-variable ZIP ingestion
- GRIB metadata extraction and validation
- consistency checks across variables and months
- batching and parallel conversion
- structured logging and run metadata
- environment validation (cfgrib, eccodes, xarray)

Modules:
- unzip_grib.py               — extract GRIB files (Branch 1: single-variable only)
- inspect_grib.py            — minimal GRIB inspection (placeholder for Branch 2)
- convert_grib_to_parquet.py — convert GRIB → Parquet for Branch 1 feature engineering
"""
