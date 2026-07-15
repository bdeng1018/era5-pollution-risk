"""
Stage 2 Preprocessing Orchestrator (Branch 2)
=============================================

Purpose
-------
Stage 2 transforms raw ERA5 GRIB files—across multiple years, months, and
variables—into structured Parquet output and produces two metadata artifacts:

1. **grib_metadata.json** (IR₀ diagnostic)
   - Produced by GRIB inspection.
   - Contains raw GRIB-level information (variables, dimensions, timestamps).
   - Used only for diagnostics and validation.

2. **metadata.json** (IR₁ canonical Parquet metadata)
   - Built exclusively from Parquet files in:
         data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
   - Contains normalized hourly timestamps, shapes, dtypes, and paths.
   - Consumed by Stage 3 chunk planning and merging.

This orchestrator coordinates:
    1. Optional ZIP extraction (backward compatibility)
    2. GRIB inspection (diagnostic-only)
    3. GRIB → Parquet conversion (parallel, restart-safe)
    4. Parquet-only metadata.json assembly (canonical IR₁)

Variable Classes
----------------
Stage 2 correctly handles three ERA5 variable classes:

1. Instantaneous hourly variables (SAFE for Stage 3 merge)
   - t2m, d2m, u10, v10, msl, sp, tcc, blh, cape, cin, tco3, tcwv
   - Identical (time, lat, lon) grid
   - Contribute to HOURLY Parquet metadata.json

2. Static variables (ONLY lsm)
   - land_sea_mask (lsm)
   - No time dimension
   - Converted to Parquet but excluded from HOURLY timestamps

3. Flux / accumulated variables (NOT safe for Stage 3 merge)
   - slhf, sshf, ssr, ssrc, ssrd, str, tp, e
   - Different grid + accumulated semantics
   - Converted to Parquet but excluded from HOURLY timestamps

Parquet Directory Layout (IR₁)
------------------------------
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet

Each Parquet file contains exactly one timestamp and one variable.

Metadata Files
--------------
**grib_metadata.json** (IR₀)
    - GRIB-level inspection output.
    - Diagnostic-only; never used by Stage 3.

**metadata.json** (IR₁)
    - Canonical hourly metadata consumed by Stage 3.
    - Structure:
        {
            "<timestamp>": {
                "variable": "<shortName>",
                "path": "/path/to/parquet",
                "year": 2019,
                "month": 1,
                "dtype": "float32",
                "shape": [lat, lon]
            },
            ...
        }

Notes
-----
- Only instantaneous hourly variables contribute to metadata.json.
- Static and flux variables are converted but excluded from HOURLY timestamps.
- GRIB inspection does not influence metadata.json.
- Stage 2 is deterministic, restart-safe, and compatible with Branch 1 and Branch 2.
"""

import json
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from src.preprocessing_02.convert_grib_to_parquet import convert_grib_to_parquet
from src.preprocessing_02.inspect_grib import inspect_all_gribs
from src.preprocessing_02.metadata_parquet import (
    build_parquet_metadata,
    write_parquet_metadata_json,
)
from src.preprocessing_02.unzip_grib import unzip_all_months
from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------------------

