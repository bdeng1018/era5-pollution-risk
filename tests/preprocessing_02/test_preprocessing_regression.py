"""
Stage 2 Regression Test — Branch 2

Regression tests ensure that future changes do not break Stage 2 guarantees.
Unlike acceptance tests (which validate correctness) or system tests (which
validate execution), regression tests validate *stability* of the pipeline's
public interfaces and structural expectations.

Covered:
- public API stability (main() functions still exist)
- module import stability (no new circular imports)
- Paths() attribute stability (directory names unchanged)
- orchestrator stability (run_preprocessing.main still callable)

Not covered (handled elsewhere):
- correctness of GRIB ingestion
- correctness of .idx generation
- correctness of Parquet output
- schema validation
- multi-variable ingestion correctness
- retry logic correctness
- performance characteristics
"""

import importlib
import sys
from pathlib import Path

# ==============================================================================
# Regression Test — Public API Stability
# ==============================================================================


def test_regression_public_api_stability():
    unzip = importlib.import_module("src.preprocessing_02.unzip_grib")
    inspect = importlib.import_module("src.preprocessing_02.inspect_grib")
    convert = importlib.import_module("src.preprocessing_02.convert_grib_to_parquet")
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")

    assert hasattr(unzip, "main")
    assert hasattr(inspect, "main")
    assert hasattr(convert, "main")
    assert hasattr(rp, "main")

    assert callable(unzip.main)
    assert callable(inspect.main)
    assert callable(convert.main)
    assert callable(rp.main)


# ==============================================================================
# Regression Test — Paths Structure Stability
# ==============================================================================


def test_regression_paths_structure_stability():
    Paths = importlib.import_module("src.utils.paths").Paths
    p = Paths()

    expected_attrs = [
        "raw_dir",
        "intermediate_dir",
        "logs_dir",
        "metadata_dir",
    ]

    for attr in expected_attrs:
        assert hasattr(p, attr)
        value = getattr(p, attr)
        assert isinstance(value, Path)


# ==============================================================================
# Regression Test — Orchestrator Stability
# ==============================================================================


def test_regression_orchestrator_stability():
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")
    assert callable(rp.main)


# ==============================================================================
# Regression Test — No Heavy Imports at Module Load
# ==============================================================================


def test_regression_no_heavy_imports():
    """
    Ensure Stage 2 modules do not import heavy libraries (cfgrib, eccodes)
    *at module load time*. Heavy imports during execution are validated in
    acceptance/system tests and are allowed here.
    """
    before = set(sys.modules.keys())

    importlib.import_module("src.preprocessing_02.unzip_grib")
    importlib.import_module("src.preprocessing_02.inspect_grib")
    importlib.import_module("src.preprocessing_02.convert_grib_to_parquet")
    importlib.import_module("src.preprocessing_02.run_preprocessing")

    after = set(sys.modules.keys())
    newly_loaded = after - before

    banned = ["cfgrib", "eccodes"]

    for name in banned:
        assert name not in newly_loaded, (
            f"Regression: heavy import detected at module load: {name}"
        )
