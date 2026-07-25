"""
Convert ERA5 GRIB files to Parquet (Branch 1 + Branch 2)
========================================================

Purpose
-------
This module converts a single ERA5 GRIB file—either single-variable (Branch 1)
or multi-variable (Branch 2)—into structured Parquet output suitable for
downstream processing in Stage 3.

Responsibilities
----------------
1. Safely load each GRIB variable using cfgrib:
   - Multi-variable GRIBs → per-variable filter_by_keys
   - Single-variable GRIBs → filename → shortName mapping
   - Automatic fallback when filter_by_keys returns an empty dataset

2. Convert each variable to Parquet according to its class:
   - Hourly instantaneous variables → one Parquet per timestamp
   - Static variables (lsm) → one Parquet per variable
   - Flux/accumulated variables → converted but excluded from HOURLY metadata

3. Produce per-file conversion metadata describing:
   - Variable class (instantaneous, static, flux)
   - Generated Parquet paths
   - Hourly timestamps (instantaneous only)
   - Success/failure status for Stage 2 orchestration

Notes
-----
- This module does *not* build metadata.json.
- GRIB-level metadata is written separately as grib_metadata.json (diagnostic).
- Parquet-only canonical metadata.json is built by metadata_parquet.py.
"""

from pathlib import Path

import pandas as pd

from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)

# ------------------------------------------------------------------------------
# Filename → ERA5 shortName mapping
# ------------------------------------------------------------------------------

FILENAME_TO_SHORTNAME = {
    "10m_u_component_of_wind": "u10",
    "10m_v_component_of_wind": "v10",
    "2m_dewpoint_temperature": "d2m",
    "2m_temperature": "t2m",
    "mean_sea_level_pressure": "msl",
    "surface_pressure": "sp",
    "total_precipitation": "tp",
    "surface_latent_heat_flux": "slhf",
    "surface_net_solar_radiation": "ssr",
    "surface_net_thermal_radiation": "str",
    "surface_sensible_heat_flux": "sshf",
    "surface_solar_radiation_downward_clear_sky": "ssrdc",
    "surface_solar_radiation_downwards": "ssrd",
    "total_cloud_cover": "tcc",
    "evaporation": "e",
    "boundary_layer_height": "blh",
    "convective_available_potential_energy": "cape",
    "convective_inhibition": "cin",
    "land_sea_mask": "lsm",
    "total_column_ozone": "tco3",
    "total_column_water_vapour": "tcwv",
}

KNOWN_ERA5_VARS = list(FILENAME_TO_SHORTNAME.values())

# ------------------------------------------------------------------------------
# Flux variables (accumulated, different grid, NOT safe for Stage 3 merge)
# ------------------------------------------------------------------------------

FLUX_VARS = {"slhf", "sshf", "ssr", "ssrc", "ssrd", "str", "tp", "e"}

# ------------------------------------------------------------------------------
# Multi-variable probing (lazy heavy imports)
# ------------------------------------------------------------------------------


def list_grib_variables(grib_path: Path) -> list[str]:
    import xarray as xr

    vars = []
    for var in KNOWN_ERA5_VARS:
        try:
            ds = xr.open_dataset(
                grib_path,
                engine="cfgrib",
                filter_by_keys={"shortName": var},
                backend_kwargs={"indexpath": "", "read_keys": ["time", "step"]},
            )
            if ds.data_vars:
                vars.append(var)
        except Exception:
            continue
    return vars


# ------------------------------------------------------------------------------
# Single-variable GRIB detection
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
# Dataset → Parquet conversion
# ------------------------------------------------------------------------------


