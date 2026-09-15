"""
Stage 05 — Temporal Feature Engineering
=======================================

This module computes *temporal features* from the Stage 04 spatiotemporal tensor.
It is the first step in the Stage 05 feature pipeline and is responsible for
transforming IR4 variables into IR5 temporal derivatives, rolling statistics,
and multi‑scale temporal windows.

Architecture Notes
------------------
Stage 04 produces a fully aligned, gap‑free, jitter‑free tensor with dimensions:

    (time, latitude, longitude, variable)

Stage 05 builds on this by computing temporal features such as:
    - rolling means (6h, 24h)
    - temporal deltas (24h)
    - short‑term vs long‑term gradients
    - multi‑scale temporal windows

These features are deterministic and reproducible, and they follow the IR5
contract defined in `docs/STAGE05_IR4_SCHEMA.md`.

This module is intentionally pure‑Python/xarray to preserve readability and
scientific transparency. Heavy lifting (deterministic merging, jitter removal)
was already handled in Stage 03/04 via C++.

"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def load_tensor(path: str):
    """
    Load the Stage 04 spatiotemporal tensor.
    """

    # Import xarray INSIDE function (Stage 2 safety)
    import xarray as xr

    logger.info(f"Loading Stage 04 tensor from: {path}")
    ds = xr.open_dataset(path)
    logger.info(
        f"Loaded tensor with dims: {ds.dims} and variables: {list(ds.data_vars)}"
    )
    return ds


def compute_temporal_features(ds, cfg: dict[str, Any]):
    """
    Compute temporal features over the IR4 tensor.
    """

    # Import xarray INSIDE function (Stage 2 safety)
    import xarray as xr

    logger.info("Computing temporal features (Stage 05 — IR5 temporal layer).")

    window_cfg = cfg.get("temporal", {})
    variables = window_cfg.get("variables", [])
    window_6h = window_cfg.get("window_6h", 6)
    window_24h = window_cfg.get("window_24h", 24)

    logger.info(
        f"Temporal config — variables={variables}, "
        f"6h_window={window_6h}, 24h_window={window_24h}"
    )

    feats = {}

    for var in variables:
        if var not in ds:
            logger.warning(f"Variable '{var}' not found in Stage 04 tensor. Skipping.")
            continue

        da = ds[var]
        logger.debug(f"Computing temporal features for variable: {var}")

        # Rolling mean (6h)
        rm6 = da.rolling(time=window_6h, center=True).mean()
        rm6 = xr.DataArray(
            rm6.values,
            dims=da.dims,
            coords=da.coords,
            name=f"{var}_roll_mean_6h",
        )
        feats[f"{var}_roll_mean_6h"] = rm6

        # Rolling mean (24h)
        rm24 = da.rolling(time=window_24h, center=True).mean()
        rm24 = xr.DataArray(
            rm24.values,
            dims=da.dims,
            coords=da.coords,
            name=f"{var}_roll_mean_24h",
        )
        feats[f"{var}_roll_mean_24h"] = rm24

        # Temporal delta (24h)
        delta = da.diff("time", n=window_24h)
        delta = xr.DataArray(
            delta.values,
            dims=delta.dims,
            coords=delta.coords,
            name=f"{var}_delta_24h",
        )
        feats[f"{var}_delta_24h"] = delta

    logger.info(f"Computed {len(feats)} temporal features.")
    return xr.Dataset(feats)


def save_features(ds, path: str, cfg: dict[str, Any]) -> None:
    """
    Persist temporal (or combined) features to NetCDF.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.info(f"Saving temporal features to: {path}")

    encoding = {var: {"zlib": True, "complevel": 4} for var in ds.data_vars}

    ds.to_netcdf(path, encoding=encoding)
    logger.info("Temporal features saved successfully.")
