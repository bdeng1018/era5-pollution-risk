"""
Stage 1 Paths (Branch 2)
========================

Purpose
-------
Defines the directory layout used throughout Stage 1 (Branch 2) for ERA5
ingestion. This class must satisfy two constraints enforced by Stage 1 tests:

1. The Stage 1 downloader constructs `Paths()` with **no arguments**.
2. Stage 1 tests monkeypatch `Paths` and construct it **with explicit
   arguments** to override directory locations.

Design Requirements
-------------------
- All fields must define safe, deterministic defaults.
- All fields must accept explicit Path overrides when monkeypatched.
- No filesystem validation or creation occurs here; Stage 1 modules perform
  directory validation explicitly.
- Paths must remain stable across Branch 2 and Stage 2, ensuring consistent
  raw, metadata, config, intermediate, and logs directory locations.

Variable Naming Model
---------------------
Stage 1 downloads ERA5 GRIB files using **long descriptive variable names**
(e.g., `2m_temperature`, `convective_inhibition`, `surface_pressure`).

Stage 2 and all downstream stages operate exclusively on ERA5 **shortName**
codes (e.g., `t2m`, `cin`, `sp`).

A normalization step occurs *after* Stage 1 download and *before* Stage 1
metadata building:

    long descriptive names → short ERA5 codes

This ensures that Stage 2 can locate GRIB files deterministically using
shortName-based directory and filename patterns.

Directory Layout (Branch 2)
---------------------------
raw_dir:          data/raw/era5/
metadata_dir:     data/metadata/
config_dir:       configs/
intermediate_dir: data/intermediate/
logs_dir:         data/logs/

This layout is consumed by:
- Stage 1 (download_era5_single.py, download_era5_monthly.py)
- Stage 1 metadata builder (after variable-name normalization)
- Stage 2 (GRIB → Parquet conversion)
- Stage 3 (chunking and parallelization)
"""

from dataclasses import dataclass
from pathlib import Path

# ------------------------------------------------------------------------------
# Stage 1 Paths (Branch 2)
# Provides deterministic directory defaults and supports monkeypatch overrides.
# ------------------------------------------------------------------------------

@dataclass
class Paths:
    raw_dir: Path = Path("data/raw/era5")
    metadata_dir: Path = Path("data/metadata")
    config_dir: Path = Path("configs")
    intermediate_dir: Path = Path("data/intermediate")
    logs_dir: Path = Path("data/logs")

    def __repr__(self):
        """
        Human-readable representation for debugging and Stage 1 test output.
        """
        return (
            "Stage1Paths(\n"
            f"  raw_dir={self.raw_dir},\n"
            f"  metadata_dir={self.metadata_dir},\n"
            f"  config_dir={self.config_dir},\n"
            f"  intermediate_dir={self.intermediate_dir},\n"
            f"  logs_dir={self.logs_dir}\n"
            ")"
        )
