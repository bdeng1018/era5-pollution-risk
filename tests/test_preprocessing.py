"""
Branch 1 smoke tests for the preprocessing stage.

These tests verify only that the preprocessing modules import correctly.
Branch 1 does NOT validate:
- GRIB → Parquet conversion
- schema correctness
- metadata extraction
- data content or shape

Branch 2 will introduce full validation tests including:
- pytest fixtures
- file existence checks
- GRIB metadata validation
- Parquet schema checks
- multi-variable ingestion tests
"""

def test_preprocess_import():
    """
    Smoke test: ensure preprocessing modules import without crashing.

    Branch 1 keeps preprocessing intentionally minimal. These imports confirm:
    - modules exist
    - no syntax errors
    - no missing dependencies
    - no circular imports

    No functions are executed in Branch 1.
    """
    import src.preprocessing_02.unzip_grib            # noqa: F401
    import src.preprocessing_02.inspect_grib          # noqa: F401
    import src.preprocessing_02.convert_grib_to_parquet  # noqa: F401