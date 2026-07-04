"""
ERA5 Preprocessing Stage (Branch 2)
===================================

This package implements the full Stage 2 preprocessing pipeline for ERA5 data.
Stage 2 transforms raw ERA5 monthly ZIP archives and GRIB files into structured,
HOURLY Parquet files suitable for downstream feature engineering, merging, and
parallelized processing in Stage 3.

Branch 2 responsibilities:
- Unzip monthly ERA5 ZIP archives into multi-variable GRIB files
- Inspect all GRIB files (single-variable + multi-variable)
- Validate GRIB structure, variables, and dimensions
- Convert GRIB → HOURLY Parquet for all months and all variables
- Produce unified logs and conversion metadata
- Build a master HOURLY metadata.json describing all variables and timestamps
- Provide a single orchestrator entrypoint for Stage 2
- Prepare for Branch 3 parallelization (chunk planning)

Branch 1 compatibility:
Stage 2 continues to support the Branch 1 workflow, which operates on
single-variable GRIB files produced by download_era5_single.py. These files
follow the naming convention:
    <variable_name>_<year>_<month>.grib

Branch 2 expands preprocessing to include:
- Multi-variable monthly GRIBs extracted from era5_YYYY_MM.zip
- Robust cfgrib opening with per-variable filtering
- Filename → ERA5 shortName mapping for Branch 1 GRIBs
- Hourly slicing and Parquet generation for every variable
- Unified metadata structure:

    {
        "variables": {
            "<shortName>": {
                "YYYY-MM-DDTHH:MM": "/path/to/parquet",
                ...
            },
            ...
        },
        "timestamps": [
            "YYYY-MM-DDTHH:MM",
            ...
        ]
    }

Modules:
- unzip_grib.py
    Extract monthly ZIP archives into GRIB files (Branch 2)
- inspect_grib.py
    Inspect GRIB structure, variables, dimensions
- convert_grib_to_parquet.py
    Convert GRIB → HOURLY Parquet (single-variable + multi-variable)
- run_preprocessing.py
    Stage 2 orchestrator: unzip → inspect → convert → metadata
"""
