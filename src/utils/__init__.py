"""
Shared utility modules for the ERA5 pipeline.

This package provides:
- YAML config loading
- project path helpers (project root, ensure_dir)
- logging setup (RichHandler)
- environment validation (Python + required packages)
- data validation helpers (GRIB and Parquet checks)
- run metadata utilities (JSON metadata writer)
- model I/O helpers (save/load model artifacts)

The package initializer intentionally contains no imports to avoid
side effects during pytest discovery or `python -m` execution.
"""
