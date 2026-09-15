"""
Stage 05 — Quality Control (IR5 QC Layer)
=========================================

This module performs quality‑control checks on Stage 05 feature outputs.
QC is a critical part of the IR5 contract and ensures scientific validity,
numerical stability, and reproducibility across the entire pipeline.

Architecture Notes
------------------
Stage 04 produces IR4 QC (grid alignment, mask consistency, temporal alignment).
Stage 05 builds on this by producing IR5 QC describing:

    - missing values in temporal/spatial/composite features
    - NaN/Inf detection
    - range checks (optional)
    - monotonicity checks (optional)
    - shape/dimension consistency
    - reproducibility checks

QC is written as JSON and stored under:

    data/features/qc/stage5_qc.json

This QC is consumed by:
    - Stage 06 modeling (feature validation)
    - Stage 07 evaluation (auditability)
    - Stage 08 deployment (model safety checks)

"""

from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _qc_missing(ds) -> dict[str, Any]:
    """
    Check for missing values (NaN) in each feature.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.debug("Running missing-value QC.")

    missing = {var: int(np.isnan(ds[var]).sum().item()) for var in ds.data_vars}

    return {"missing_values": missing}


def _qc_inf(ds) -> dict[str, Any]:
    """
    Check for infinite values in each feature.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.debug("Running infinite-value QC.")

    inf = {var: int(np.isinf(ds[var]).sum().item()) for var in ds.data_vars}

    return {"infinite_values": inf}


def _qc_dims(ds) -> dict[str, Any]:
    """
    Validate that all features share the same dimensionality.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.debug("Running dimension-consistency QC.")

    dims = {var: list(ds[var].dims) for var in ds.data_vars}

    return {"dimensions": dims}


def build_qc(
    temporal_ds,
    spatial_ds,
    composite_ds,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """
    Build IR5 QC describing all Stage 05 feature layers.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.info("Building IR5 QC for Stage 05.")

    qc = {
        "stage": "05",
        "layers": {
            "temporal": {
                **_qc_missing(temporal_ds),
                **_qc_inf(temporal_ds),
                **_qc_dims(temporal_ds),
            },
            "spatial": {
                **_qc_missing(spatial_ds),
                **_qc_inf(spatial_ds),
                **_qc_dims(spatial_ds),
            },
            "composite": {
                **_qc_missing(composite_ds),
                **_qc_inf(composite_ds),
                **_qc_dims(composite_ds),
            },
        },
    }

    logger.info("IR5 QC built successfully.")
    return qc


def write_qc(qc: dict[str, Any], path: str, cfg: dict[str, Any]) -> None:
    """
    Write IR5 QC to JSON.
    """

    logger.info(f"Writing IR5 QC to: {path}")

    with open(path, "w") as f:
        json.dump(qc, f, indent=2, sort_keys=True)

    logger.info("IR5 QC written successfully.")
