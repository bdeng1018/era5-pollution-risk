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

import importlib
from pathlib import Path

# ==============================================================================
# Unit Test — unzip_grib
# ==============================================================================

def test_unzip_module_has_main():
    unzip = importlib.import_module("src.preprocessing_02.unzip_grib")
    assert hasattr(unzip, "main")
    assert callable(unzip.main)


# ==============================================================================
# Unit Test — inspect_grib
# ==============================================================================

def test_inspect_module_has_main():
    inspect = importlib.import_module("src.preprocessing_02.inspect_grib")
    assert hasattr(inspect, "main")
    assert callable(inspect.main)


# ==============================================================================
# Unit Test — convert_grib_to_parquet
# ==============================================================================

def test_convert_module_has_main():
    convert = importlib.import_module("src.preprocessing_02.convert_grib_to_parquet")
    assert hasattr(convert, "main")
    assert callable(convert.main)


# ==============================================================================
# Unit Test — run_preprocessing
# ==============================================================================

def test_run_preprocessing_has_main():
    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")
    assert hasattr(rp, "main")
    assert callable(rp.main)


# ==============================================================================
# Unit Test — Paths() Utility
# ==============================================================================

def test_paths_resolve_directories():
    from src.utils.paths import Paths
    p = Paths()

    required_attrs = ["raw_dir", "intermediate_dir", "logs_dir"]

    for attr in required_attrs:
        assert hasattr(p, attr)
        assert isinstance(getattr(p, attr), Path)


# ==============================================================================
# Unit Test — Ensure no heavy imports occur
# ==============================================================================

def test_no_heavy_imports():
    import sys
    banned = ["cfgrib", "eccodes"]
    for name in banned:
        assert name not in sys.modules
