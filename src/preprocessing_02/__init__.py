"""
ERA5 Preprocessing Stage (Branch 2)
===================================

Stage 2 transforms raw ERA5 monthly ZIP archives and GRIB files into structured
HOURLY and STATIC Parquet files suitable for downstream merging, feature
engineering, and parallelized processing in Stage 3.

Branch 2 Responsibilities
-------------------------
- Unzip monthly ERA5 ZIP archives into multi-variable GRIB files.
- Inspect all GRIB files (single-variable + multi-variable).
- Validate GRIB structure, variables, dimensions, and availability.
- Convert GRIB → Parquet for all months and all variables:
    * Hourly fields → one Parquet per timestamp.
    * Static / monthly-mean fields → one Parquet per variable.
- Provide robust cfgrib loading:
    * Per-variable filtering for multi-variable GRIBs.
    * Filename → shortName mapping for single-variable GRIBs.
    * Automatic fallback when filter_by_keys returns an empty dataset.
- Produce unified logs and per-file conversion metadata.

Two Metadata Files (New Architecture)
-------------------------------------
Stage 2 now produces **two separate metadata files**, reflecting the correct
compiler-style IR boundary:

1. **grib_metadata.json** (IR₀ diagnostic)
   - Contains GRIB-level inspection results.
   - Includes raw timestamps, raw GRIB filenames, raw variable availability.
   - Used only for diagnostics and validation.
   - Never consumed by Stage 3 or Stage 4.

2. **metadata.json** (IR₁ canonical Parquet metadata)
   - Built *only* from Parquet files in:
         data/intermediate/<year>/<month>/<variable>/*.parquet
   - Contains normalized timestamps, correct shapes, correct dtypes.
   - Includes ONLY instantaneous hourly variables.
   - Static and flux variables are excluded.
   - This file is consumed by Stage 3 chunk planning and merging.

Branch 1 Compatibility
----------------------
Stage 2 continues to support the Branch 1 workflow, which operates on
single-variable GRIB files produced by download_era5_single.py. These files
follow the naming convention:

    <variable_name>_<year>_<month>.grib

Branch 2 Expands Preprocessing to Include
-----------------------------------------
- Multi-variable monthly GRIBs extracted from era5_YYYY_MM.zip.
- Robust cfgrib opening with per-variable filtering.
- Automatic fallback to full GRIB open when shortName filtering fails.
- Support for static / monthly-mean variables (no time dimension).
- Hourly slicing and Parquet generation for all variables with time.
- Canonical Parquet metadata (metadata.json) for downstream merging.

Canonical HOURLY metadata.json (IR₁)
------------------------------------
Stage 3 merging relies exclusively on metadata.json:

    {
        "<timestamp>": {
            "variable": "<shortName>",
            "path": "/path/to/parquet",
            "year": 2019,
            "month": 1,
            "dtype": "float32",
            "shape": [lat, lon]
        },
        ...
    }

Notes
-----
- Flux/accumulated variables (e.g., slhf, sshf, ssr, str, tp) are written to
  Parquet but intentionally excluded from metadata.json because they use
  different spatial grids and timestamp structures.
- Static variables (e.g., lsm) are also excluded from metadata.json.
- GRIB inspection metadata is diagnostic-only and never influences IR₁.

Modules
-------
- unzip_grib.py
    Extract monthly ZIP archives into GRIB files (Branch 2).

- inspect_grib.py
    Inspect GRIB structure, variables, dimensions, and availability.
    Writes grib_metadata.json (diagnostic-only).

- convert_grib_to_parquet.py
    Convert GRIB → Parquet (hourly + static) for single-variable and
    multi-variable GRIBs.

- metadata_parquet.py
    Build canonical Parquet-only metadata.json (IR₁).

- run_preprocessing.py
    Stage 2 orchestrator:
        unzip → inspect → convert → build grib_metadata.json → build metadata.json.
"""
