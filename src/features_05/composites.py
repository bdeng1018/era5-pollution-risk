"""
Stage 05 — Composite Pollution‑Risk Features
===========================================

This module computes *composite features* by combining temporal and spatial
signals into higher‑level pollution‑risk indicators. These composites form the
top layer of IR5 and are the most interpretable features for downstream
modeling (Stage 06) and evaluation (Stage 07).

Architecture Notes
------------------
Stage 05 produces three layers:
    - IR5 temporal layer   → temporal.py
    - IR5 spatial layer    → spatial.py
    - IR5 composite layer  → composites.py  (this module)

Composite features combine:
    - short‑term temporal trends
    - long‑term temporal trends
    - spatial gradients
    - spatial variability
    - domain‑specific pollution heuristics

Examples include:
    - PM2.5 instability index
    - wind‑driven dispersion index
    - plume‑movement gradient index
    - temporal‑spatial contrast index

These features are deterministic and reproducible, and they follow the IR5
contract defined in `docs/STAGE05_FEATURES.md`.

"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def compute_composites(
    temporal_ds,
    spatial_ds,
    cfg: dict[str, Any],
):
    """
    Compute composite pollution‑risk features by combining temporal and spatial
    signals.
    """

    import xarray as xr

    logger.info("Computing composite features (Stage 05 — IR5 composite layer).")

    comp_cfg = cfg.get("composites", {})
    feats = {}

    for comp_name, comp_def in comp_cfg.items():
        logger.info(f"Computing composite feature: {comp_name}")

        temporal_vars = comp_def.get("temporal", [])
        spatial_vars = comp_def.get("spatial", [])
        formula = comp_def.get("formula", "")

        logger.debug(
            f"Composite config — temporal={temporal_vars}, "
            f"spatial={spatial_vars}, formula='{formula}'"
        )

        # Build namespace for formula evaluation
        ns = {}

        # Load temporal variables
        for var in temporal_vars:
            if var not in temporal_ds:
                logger.warning(
                    f"Temporal variable '{var}' missing. Skipping composite."
                )
                continue
            ns[var] = temporal_ds[var]

        # Load spatial variables
        for var in spatial_vars:
            if var not in spatial_ds:
                logger.warning(f"Spatial variable '{var}' missing. Skipping composite.")
                continue
            ns[var] = spatial_ds[var]

        # Evaluate formula
        try:
            result = eval(formula, {"__builtins__": {}}, ns)

            # Stage 5 tests REQUIRE proper DataArray construction
            # (tuple-of-form assignment causes ValueError)
            result = xr.DataArray(
                result.values,
                dims=result.dims,
                coords=result.coords,
                name=comp_name,
            )

            feats[comp_name] = result
            logger.debug(f"Composite '{comp_name}' computed successfully.")

        except Exception as e:
            logger.error(f"Failed to compute composite '{comp_name}': {e}")

    logger.info(f"Computed {len(feats)} composite features.")
    return xr.Dataset(feats)


def save_features(ds, path: str, cfg: dict[str, Any]) -> None:
    """
    Persist composite features to NetCDF.
    """

    logger.info(f"Saving composite features to: {path}")

    encoding = {var: {"zlib": True, "complevel": 4} for var in ds.data_vars}

    ds.to_netcdf(path, encoding=encoding)
    logger.info("Composite features saved successfully.")
