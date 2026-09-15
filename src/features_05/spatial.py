"""
Stage 05 — Spatial Feature Engineering
======================================

This module computes *spatial features* from the Stage 04 spatiotemporal tensor.
Spatial features capture neighborhood structure, local gradients, and spatial
patterns that temporal features alone cannot represent.

Architecture Notes
------------------
Stage 04 produces a fully aligned IR4 tensor with dimensions:

    (time, latitude, longitude, variable)

Stage 05 builds on this by computing spatial features such as:
    - 3x3 neighborhood means
    - spatial gradients (dx, dy)
    - Laplacian-like kernels
    - local contrast / variability

These features form the IR5 spatial layer, complementing temporal features and
feeding into composite pollution‑risk indices.

Why Spatial Features Matter
---------------------------
Pollution risk is not only temporal (e.g., rising PM2.5) but also spatial:
    - plumes move across grids
    - gradients indicate transport
    - hotspots form in clusters
    - spatial variability predicts instability

This module uses pure Python/xarray for transparency and reproducibility.
Heavy deterministic operations (mask alignment, jitter removal) were already
handled in Stage 04.

"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _apply_kernel(da, kernel: np.ndarray, name: str):
    """
    Apply a 2D convolution kernel to a DataArray using xarray's rolling windows.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.debug(f"Applying spatial kernel for feature: {name}")

    # Normalize kernel for deterministic behavior
    kernel = kernel.astype(float)
    kernel = kernel / kernel.sum() if kernel.sum() != 0 else kernel

    # Rolling window over lat/lon
    rolled = da.rolling(
        lat=kernel.shape[0], lon=kernel.shape[1], center=True
    ).construct(lat="lat_win", lon="lon_win")

    # Weighted sum over the window
    conv = (rolled * kernel).sum(dim=("lat_win", "lon_win"))
    conv = conv.rename(name)

    return conv


def compute_spatial_features(ds, cfg: dict[str, Any]):
    """
    Compute spatial features over the IR4 tensor.
    """

    # Import xarray INSIDE function (Stage 2 safety)
    import xarray as xr

    logger.info("Computing spatial features (Stage 05 — IR5 spatial layer).")

    spatial_cfg = cfg.get("spatial", {})
    variables = spatial_cfg.get("variables", [])
    kernels_cfg = spatial_cfg.get("kernels", {})

    logger.info(
        f"Spatial config — variables={variables}, kernels={list(kernels_cfg.keys())}"
    )

    feats = {}

    for var in variables:
        if var not in ds:
            logger.warning(f"Variable '{var}' not found in Stage 04 tensor. Skipping.")
            continue

        da = ds[var]
        logger.debug(f"Computing spatial features for variable: {var}")

        for kernel_name, kernel_matrix in kernels_cfg.items():
            kernel = np.array(kernel_matrix)
            feat_name = f"{var}_{kernel_name}"

            feats[feat_name] = _apply_kernel(da, kernel, feat_name)

    logger.info(f"Computed {len(feats)} spatial features.")
    return xr.Dataset(feats)


def save_features(ds, path: str, cfg: dict[str, Any]) -> None:
    """
    Persist spatial (or combined) features to NetCDF.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.info(f"Saving spatial features to: {path}")

    encoding = {var: {"zlib": True, "complevel": 4} for var in ds.data_vars}

    ds.to_netcdf(path, encoding=encoding)
    logger.info("Spatial features saved successfully.")
