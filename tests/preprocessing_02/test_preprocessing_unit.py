"""
Stage 2 Unit Tests — Branch 2

These tests validate the smallest, lowest‑level guarantees of the Stage 2
preprocessing modules. No GRIB files are opened, no Parquet files are written,
and no directories are created. All tests remain pure unit tests.

Covered:
- function existence tests (main() presence)
- basic structural validation of preprocessing modules
- Paths() attribute resolution

Not covered (handled in other test files):
- module import smoke tests (test_preprocessing_smoke.py)
- unzip → inspect → convert behavior
- GRIB metadata extraction
- cfgrib index generation
- Parquet schema correctness
- multi-variable ingestion
- run_preprocessing orchestration
- logging behavior
- retry logic
"""

# ==============================================================================
# Unit Test — unzip_grib
# ==============================================================================

def test_unzip_module_has_main():
    """
    Unit test: unzip_grib should expose a main() function in Stage 2.

    This does NOT execute unzip logic.
    """
    import src.preprocessing_02.unzip_grib as unzip

    assert hasattr(unzip, "main"), "unzip_grib.main() must exist in Stage 2"
    assert callable(unzip.main), "unzip_grib.main must be callable"


# ==============================================================================
# Unit Test — inspect_grib
# ==============================================================================

def test_inspect_module_has_main():
    """
    Unit test: inspect_grib should expose a main() function in Stage 2.

    This does NOT open GRIB files or generate .idx files.
    """
    import src.preprocessing_02.inspect_grib as inspect

    assert hasattr(inspect, "main"), "inspect_grib.main() must exist in Stage 2"
    assert callable(inspect.main), "inspect_grib.main must be callable"


# ==============================================================================
# Unit Test — convert_grib_to_parquet
# ==============================================================================

def test_convert_module_has_main():
    """
    Unit test: convert_grib_to_parquet should expose a main() function.

    This does NOT open GRIB files or write Parquet.
    """
    import src.preprocessing_02.convert_grib_to_parquet as convert

    assert hasattr(convert, "main"), "convert_grib_to_parquet.main() must exist"
    assert callable(convert.main), "convert_grib_to_parquet.main must be callable"


# ==============================================================================
# Unit Test — Paths() Utility
# ==============================================================================

def test_paths_resolve_directories():
    """
    Unit test: ensure Paths() resolves directory attributes correctly.

    This does NOT create directories — it only checks attribute existence.
    """
    from src.utils.paths import Paths

    p = Paths()

    required_attrs = [
        "raw_dir",
        "intermediate_dir",
        "logs_dir",
    ]

    for attr in required_attrs:
        assert hasattr(p, attr), f"Paths() missing required attribute: {attr}"
        assert isinstance(getattr(p, attr), str), f"Paths.{attr} must be a string"
