"""
Stage 2 Smoke Tests — Preprocessing Pipeline (Branch 2)

Purpose
-------
These tests verify only that the preprocessing modules import correctly.
A smoke test ensures the pipeline is structurally intact before running
unit, integration, acceptance, system, or regression tests.

What this smoke test DOES validate:
- modules exist
- modules import without syntax errors
- dependencies resolve correctly
- no circular imports occur

What this smoke test DOES NOT validate:
- unzip behavior
- GRIB metadata extraction
- .idx generation
- GRIB → Parquet conversion
- multi-variable ingestion
- directory creation
- run_preprocessing orchestration
- schema correctness
- logging behavior
- retry logic

Why so minimal?
---------------
Smoke tests are intentionally shallow. Their job is to detect catastrophic
failures early (missing modules, broken imports, dependency issues) before
any deeper tests run. They never execute pipeline logic or touch real data.

Branch 2 introduces full validation tests in separate files:
- unit tests for unzip/inspect/convert
- integration tests for multi-step ingestion
- acceptance tests for full pipeline correctness
- system tests for CLI/Makefile execution
- regression tests for future stability
"""

import importlib


def test_stage2_smoke_imports():
    """
    Smoke test: ensure Stage 2 preprocessing modules import without crashing.

    No functions are executed. Only module imports are validated.
    """
    modules = [
        "src.preprocessing_02.unzip_grib",
        "src.preprocessing_02.inspect_grib",
        "src.preprocessing_02.convert_grib_to_parquet",
        "src.preprocessing_02.run_preprocessing",
    ]

    for module in modules:
        imported = importlib.import_module(module)
        assert imported is not None, f"Failed to import {module}"
