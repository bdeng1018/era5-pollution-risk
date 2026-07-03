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

# ==============================================================================
# Integration Test — unzip → inspect
# ==============================================================================

def test_unzip_then_inspect_structural():
    """
    Integration test: ensure unzip_grib and inspect_grib can be imported and
    referenced together without causing circular imports or structural failures.

    No GRIB files are opened. No unzip or inspect logic is executed.
    """
    import src.preprocessing_02.inspect_grib as inspect
    import src.preprocessing_02.unzip_grib as unzip

    assert hasattr(unzip, "main"), "unzip_grib.main() must exist for integration"
    assert hasattr(inspect, "main"), "inspect_grib.main() must exist for integration"


# ==============================================================================
# Integration Test — inspect → convert
# ==============================================================================

def test_inspect_then_convert_structural():
    """
    Integration test: ensure inspect_grib and convert_grib_to_parquet can be
    referenced together without structural conflicts.

    No GRIB files are opened. No conversion logic is executed.
    """
    import src.preprocessing_02.convert_grib_to_parquet as convert
    import src.preprocessing_02.inspect_grib as inspect

    assert hasattr(inspect, "main"), "inspect_grib.main() must exist for integration"
    assert hasattr(convert, "main"), "convert_grib_to_parquet.main() must exist"


# ==============================================================================
# Integration Test — unzip → inspect → convert
# ==============================================================================

def test_full_stage2_chain_structural():
    """
    Integration test: ensure all three preprocessing modules can be chained
    structurally without import conflicts.

    This validates the orchestration wiring at a structural level.
    """
    import src.preprocessing_02.convert_grib_to_parquet as convert
    import src.preprocessing_02.inspect_grib as inspect
    import src.preprocessing_02.unzip_grib as unzip

    assert callable(unzip.main), "unzip_grib.main must be callable"
    assert callable(inspect.main), "inspect_grib.main must be callable"
    assert callable(convert.main), "convert_grib_to_parquet.main must be callable"


# ==============================================================================
# Integration Test — run_preprocessing orchestrator
# ==============================================================================

def test_run_preprocessing_structural():
    """
    Integration test: ensure run_preprocessing orchestrator imports correctly
    and exposes a main() function that ties together unzip → inspect → convert.

    No pipeline logic is executed.
    """
    import src.preprocessing_02.run_preprocessing as rp

    assert hasattr(rp, "main"), "run_preprocessing.main() must exist"
    assert callable(rp.main), "run_preprocessing.main must be callable"
