"""
Stage 05 — Metadata Generation (IR5 Metadata Layer)
===================================================

This module generates metadata for Stage 05 feature outputs. Metadata is a
critical part of the IR5 contract and ensures reproducibility, traceability,
and scientific transparency across the entire pipeline.

Architecture Notes
------------------
Stage 04 produces IR4 metadata (grid alignment, mask, QC, temporal alignment).
Stage 05 builds on this by producing IR5 metadata describing:

    - temporal features computed
    - spatial features computed
    - composite features computed
    - configuration parameters used
    - IR4 → IR5 lineage
    - deterministic hashing fingerprints (optional)
    - timestamps, versions, and provenance

Metadata is written as JSON and stored under:

    data/features/metadata/stage5_metadata.json

This metadata is consumed by:
    - Stage 06 modeling (feature selection, reproducibility)
    - Stage 07 evaluation (auditability)
    - Stage 08 deployment (model lineage, versioning)

"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _extract_feature_list(ds) -> dict[str, Any]:
    """
    Extract a list of feature names and basic statistics from an IR5 dataset.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.debug("Extracting feature list from IR5 dataset.")

    features = list(ds.data_vars)
    dims = {var: list(ds[var].dims) for var in features}

    return {
        "count": len(features),
        "features": features,
        "dimensions": dims,
    }


def build_metadata(
    temporal_ds,
    spatial_ds,
    composite_ds,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """
    Build IR5 metadata describing all Stage 05 feature layers.
    """

    # Import xarray INSIDE function (Stage 2 safety)

    logger.info("Building IR5 metadata for Stage 05.")

    metadata = {
        "stage": "05",
        "layers": {
            "temporal": _extract_feature_list(temporal_ds),
            "spatial": _extract_feature_list(spatial_ds),
            "composite": _extract_feature_list(composite_ds),
        },
        "config": cfg,
        "provenance": {
            "source_tensor": cfg.get("paths", {}).get("input", "unknown"),
            "version": cfg.get("version", "unknown"),
        },
    }

    logger.info("IR5 metadata built successfully.")
    return metadata


def write_metadata(metadata: dict[str, Any], path: str, cfg: dict[str, Any]) -> None:
    """
    Write IR5 metadata to JSON.
    """

    logger.info(f"Writing IR5 metadata to: {path}")

    with open(path, "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)

    logger.info("IR5 metadata written successfully.")
