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
from pathlib import Path

# ==============================================================================
# Regression Test — Public API Stability
# ==============================================================================


def test_regression_public_api_stability():
    """
    Regression test: ensure all Stage 2 preprocessing modules still expose
    their expected public API (main() functions). This protects against
    accidental refactors that remove or rename entry points.
    """
    unzip = importlib.import_module("src.preprocessing_02.unzip_grib")
    inspect = importlib.import_module("src.preprocessing_02.inspect_grib")
    convert = importlib.import_module("src.preprocessing_02.convert_grib_to_parquet")
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")

    assert hasattr(unzip, "main"), "Regression: unzip_grib.main() missing"
    assert hasattr(inspect, "main"), "Regression: inspect_grib.main() missing"
    assert hasattr(convert, "main"), (
        "Regression: convert_grib_to_parquet.main() missing"
    )
    assert hasattr(rp, "main"), "Regression: run_preprocessing.main() missing"

    assert callable(unzip.main), "Regression: unzip_grib.main() not callable"
    assert callable(inspect.main), "Regression: inspect_grib.main() not callable"
    assert callable(convert.main), (
        "Regression: convert_grib_to_parquet.main() not callable"
    )
    assert callable(rp.main), "Regression: run_preprocessing.main() not callable"


# ==============================================================================
# Regression Test — Paths Structure Stability
# ==============================================================================


def test_regression_paths_structure_stability():
    """
    Regression test: ensure Paths() still exposes the same directory attributes.
    This protects against accidental renaming or removal of Stage 2 directories.
    """
    Paths = importlib.import_module("src.utils.paths").Paths
    p = Paths()

    expected_attrs = [
        "raw_dir",
        "intermediate_dir",
        "logs_dir",
        "metadata_dir",
    ]

    for attr in expected_attrs:
        assert hasattr(p, attr), f"Regression: Paths.{attr} missing"
        value = getattr(p, attr)
        assert isinstance(value, Path), (
            f"Regression: Paths.{attr} must be a pathlib.Path"
        )


# ==============================================================================
# Regression Test — Orchestrator Stability
# ==============================================================================


def test_regression_orchestrator_stability():
    """
    Regression test: ensure run_preprocessing.main() remains callable and
    structurally intact. This protects against accidental refactors that
    break the pipeline entry point.
    """
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")
    assert callable(rp.main), (
        "Regression: run_preprocessing.main() is no longer callable"
    )


# ==============================================================================
# Regression Test — No Heavy Imports at Module Load
# ==============================================================================


def test_regression_no_heavy_imports():
    """
    Regression test: ensure Stage 2 modules do not import heavy libraries
    (cfgrib, eccodes) at module load time. This protects startup performance
    and prevents accidental top-level GRIB parsing.
    """
    import sys

    banned = ["cfgrib", "eccodes"]

    for name in banned:
        assert name not in sys.modules, (
            f"Regression: heavy import detected during Stage 2 module load: {name}"
        )
