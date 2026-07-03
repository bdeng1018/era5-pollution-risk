"""
Stage 2 Preprocessing Orchestrator (Parallelized)
=================================================

This module runs the full Stage 2 preprocessing pipeline:

    1. Unzip monthly ERA5 ZIP files
    2. Inspect all GRIB files
    3. Convert GRIB → Parquet (parallelized)

This is the single entrypoint for Stage 2 and prepares data for
Stage 3 parallelization and Stage 4 merging.
"""

import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from src.preprocessing_02.convert_grib_to_parquet import convert_grib_to_parquet
from src.preprocessing_02.inspect_grib import inspect_all_gribs
from src.preprocessing_02.unzip_grib import unzip_all_months
from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Stage 2 logging configuration
# ------------------------------------------------------------------------------

paths = Paths()
logs_dir = Path(paths.logs_dir)
logs_dir.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(logs_dir / "preprocessing.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.INFO)


# ------------------------------------------------------------------------------
# Step 1: Unzip
# ------------------------------------------------------------------------------

def step_unzip() -> list[Path]:
    logger.info("[stage2] Step 1: Unzipping monthly ZIP files")
    extracted = unzip_all_months()
    logger.info(f"[stage2] Unzipped {len(extracted)} GRIB files")
    return extracted


# ------------------------------------------------------------------------------
# Step 2: Inspect
# ------------------------------------------------------------------------------

def step_inspect() -> list[dict]:
    logger.info("[stage2] Step 2: Inspecting GRIB files")

    paths = Paths()
    raw_dir = Path(paths.raw_dir)

    metadata = inspect_all_gribs(raw_dir)
    logger.info(f"[stage2] Inspected {len(metadata)} GRIB files")

    return metadata


# ------------------------------------------------------------------------------
# Step 3: Convert (Parallel)
# ------------------------------------------------------------------------------

def step_convert_parallel() -> list[dict]:
    """
    Convert all GRIB files to Parquet using multi-process parallelism.
    """
    logger.info("[stage2] Step 3: Converting GRIB → Parquet (parallel)")

    paths = Paths()
    raw_dir = Path(paths.raw_dir)
    intermediate_dir = Path(paths.intermediate_dir)
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    grib_files = sorted(raw_dir.glob("*.grib"))
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
                parquet_path = future.result()
                results.append({
                    "path": str(grib_path),
                    "success": True,
                    "output": str(parquet_path) if parquet_path else None,
                })
                logger.info(f"[stage2] OK → {grib_path} → {parquet_path}")
            except Exception as e:
                logger.error(f"[stage2] FAILED → {grib_path}: {e}")
                results.append({
                    "path": str(grib_path),
                    "success": False,
                    "error": str(e),
                })

    logger.info(f"[stage2] Converted {len(results)} GRIB files")
    return results


# ------------------------------------------------------------------------------
# Unified Stage 2 pipeline
# ------------------------------------------------------------------------------

def run_preprocessing():
    logger.info("========== Stage 2 Preprocessing Started ==========")

    extracted = step_unzip()
    metadata = step_inspect()
    results = step_convert_parallel()

    logger.info("========== Stage 2 Preprocessing Complete ==========")


# ------------------------------------------------------------------------------
# CLI entrypoint
# ------------------------------------------------------------------------------

def main():
    try:
        run_preprocessing()
    except Exception as e:
        raise RuntimeError(f"run_preprocessing.main() failed: {e}")


if __name__ == "__main__":
    main()