def _convert_dataset_to_parquet(
    ds, grib_path: Path, intermediate_dir: Path, var: str
) -> dict:

    parts = grib_path.stem.split("_")
    year = int(parts[-2])
    month = int(parts[-1])

    output_dir = intermediate_dir / str(year) / f"{month:02d}" / var
    output_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------------------------
    # STATIC OVERRIDE: lsm is ALWAYS static
    # --------------------------------------------------------------------------
    if var == "lsm":
        logger.info(f"[convert] {var} forced static (land-sea mask).")
        df = ds.to_dataframe().reset_index()

        # --- SAFE COORDINATE NORMALIZATION ---
        cols = df.columns
        if "valid_time" in cols and "time" in cols:
            df = df.drop(columns=["time"])
            df = df.rename(columns={"valid_time": "time"})
        elif "valid_time" in cols:
            df = df.rename(columns={"valid_time": "time"})

        df = df.rename(columns={"latitude": "lat", "longitude": "lon"})

        parquet_path = output_dir / f"{var}_{year}_{month}_static.parquet"
        df.to_parquet(parquet_path, index=False)

        return {
            "timestamps": [],
            "parquet_files": {"static": str(parquet_path)},
            "is_static": True,
            "is_flux": False,
        }

    # --------------------------------------------------------------------------
    # STATIC / MONTHLY FIELDS (rare)
    # --------------------------------------------------------------------------
    if "time" not in ds.coords and "valid_time" not in ds:
        logger.warning(
            f"[convert] {var} in {grib_path.name} has no time/valid_time → static/monthly."
        )

        df = ds.to_dataframe().reset_index()

        # --- SAFE COORDINATE NORMALIZATION ---
        cols = df.columns
        if "valid_time" in cols and "time" in cols:
            df = df.drop(columns=["time"])
            df = df.rename(columns={"valid_time": "time"})
        elif "valid_time" in cols:
            df = df.rename(columns={"valid_time": "time"})

        df = df.rename(columns={"latitude": "lat", "longitude": "lon"})

        parquet_path = output_dir / f"{var}_{year}_{month}_static.parquet"
        df.to_parquet(parquet_path, index=False)

        return {
            "timestamps": [],
            "parquet_files": {"static": str(parquet_path)},
            "is_static": True,
            "is_flux": var in FLUX_VARS,
        }

    # --------------------------------------------------------------------------
    # IMPORTANT: CIN TAIL-HOUR CLEANUP (January 2019)
    #
    # ERA5 CIN GRIB files include several hours from the previous month
    # (e.g., 2018-12-31T18:00, 2018-12-31T19:00, 2018-12-31T20:00).
    #
    # These timestamps are *correct* at the GRIB (IR₀) level but must be removed
    # at the Parquet (IR₁) level because Stage 3 relies on a clean, normalized
    # hourly timestamp index. Any leftover CIN Parquet files containing tail-hour
    # timestamps will contaminate metadata.json even after filtering.
    #
    # Correct IR boundary:
    #   - GRIB inspection (IR₀) is diagnostic-only.
    #   - Parquet metadata (IR₁) is canonical and must contain *only* valid hours.
    #
    # REQUIRED CLEANUP:
    #   DELETE all CIN Parquet files for January 2019:
    #
    #       data/intermediate/2019/01/cin/*.parquet
    #
    # Then rerun Stage 2 for January 2019 so that only clean hourly Parquet files
    # are regenerated. This deletion is safe, isolated, and does not affect any
    # other variables or months.
    #
    # This ensures:
    #   - metadata.json contains only valid hourly timestamps
    #   - Stage 3 chunk planning and merging remain deterministic
    #   - IR₁ → IR₂ evolution is clean and restart-safe
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # HOURLY FIELDS (instantaneous or flux)
    # --------------------------------------------------------------------------

    hourly_meta = {"timestamps": [], "parquet_files": {}, "is_static": False}

    # Always use 'time' — NEVER use 'valid_time'
    if "time" in ds.coords:
        times = pd.to_datetime(ds.time.values)
    else:
        raw_times = ds.indexes.get("time", None)
        if raw_times is not None:
            times = pd.to_datetime(raw_times)
        else:
            times = pd.to_datetime(
                [
                    (
                        ds.time.values[i]
                        if "time" in ds.coords
                        else ds.step.values[i]
                        if "step" in ds.coords
                        else i
                    )
                    for i in range(ds.dims.get("time", ds.dims.get("step", 0)))
                ]
            )

    # Deduplicate + sort
    times = pd.to_datetime(sorted(set(times)))

    for vt in times:
        ts = vt.strftime("%Y-%m-%dT%H:%M")

        if "time" in ds.coords:
            sel = ds.sel(time=vt)
        else:
            idx = list(times).index(vt)
            sel = ds.isel(time=idx) if "time" in ds.dims else ds.isel(step=idx)

        df = sel.to_dataframe().reset_index()

        # --- SAFE COORDINATE NORMALIZATION ---
        cols = df.columns
        if "valid_time" in cols and "time" in cols:
            df = df.drop(columns=["time"])
            df = df.rename(columns={"valid_time": "time"})
        elif "valid_time" in cols:
            df = df.rename(columns={"valid_time": "time"})

        df = df.rename(columns={"latitude": "lat", "longitude": "lon"})

        # --- FILTER OUT TAIL HOURS (e.g., CIN/CAPE 2018-12-31) ---
        month_start = pd.Timestamp(f"{year}-{month:02d}-01T00:00:00")
        df = df[df["time"] >= month_start]

        if (df["time"] < month_start).any():
            logger.warning(
                f"[convert] Tail-hour timestamps detected for {var}. "
                "Ensure old Parquets are deleted."
            )

        # If the slice is outside the month, skip writing Parquet
        if df.empty:
            continue

        parquet_path = output_dir / f"{var}_{year}_{month}_{ts}.parquet"
        df.to_parquet(parquet_path, index=False)

        hourly_meta["timestamps"].append(ts)
        hourly_meta["parquet_files"][ts] = str(parquet_path)

    hourly_meta["is_flux"] = var in FLUX_VARS
    return hourly_meta