def setup_logging():
    paths = Paths()
    logs_dir = paths.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(logs_dir / "preprocessing.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)


# ------------------------------------------------------------------------------
# Stage 2 success checker (per-GRIB conversion)
# ------------------------------------------------------------------------------

def stage2_success(meta: dict) -> bool:
    if not isinstance(meta, dict):
        return False
    if "variables" not in meta or "timestamps" not in meta:
        return False

    variables = meta["variables"]
    timestamps = meta["timestamps"]

    if not variables:
        return False

    for var, parquet_map in variables.items():

        # Static variable (lsm)
        if meta.get("is_static", False):
            if "static" not in parquet_map:
                return False
            if not parquet_map["static"]:
                return False
            continue

        # Flux variables → converted but timestamps ignored
        if meta.get("is_flux", False):
            if not parquet_map:
                return False
            continue

        # Hourly instantaneous variables
        if not timestamps:
            return False

        for ts in timestamps:
            if ts not in parquet_map:
                return False
            if not parquet_map[ts]:
                return False

    return True


# ------------------------------------------------------------------------------
# Step 1: Unzip monthly ZIP files
# ------------------------------------------------------------------------------

def step_unzip() -> list[Path]:
    logger.info("[stage2] Step 1: Unzipping monthly ZIP files")
    extracted = unzip_all_months()
    logger.info(f"[stage2] Unzipped {len(extracted)} GRIB files")
    return extracted


# ------------------------------------------------------------------------------
# Step 2: Inspect GRIB files (diagnostic-only → grib_metadata.json)
# ------------------------------------------------------------------------------

def step_inspect() -> Path:
    logger.info("[stage2] Step 2: Inspecting GRIB files")

    paths = Paths()
    raw_dir = paths.raw_dir

    grib_metadata = inspect_all_gribs(raw_dir)
    logger.info(f"[stage2] Inspected {len(grib_metadata)} GRIB files")

    metadata_dir = paths.metadata_dir
    metadata_dir.mkdir(parents=True, exist_ok=True)

    grib_metadata_path = metadata_dir / "grib_metadata.json"
    with open(grib_metadata_path, "w") as f:
        json.dump(grib_metadata, f, indent=2)

    logger.info(f"[stage2] Wrote GRIB diagnostic metadata → {grib_metadata_path}")
    return grib_metadata_path


# ------------------------------------------------------------------------------
# Delete stale eccodes index files
# ------------------------------------------------------------------------------

def cleanup_idx_files():
    paths = Paths()
    raw_dir = paths.raw_dir
    for idx in raw_dir.rglob("*.idx"):
        try:
            idx.unlink()
            logger.info(f"[stage2] Deleted stale index file: {idx}")
        except Exception as e:
            logger.warning(f"[stage2] Could not delete {idx}: {e}")


# ------------------------------------------------------------------------------
# Step 3: Convert GRIB → Parquet (parallel)
# ------------------------------------------------------------------------------

def step_convert_parallel() -> list[dict]:
    logger.info("[stage2] Step 3: Converting GRIB → Parquet (parallel)")

    paths = Paths()
    raw_dir = paths.raw_dir
    intermediate_dir = paths.intermediate_dir
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    grib_files = sorted(raw_dir.rglob("*.grib"))

    if not grib_files:
        logger.info("[stage2] No GRIB files found for conversion")
        return []

    max_workers = os.cpu_count() or 4
    logger.info(f"[stage2] Using {max_workers} workers for conversion")

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(convert_grib_to_parquet, grib_path): grib_path
            for grib_path in grib_files
        }

        for future in as_completed(futures):
            grib_path = futures[future]
            try:
                meta = future.result()
                if meta is None:
                    raise ValueError("convert_grib_to_parquet returned None")

                ok = stage2_success(meta)
                results.append({
                    "path": str(grib_path),
                    "success": ok,
                    "output": meta if ok else None,
                    "raw_output": meta,
                })

                if ok:
                    logger.info(
                        f"[stage2] OK → {grib_path.name} "
                        f"→ {len(meta['timestamps'])} hourly timestamps "
                        f"(flux={meta.get('is_flux', False)}, "
                        f"static={meta.get('is_static', False)})"
                    )
                else:
                    logger.error(
                        f"[stage2] INVALID METADATA → {grib_path.name}"
                    )

            except Exception as e:
                logger.error(f"[stage2] FAILED → {grib_path}: {e}")
                results.append({
                    "path": str(grib_path),
                    "success": False,
                    "error": str(e),
                    "output": None,
                    "raw_output": None,
                })

    logger.info(f"[stage2] Converted {len(results)} GRIB files")
    return results


# ------------------------------------------------------------------------------
# Step 4: Build Parquet-only HOURLY metadata.json
# ------------------------------------------------------------------------------

def step_build_parquet_metadata() -> Path:
    logger.info("[stage2] Step 4: Building Parquet-only metadata.json")

    metadata = build_parquet_metadata()
    write_parquet_metadata_json(metadata)

    paths = Paths()
    metadata_path = Path(paths.metadata_dir) / "metadata.json"

    logger.info(
        f"[stage2] Wrote Parquet-only metadata → {metadata_path} "
        f"({len(metadata)} timestamps)"
    )
    return metadata_path


# ------------------------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------------------------

def run_preprocessing():
    setup_logging()
    logger.info("========== Stage 2 Preprocessing Started ==========")

    paths = Paths()
    paths.raw_dir.mkdir(parents=True, exist_ok=True)
    paths.metadata_dir.mkdir(parents=True, exist_ok=True)
    paths.intermediate_dir.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)

    cleanup_idx_files()
    extracted = step_unzip()
    grib_metadata_path = step_inspect()
    results = step_convert_parallel()
    parquet_metadata_path = step_build_parquet_metadata()

    logger.info(
        "========== Stage 2 Preprocessing Complete ==========\n"
        f"GRIB metadata  → {grib_metadata_path}\n"
        f"Parquet metadata → {parquet_metadata_path}\n"
        f"Converted GRIB files: {len(results)}"
    )


def main():
    try:
        run_preprocessing()
    except Exception as e:
        raise RuntimeError(f"run_preprocessing.main() failed: {e}")


if __name__ == "__main__":
    main()
