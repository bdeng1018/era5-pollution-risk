"""
Stage 2: Inspect ERA5 GRIB Files (Branch 1 + Branch 2)
======================================================

Purpose
-------
This module inspects ERA5 GRIB files and produces lightweight GRIB-level
diagnostic metadata (IR₀). It supports both Branch 1 single‑variable GRIBs and
Branch 2 multi‑variable monthly GRIBs.

GRIB inspection is used to:
    - Detect available variables within each GRIB file
    - Validate GRIB structure, dimensions, and coordinate consistency
    - Identify static, instantaneous, and flux/accumulated variable classes
    - Provide diagnostic information for Stage 2 conversion and logging

IR Boundary (New Architecture)
------------------------------
GRIB inspection produces **diagnostic-only metadata** written to:

    grib_metadata.json

This file is *not* used for Stage 3 merging or timestamp planning.

Canonical hourly metadata (IR₁) is built exclusively from Parquet files by
metadata_parquet.py and written to:

    metadata.json

This separation ensures deterministic, restart‑safe behavior and prevents
GRIB-level tail-hour contamination from affecting downstream stages.

Unified Behavior
----------------
inspect_all_gribs() automatically detects GRIB type and dispatches to the
appropriate inspection path:
    - Branch 1: single-variable GRIBs
    - Branch 2: multi-variable monthly GRIBs

Returned metadata is used only for:
    - Stage 2 diagnostics
    - Logging
    - Conversion validation

Public API Contract
-------------------
Stage 2 tests require:
    - inspect_grib.main() must exist
    - inspect_grib.main() must call inspect_all_gribs()
    - inspect_grib.main() must not crash

This module does *not* build metadata.json and does *not* influence IR₁.
"""

from pathlib import Path

from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Detect Branch 1 single‑variable GRIBs
# ------------------------------------------------------------------------------


def is_single_variable_grib(path: Path) -> bool:
    parts = path.stem.split("_")

    if parts[0].lower() == "era5":
        return False

    if len(parts) < 3:
        return False

    year = parts[-2]
    month = parts[-1]
    return year.isdigit() and month.isdigit()


# ------------------------------------------------------------------------------
# Branch 1: Single‑variable GRIB inspection
# ------------------------------------------------------------------------------


def inspect_grib_single(grib_path: Path):
    import xarray as xr

    if not is_single_variable_grib(grib_path):
        return None

    logger.info(f"[inspect] Inspecting single-variable GRIB: {grib_path.name}")

    parts = grib_path.stem.split("_")
    filename_var = "_".join(parts[:-2])

    from src.preprocessing_02.convert_grib_to_parquet import FILENAME_TO_SHORTNAME

    shortname = FILENAME_TO_SHORTNAME.get(filename_var, filename_var)

    try:
        ds = xr.open_dataset(
            grib_path,
            engine="cfgrib",
            filter_by_keys={"shortName": shortname},
        )

        if not ds.data_vars:
            logger.warning(
                f"[inspect] filter_by_keys({shortname}) empty → full open fallback."
            )
            ds = xr.open_dataset(grib_path, engine="cfgrib")

    except Exception as e:
        logger.error(f"[inspect] Failed to open {grib_path}: {e}")
        return None

    logger.info(f"[inspect] Dimensions: {ds.sizes}")
    logger.info(f"[inspect] Variables: {list(ds.data_vars)}")

    return {
        "path": str(grib_path),
        "variables": list(ds.data_vars),
        "dims": dict(ds.sizes),
        "coords": list(ds.coords),
        "error": None,
    }


# ------------------------------------------------------------------------------
# Branch 2: Multi‑variable GRIB inspection
# ------------------------------------------------------------------------------


def inspect_grib_multi(grib_path: Path) -> dict:
    import eccodes

    logger.info(f"[inspect] Inspecting multi-variable GRIB: {grib_path.name}")

    try:
        index = eccodes.codes_index_new_from_file(
            str(grib_path), "shortName,dataDate,dataTime"
        )

        variables = set()
        times = set()
        lat = None
        lon = None

        shortnames = eccodes.codes_index_get(index, "shortName") or []

        for shortName in shortnames:
            if shortName is None:
                continue

            variables.add(shortName)
            eccodes.codes_index_select(index, "shortName", shortName)

            while True:
                gid = eccodes.codes_index_get(index, "message")
                if gid is None:
                    break

                try:
                    dataDate = eccodes.codes_get(gid, "dataDate")
                    dataTime = eccodes.codes_get(gid, "dataTime")
                    if dataDate is not None and dataTime is not None:
                        times.add(dataDate * 100 + dataTime)
                except Exception:
                    pass

                if lat is None or lon is None:
                    try:
                        lat = eccodes.codes_get(gid, "Nj")
                        lon = eccodes.codes_get(gid, "Ni")
                    except Exception:
                        pass

                eccodes.codes_release(gid)

        eccodes.codes_index_release(index)

        dims = {
            "time": len(times),
            "lat": lat,
            "lon": lon,
        }

        return {
            "path": str(grib_path),
            "variables": sorted(variables),
            "dims": dims,
            "coords": ["time", "lat", "lon"],
            "size_bytes": grib_path.stat().st_size,
            "error": None,
        }

    except Exception as e:
        logger.error(
            f"[inspect] Failed to inspect multi-variable GRIB {grib_path}: {e}"
        )
        return {
            "path": str(grib_path),
            "variables": [],
            "dims": {},
            "coords": [],
            "size_bytes": grib_path.stat().st_size,
            "error": str(e),
        }


# ------------------------------------------------------------------------------
# Unified inspection entrypoint
# ------------------------------------------------------------------------------


def inspect_all_gribs(raw_dir: Path | str) -> list[dict]:
    raw_dir = Path(raw_dir)

    grib_files = sorted(raw_dir.rglob("*.grib"))
    logger.info(f"[inspect] Found {len(grib_files)} GRIB files under {raw_dir}")

    results = []

    for grib_path in grib_files:
        if is_single_variable_grib(grib_path):
            results.append(inspect_grib_single(grib_path))
        else:
            results.append(inspect_grib_multi(grib_path))

    return results


# ------------------------------------------------------------------------------
# Stage 2 public API entrypoint
# ------------------------------------------------------------------------------


def main():
    try:
        paths = Paths()
        raw_dir = paths.raw_dir
        return inspect_all_gribs(raw_dir)
    except Exception as e:
        logger.error(f"[inspect] main() failed: {e}")
        raise


if __name__ == "__main__":
    main()
