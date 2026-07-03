"""
ERA5 Preprocessing Stage (Branch 2)

This package implements the full Stage 2 preprocessing pipeline for ERA5 data.
Stage 2 transforms raw ERA5 monthly ZIP archives and GRIB files into structured
intermediate Parquet files suitable for downstream feature engineering,
merging, and modeling.

Branch 2 responsibilities:
- Unzip monthly ERA5 ZIP files into multi-variable GRIBs
- Inspect all GRIB files (single-variable + multi-variable)
- Generate cfgrib index (.idx) files for fast access
- Validate GRIB structure, variables, and dimensions
- Convert GRIB → Parquet for all months and all variables
- Produce unified logs and conversion metadata
- Provide a single orchestrator entrypoint for Stage 2
- Prepare for Branch 3 parallelization

Branch 1 compatibility:
Stage 2 still supports the Branch 1 workflow, which operates only on
single-variable GRIB files produced by download_era5_single.py. These files
follow the naming convention:
    <variable_name>_<year>_<month>.grib

Branch 2 expands preprocessing to include:
- Multi-variable monthly GRIBs extracted from era5_YYYY_MM.zip
- Full inspection and metadata extraction
- Robust cfgrib opening with error handling
- Conversion of both single-variable and multi-variable GRIBs
- Unified pipeline execution via run_preprocessing.py

Modules:
- unzip_grib.py
    Extract monthly ZIP archives into GRIB files (Branch 2)
- inspect_grib.py
    Inspect GRIB structure, variables, dimensions; generate .idx files
- convert_grib_to_parquet.py
    Convert GRIB → Parquet (single-variable + multi-variable)
- run_preprocessing.py
    Stage 2 orchestrator: unzip → inspect → convert
"""