# ------------------------------------------------------------------------------
# Branch 1: Single-variable conversion
# ------------------------------------------------------------------------------


def convert_single_variable(grib_path: Path, intermediate_dir: Path) -> dict:
    import xarray as xr

    logger.info(f"[convert] Single-variable GRIB → {grib_path.name}")

    parts = grib_path.stem.split("_")
    filename_var = "_".join(parts[:-2])
    var = FILENAME_TO_SHORTNAME.get(filename_var, filename_var)

    try:
        ds = xr.open_dataset(
            grib_path,
            engine="cfgrib",
            filter_by_keys={"shortName": var},
            backend_kwargs={"indexpath": "", "read_keys": ["time", "step"]},
        )
        if not ds.data_vars:
            logger.warning(
                f"[convert] filter_by_keys({var}) empty → full open fallback."
            )
            ds = xr.open_dataset(
                grib_path,
                engine="cfgrib",
                backend_kwargs={"indexpath": "", "read_keys": ["time", "step"]},
            )
    except Exception as e:
        logger.error(f"[convert] Failed to open {grib_path.name}: {e}")
        raise

    meta = _convert_dataset_to_parquet(ds, grib_path, intermediate_dir, var)

    return {
        "grib_path": str(grib_path),
        "variables": {var: meta["parquet_files"]},
        "timestamps": meta["timestamps"],
        "is_flux": meta.get("is_flux", False),
        "is_static": meta.get("is_static", False),
    }


# ------------------------------------------------------------------------------
# Branch 2: Multi-variable conversion
# ------------------------------------------------------------------------------


def convert_multi_variable(grib_path: Path, intermediate_dir: Path) -> dict:
    import xarray as xr

    logger.info(f"[convert] Multi-variable GRIB → {grib_path.name}")

    vars = list_grib_variables(grib_path)
    logger.info(f"[convert] Variables found: {vars}")

    meta = {"grib_path": str(grib_path), "variables": {}, "timestamps": set()}

    for var in vars:
        try:
            ds = ds = xr.open_dataset(
                grib_path,
                engine="cfgrib",
                filter_by_keys={"shortName": var},
                backend_kwargs={"indexpath": "", "read_keys": ["time", "step"]},
            )

            if not ds.data_vars:
                logger.warning(f"[convert] Empty dataset for {var} → skip.")
                continue
        except Exception as e:
            logger.warning(f"[convert] Failed var={var}: {e}")
            continue

        var_meta = _convert_dataset_to_parquet(ds, grib_path, intermediate_dir, var)
        meta["variables"][var] = var_meta["parquet_files"]
        meta["timestamps"].update(var_meta["timestamps"])

    meta["timestamps"] = sorted(meta["timestamps"])
    return meta


# ------------------------------------------------------------------------------
# Unified entrypoint
# ------------------------------------------------------------------------------


def convert_grib_to_parquet(grib_path: Path) -> dict:
    paths = Paths()
    intermediate_dir = paths.intermediate_dir
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    if is_single_variable_grib(grib_path):
        return convert_single_variable(grib_path, intermediate_dir)
    return convert_multi_variable(grib_path, intermediate_dir)


# ------------------------------------------------------------------------------
# Stage 2 public API entrypoint
# ------------------------------------------------------------------------------


def main():
    try:
        paths = Paths()
        raw_dir = paths.raw_dir

        grib_files = sorted(raw_dir.rglob("*.grib"))
        results = [convert_grib_to_parquet(g) for g in grib_files]
        return results

    except Exception as e:
        logger.error(f"[convert] main() failed: {e}")
        raise


if __name__ == "__main__":
    main()
