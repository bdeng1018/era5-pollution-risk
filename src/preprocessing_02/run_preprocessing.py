"""
Stage 2 Preprocessing Orchestrator (Parallelized)
=================================================

Builds HOURLY master metadata.json:

{
    "variables": {
        "<shortName>": {
            "YYYY-MM-DDTHH:MM": "/path/to/parquet",
            ...
        },
        ...
    },
    "timestamps": [
        "YYYY-MM-DDTHH:MM",
        ...
    ]
}
"""

import json
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from src.download_01.paths import Paths
from src.preprocessing_02.convert_grib_to_parquet import convert_grib_to_parquet
from src.preprocessing_02.inspect_grib import inspect_all_gribs
from src.preprocessing_02.unzip_grib import unzip_all_months
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Logging setup
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
# Step 1: Unzip monthly ZIP files
# ------------------------------------------------------------------------------

def step_unzip() -> list[Path]:
    logger.info("[stage2] Step 1: Unzipping monthly ZIP files")
    extracted = unzip_all_months()
    logger.info(f"[stage2] Unzipped {len(extracted)} GRIB files")
    return extracted


# ------------------------------------------------------------------------------
# Step 2: Inspect GRIB files
# ------------------------------------------------------------------------------

def step_inspect() -> list[dict]:
    logger.info("[stage2] Step 2: Inspecting GRIB files")

    paths = Paths()
    raw_dir = Path(paths.raw_dir)

    metadata = inspect_all_gribs(raw_dir)
    logger.info(f"[stage2] Inspected {len(metadata)} GRIB files")

    return metadata


# ------------------------------------------------------------------------------
# Step 3: Convert GRIB → Parquet (parallel)
# ------------------------------------------------------------------------------

def step_convert_parallel() -> list[dict]:
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
                meta = future.result()
                if meta is None:
                    raise ValueError("convert_grib_to_parquet returned None")

                results.append({
                    "path": str(grib_path),
                    "success": True,
                    "output": meta,
                })

                logger.info(
                    f"[stage2] OK → {grib_path} "
                    f"→ {len(meta['timestamps'])} hourly timestamps"
                )

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
# Step 4: Build HOURLY master metadata.json
# ------------------------------------------------------------------------------

def build_master_metadata(results: list[dict]) -> Path:
    """
    Build HOURLY master metadata.json directly from conversion results.

    New Stage 2 metadata format:

    {
        "grib_path": "...",
        "variables": {
            "<shortName>": { ts: parquet_path }
        },
        "timestamps": [...]
    }
    """

    paths = Paths()
    metadata_dir = Path(paths.metadata_dir)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    master = {
        "variables": {},
        "timestamps": set(),
    }

    for r in results:
        if not r["success"]:
            continue

        meta = r["output"]

        # Merge per-variable parquet paths
        for var, parquet_map in meta["variables"].items():
            if var not in master["variables"]:
                master["variables"][var] = {}

            for ts, parquet_path in parquet_map.items():
                master["variables"][var][ts] = parquet_path
                master["timestamps"].add(ts)

    # Convert timestamps set → sorted list
    master["timestamps"] = sorted(master["timestamps"])

    master_path = metadata_dir / "metadata.json"
    with open(master_path, "w") as f:
        json.dump(master, f, indent=2)

    logger.info(f"[stage2] Wrote master metadata → {master_path}")
    return master_path


# ------------------------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------------------------

def run_preprocessing():
    logger.info("========== Stage 2 Preprocessing Started ==========")

    extracted = step_unzip()
    metadata = step_inspect()
    results = step_convert_parallel()

    master_path = build_master_metadata(results)

    logger.info(f"========== Stage 2 Preprocessing Complete → {master_path} ==========")


def main():
    try:
        run_preprocessing()
    except Exception as e:
        raise RuntimeError(f"run_preprocessing.main() failed: {e}")


if __name__ == "__main__":
    main()
