"""
Stage 2 — Parquet-only metadata builder
=======================================

Purpose
-------
This module builds the canonical Stage 2 metadata.json *exclusively* from IR₁
(hourly Parquet files). GRIB inspection metadata is diagnostic-only and is
written separately to grib_metadata.json.

IR Boundary
-----------
- GRIB-level metadata (IR₀) → diagnostic, never used for merging.
- Parquet-level metadata (IR₁) → canonical hourly metadata consumed by Stage 3.

Directory Structure (IR₁)
-------------------------
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet

Each Parquet file contains exactly one timestamp and one variable. This module
scans the full IR₁ directory tree, extracts timestamps, shapes, dtypes, and
paths, and writes a deterministic, restart-safe metadata.json.

Downstream Usage
----------------
Stage 3 chunk planning and merging rely *exclusively* on metadata.json. GRIB
metadata plays no role in downstream processing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


def build_parquet_metadata() -> dict:
    """
    Scan all Stage 2 Parquet files and build deterministic metadata.json.

    FLAT STRUCTURE (Stage 3 compatible):
    {
        "<timestamp>::<variable>": {
            "timestamp": "<timestamp>",
            "variable": "<var>",
            "path": "<full parquet path>",
            "year": 2019,
            "month": 1,
            "dtype": "float64",
            "shape": [153],
        },
        ...
    }
    """

    paths = Paths()
    intermediate_dir = Path(paths.intermediate_dir)

    metadata = {}

    # Directory structure:
    # data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
    for year_dir in intermediate_dir.iterdir():
        if not year_dir.is_dir():
            continue

        try:
            year = int(year_dir.name)
        except ValueError:
            logger.warning(f"[stage2] Skipping non-year directory: {year_dir}")
            continue

        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue

            try:
                month = int(month_dir.name)
            except ValueError:
                logger.warning(f"[stage2] Skipping non-month directory: {month_dir}")
                continue

            for var_dir in month_dir.iterdir():
                if not var_dir.is_dir():
                    continue

                variable = var_dir.name

                for parquet_file in var_dir.glob("*.parquet"):
                    try:
                        df = pd.read_parquet(parquet_file)

                        # Expect exactly one timestamp per file
                        ts = df["time"].iloc[0]
                        ts_str = str(ts)

                        # Identify the actual data column (exclude coords)
                        data_cols = [c for c in df.columns if c not in ("time", "latitude", "longitude")]
                        if not data_cols:
                            raise ValueError(f"No data column found in {parquet_file}")

                        col = data_cols[0]

                        # FLAT KEY: "<timestamp>::<variable>"
                        key = f"{ts_str}::{variable}"

                        metadata[key] = {
                            "timestamp": ts_str,
                            "variable": variable,
                            "path": str(parquet_file),
                            "year": year,
                            "month": month,
                            "dtype": str(df.dtypes[col]),
                            "shape": list(df[col].values.shape),
                        }

                    except Exception as e:
                        logger.error(f"[stage2] Failed reading {parquet_file}: {e}")

    logger.info(f"[stage2] Built metadata entries: {len(metadata)}")
    return metadata


def write_parquet_metadata_json(metadata: dict) -> None:
    """Write metadata.json to disk."""
    paths = Paths()
    metadata_path = Path(paths.metadata_dir) / "metadata.json"

    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    logger.info(f"[stage2] Wrote metadata.json → {metadata_path}")


if __name__ == "__main__":
    logger.info("[stage2] Starting metadata rebuild")
    metadata = build_parquet_metadata()
    write_parquet_metadata_json(metadata)
    logger.info("[stage2] Metadata rebuild complete")
