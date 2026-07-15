"""
Stage 2 System Test — Branch 2

This test validates that the Stage 2 preprocessing pipeline can be executed
as a system through its public entry point (run_preprocessing.main). Unlike
unit or integration tests, system tests verify that the pipeline *runs*,
initializes logging, resolves paths, and does not crash during startup.

Covered:
- run_preprocessing.main() executes without raising exceptions
- pipeline modules load correctly in a real execution context
- logging initializes successfully
- system-level orchestration wiring is intact

Not covered (handled in acceptance/regression tests):
- correctness of GRIB ingestion
- correctness of .idx generation
- correctness of Parquet output
- schema validation
- multi-variable ingestion
- directory creation
- retry logic
- performance characteristics
"""

import importlib


def test_stage2_system_execution(tmp_path, monkeypatch):
    """
    System test: ensure run_preprocessing.main() executes without crashing.

    This does NOT validate correctness of outputs. It only ensures that the
    pipeline can run end-to-end at a system level without raising exceptions.

    No GRIB files are opened and no Parquet files are written in this test.
    """
    monkeypatch.setenv("ERA5_BASE_DIR", str(tmp_path))
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")

    try:
        rp.main()
    except Exception as exc:
        raise AssertionError(
            f"System-level execution of run_preprocessing.main() failed: {exc}"
        )
