"""
Stage 05 — Feature Registry (IR5 Registry)
==========================================

The IR5 Feature Registry defines the canonical ordering, grouping, and naming
of all Stage 05 features. It is the authoritative source for:

    - which features exist (temporal, spatial, composite)
    - how they are grouped
    - how they are named
    - how they should be consumed by Stage 06 modeling
    - how they should be validated in Stage 07 evaluation
    - how they should be exposed in Stage 08 deployment

Architecture Notes
------------------
The registry is a *declarative* structure that ensures reproducibility and
stability across versions. It prevents downstream code from relying on
implicit assumptions about feature names or ordering.

The registry is stored in YAML (`configs/stage5.yml`) and loaded here.

Registry Structure
------------------
The registry defines:

    registry:
      temporal:
        - pm2p5_roll_mean_6h
        - pm2p5_roll_mean_24h
        - pm2p5_delta_24h

      spatial:
        - pm2p5_mean_3x3
        - pm2p5_laplacian

      composite:
        - pm2p5_instability
        - dispersion_index

This module loads the registry and exposes helper functions for:

    - listing all IR5 features
    - listing features by group
    - validating that computed features match the registry
    - producing canonical ordering for Stage 06 modeling

"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def load_registry(cfg: dict[str, Any]) -> dict[str, list[str]]:
    """
    Load the IR5 feature registry from the Stage 05 configuration.

    Parameters
    ----------
    cfg : dict
        Stage 05 configuration dictionary loaded from stage5.yml.

    Returns
    -------
    dict
        Registry mapping:
            {
                "temporal": [...],
                "spatial": [...],
                "composite": [...]
            }

    Notes
    -----
    The registry is intentionally declarative and stable. It is the canonical
    definition of IR5 features and should be version-controlled.
    """
    logger.info("Loading IR5 feature registry.")

    registry = cfg.get("registry", {})
    temporal = registry.get("temporal", [])
    spatial = registry.get("spatial", [])
    composite = registry.get("composite", [])

    logger.info(
        f"Registry loaded — temporal={len(temporal)}, "
        f"spatial={len(spatial)}, composite={len(composite)}"
    )

    return {
        "temporal": temporal,
        "spatial": spatial,
        "composite": composite,
    }


def list_all_features(registry: dict[str, list[str]]) -> list[str]:
    """
    List all IR5 features in canonical order.

    Parameters
    ----------
    registry : dict
        Registry mapping loaded via load_registry().

    Returns
    -------
    list
        Flattened list of all IR5 features in canonical order.

    Notes
    -----
    Canonical ordering is:
        temporal → spatial → composite

    This ordering is used by:
        - Stage 06 modeling (feature vector construction)
        - Stage 07 evaluation (feature attribution)
        - Stage 08 deployment (model input schema)
    """
    logger.debug("Listing all IR5 features in canonical order.")

    return (
        registry.get("temporal", [])
        + registry.get("spatial", [])
        + registry.get("composite", [])
    )


def validate_features(
    temporal_ds,
    spatial_ds,
    composite_ds,
    registry: dict[str, list[str]],
) -> dict[str, Any]:
    """
    Validate that computed IR5 features match the registry.

    Parameters
    ----------
    temporal_ds : xr.Dataset
        IR5 temporal features.
    spatial_ds : xr.Dataset
        IR5 spatial features.
    composite_ds : xr.Dataset
        IR5 composite features.
    registry : dict
        Registry mapping loaded via load_registry().

    Returns
    -------
    dict
        Validation report describing missing or extra features.

    Architecture Notes
    ------------------
    Validation ensures:
        - reproducibility
        - correctness
        - alignment with IR5 contract
        - safety for downstream modeling

    This is not QC (which checks numerical validity). This is *schema validation*.
    """
    logger.info("Validating IR5 features against registry.")

    report = {
        "missing": [],
        "extra": [],
    }

    # Expected features
    expected_temporal = set(registry.get("temporal", []))
    expected_spatial = set(registry.get("spatial", []))
    expected_composite = set(registry.get("composite", []))

    # Actual features
    actual_temporal = set(temporal_ds.data_vars)
    actual_spatial = set(spatial_ds.data_vars)
    actual_composite = set(composite_ds.data_vars)

    # Missing features
    report["missing"] = list(
        (expected_temporal - actual_temporal)
        | (expected_spatial - actual_spatial)
        | (expected_composite - actual_composite)
    )

    # Extra features
    report["extra"] = list(
        (actual_temporal - expected_temporal)
        | (actual_spatial - expected_spatial)
        | (actual_composite - expected_composite)
    )

    logger.info(
        f"Registry validation — missing={len(report['missing'])}, "
        f"extra={len(report['extra'])}"
    )

    return report
