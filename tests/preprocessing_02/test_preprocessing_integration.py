"""
Stage 2 Integration Tests — Branch 2

These tests validate multi‑step interactions between preprocessing modules.
They do NOT open real GRIB files, generate .idx files, or write Parquet.
Instead, they ensure that the modules can be orchestrated together at a
structural level without executing full pipeline logic.

Covered:
- unzip → inspect structural integration
- inspect → convert structural integration
- unzip → inspect → convert orchestration wiring
- run_preprocessing structural integration

Not covered (handled in acceptance/system tests):
- actual GRIB ingestion
- cfgrib index generation
- Parquet schema correctness
- multi-variable ingestion
- directory creation
- logging behavior
- retry logic
- real pipeline execution
"""

import importlib

# ==============================================================================
# Integration Test — unzip → inspect
# ==============================================================================


def test_unzip_then_inspect_structural():
    unzip = importlib.import_module("src.preprocessing_02.unzip_grib")
    inspect = importlib.import_module("src.preprocessing_02.inspect_grib")

    assert hasattr(unzip, "main")
    assert hasattr(inspect, "main")
    assert callable(unzip.main)
    assert callable(inspect.main)


# ==============================================================================
# Integration Test — inspect → convert
# ==============================================================================


def test_inspect_then_convert_structural():
    inspect = importlib.import_module("src.preprocessing_02.inspect_grib")
    convert = importlib.import_module("src.preprocessing_02.convert_grib_to_parquet")

    assert hasattr(inspect, "main")
    assert hasattr(convert, "main")
    assert callable(inspect.main)
    assert callable(convert.main)


# ==============================================================================
# Integration Test — unzip → inspect → convert
# ==============================================================================


def test_full_stage2_chain_structural():
    unzip = importlib.import_module("src.preprocessing_02.unzip_grib")
    inspect = importlib.import_module("src.preprocessing_02.inspect_grib")
    convert = importlib.import_module("src.preprocessing_02.convert_grib_to_parquet")

    assert callable(unzip.main)
    assert callable(inspect.main)
    assert callable(convert.main)


# ==============================================================================
# Integration Test — run_preprocessing orchestrator
# ==============================================================================


def test_run_preprocessing_structural():
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")

    assert hasattr(rp, "main")
    assert callable(rp.main)


# ==============================================================================
# Integration Test — Ensure no heavy imports occur
# ==============================================================================


def test_no_heavy_imports_in_stage2():
    import sys

    banned = ["cfgrib", "eccodes"]
    for name in banned:
        assert name not in sys.modules
