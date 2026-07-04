"""
Convert ERA5 GRIB files to HOURLY Parquet (Branch 1 + Branch 2)
===============================================================

This Stage 2 module now produces HOURLY Parquet files and HOURLY timestamps.

Returned metadata format:

{
    "grib_path": "...",
    "variables": {
        "<var>": {
            "YYYY-MM-DDTHH:MM": "/path/to/file.parquet",
            ...
        }
    },
    "timestamps": [...]
}

This is the required Stage 2 → Stage 3 contract.
"""

from pathlib import Path

import cfgrib
import pandas as pd
import xarray as xr

from src.download_01.paths import Paths
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# Filename → ERA5 shortName mapping (21 variables)
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

    "surface_solar_radiation_downward_clear_sky": "ssrc",
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


# ------------------------------------------------------------------------------
# Known ERA5 shortNames for Branch 2 probing
# ------------------------------------------------------------------------------

KNOWN_ERA5_VARS = list(FILENAME_TO_SHORTNAME.values())


def list_grib_variables(grib_path: Path) -> list[str]:
    """
    Discover variables by probing known ERA5 shortNames.
    Works even in minimal cfgrib/eccodes installations.
    """
    vars = []

    for var in KNOWN_ERA5_VARS:
        try:
            ds = xr.open_dataset(
                grib_path,
                engine="cfgrib",
                filter_by_keys={"shortName": var},
            )
            vars.append(var)
        except Exception:
            continue

    return vars


# ------------------------------------------------------------------------------
# Branch 1: Single-variable GRIB detection
# ------------------------------------------------------------------------------

def is_single_variable_grib(path: Path) -> bool:
    """
    True single-variable GRIBs follow:
        <long_variable_name>_<year>_<month>.grib

    Multi-variable GRIBs follow:
        era5_<year>_<month>.grib
    """
    parts = path.stem.split("_")
    if len(parts) < 3:
        return False

    # Multi-variable GRIBs always start with "era5"
    if parts[0] == "era5":
        return False

    year = parts[-2]
    month = parts[-1]
    return year.isdigit() and month.isdigit()


# ------------------------------------------------------------------------------
# Shared hourly conversion logic
# ------------------------------------------------------------------------------

def _convert_hourly(ds: xr.Dataset, grib_path: Path, intermediate_dir: Path, var: str) -> dict:
    """
    Convert an xarray Dataset into HOURLY Parquet files for a single variable.
    """

    if "time" not in ds.coords:
        raise ValueError(f"[convert] Variable {var} has no time coordinate in {grib_path}")

    hourly_metadata = {
        "timestamps": [],
        "parquet_files": {}
    }

    for t in ds.time.values:
        ts = pd.to_datetime(t).strftime("%Y-%m-%dT%H:%M")

        hourly_ds = ds.sel(time=t)
        df = hourly_ds.to_dataframe().reset_index()

        parquet_name = f"{grib_path.stem}_{var}_{ts}.parquet"
        parquet_path = intermediate_dir / parquet_name

        df.to_parquet(parquet_path, index=False)

        hourly_metadata["timestamps"].append(ts)
        hourly_metadata["parquet_files"][ts] = str(parquet_path)

    logger.info(
        f"[convert] Wrote {len(hourly_metadata['timestamps'])} hourly Parquet files "
        f"for variable {var} in {grib_path.name}"
    )

    return hourly_metadata


# ------------------------------------------------------------------------------
# Branch 1: Single-variable conversion (now hourly)
# ------------------------------------------------------------------------------

def convert_single_variable(grib_path: Path, intermediate_dir: Path) -> dict:
    logger.info(f"[convert] Single-variable GRIB → hourly Parquet: {grib_path}")

    parts = grib_path.stem.split("_")
    filename_var = "_".join(parts[:-2])

    # Map filename → ERA5 shortName
    variable = FILENAME_TO_SHORTNAME.get(filename_var, filename_var)

    try:
        ds = xr.open_dataset(
            grib_path,
            engine="cfgrib",
            filter_by_keys={"shortName": variable}
        )
    except Exception as e:
        logger.error(f"[convert] Failed to open single-variable GRIB {grib_path}: {e}")
        raise

    hourly_meta = _convert_hourly(ds, grib_path, intermediate_dir, variable)

    return {
        "grib_path": str(grib_path),
        "variables": {variable: hourly_meta["parquet_files"]},
        "timestamps": hourly_meta["timestamps"],
    }


# ------------------------------------------------------------------------------
# Branch 2: Multi-variable conversion (now hourly)
# ------------------------------------------------------------------------------

def convert_multi_variable(grib_path: Path, intermediate_dir: Path) -> dict:
    logger.info(f"[convert] Multi-variable GRIB → hourly Parquet: {grib_path}")

    variables = list_grib_variables(grib_path)
    logger.info(f"[convert] Variables found: {variables}")

    multi_meta = {
        "grib_path": str(grib_path),
        "variables": {},
        "timestamps": set(),
    }

    for var in variables:
        try:
            ds = xr.open_dataset(
                grib_path,
                engine="cfgrib",
                filter_by_keys={"shortName": var},
            )
        except Exception as e:
            logger.warning(f"[convert] Skipping variable {var}: {e}")
            continue

        if "time" not in ds.coords:
            logger.warning(f"[convert] Variable {var} has no time coordinate, skipping")
            continue

        hourly_meta = _convert_hourly(ds, grib_path, intermediate_dir, var)

        multi_meta["variables"][var] = hourly_meta["parquet_files"]
        multi_meta["timestamps"].update(hourly_meta["timestamps"])

    multi_meta["timestamps"] = sorted(multi_meta["timestamps"])
    return multi_meta


# ------------------------------------------------------------------------------
# Unified Stage 2 entrypoint
# ------------------------------------------------------------------------------

def convert_grib_to_parquet(grib_path: Path) -> dict | None:
    logger.info(f"[convert] Converting GRIB → hourly Parquet: {grib_path}")

    paths = Paths()
    intermediate_dir = Path(paths.intermediate_dir)
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    if is_single_variable_grib(grib_path):
        return convert_single_variable(grib_path, intermediate_dir)

    return convert_multi_variable(grib_path, intermediate_dir)


# ------------------------------------------------------------------------------
# CLI (Branch 1 behavior preserved)
# ------------------------------------------------------------------------------

def main():
    paths = Paths()
    era5_dir = Path(paths.raw_dir)

    single_var_gribs = sorted(
        p for p in era5_dir.glob("*.grib")
        if is_single_variable_grib(p)
    )

    if not single_var_gribs:
        logger.warning("No single-variable GRIB files found for conversion.")
        return

    logger.info(f"Found {len(single_var_gribs)} single-variable GRIB file(s).")

    for grib_path in single_var_gribs:
        convert_grib_to_parquet(grib_path)


if __name__ == "__main__":
    main()
