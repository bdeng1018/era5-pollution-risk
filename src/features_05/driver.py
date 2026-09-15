"""
Stage 05 — Feature Pipeline Driver (IR5 Orchestration)
======================================================

This module orchestrates the entire Stage 05 feature pipeline:

    1. Load Stage 04 tensor (IR4)
    2. Compute temporal features (IR5 temporal layer)
    3. Compute spatial features (IR5 spatial layer)
    4. Compute composite features (IR5 composite layer)
    5. Build + write metadata (IR5 metadata layer)
    6. Build + write QC (IR5 QC layer)
    7. Validate features against the IR5 registry
"""

from __future__ import annotations

import argparse
from typing import Any

from src.utils.config import load_yaml
from src.utils.logging import add_file_logging, get_logger
from src.utils.paths import get_path

from .composites import compute_composites
from .metadata import build_metadata, write_metadata
from .qc import build_qc, write_qc
from .registry import load_registry, validate_features
from .spatial import compute_spatial_features
from .temporal import compute_temporal_features, load_tensor


def run_stage05(cfg: dict[str, Any]) -> None:
    """
    Execute the full Stage 05 feature pipeline.
    """

    # ======================================================================
    # Configure logging BEFORE any feature computation
    # ======================================================================
    if "paths" in cfg and "log" in cfg["paths"]:
        log_path = cfg["paths"]["log"]
    else:
        log_path = "data/logs/stage5.log"

    add_file_logging(log_path)
    logger = get_logger(__name__)
    logger.info("=== Stage 05: Feature Pipeline (IR5) Starting ===")

    # ======================================================================
    # 1. Load Stage 04 tensor
    # ======================================================================
    input_path = get_path(cfg, "paths.input")
    logger.info(f"Loading Stage 04 tensor from: {input_path}")
    ds = load_tensor(input_path)

    # ======================================================================
    # 2. Temporal features
    # ======================================================================
    logger.info("Computing IR5 temporal features.")
    temporal_ds = compute_temporal_features(ds, cfg)

    # ======================================================================
    # 3. Spatial features
    # ======================================================================
    logger.info("Computing IR5 spatial features.")
    spatial_ds = compute_spatial_features(ds, cfg)

    # ======================================================================
    # 4. Composite features
    # ======================================================================
    logger.info("Computing IR5 composite features.")
    composite_ds = compute_composites(temporal_ds, spatial_ds, cfg)

    # ======================================================================
    # 5. Metadata
    # ======================================================================
    metadata_path = get_path(cfg, "paths.metadata")
    logger.info("Building IR5 metadata.")
    metadata = build_metadata(temporal_ds, spatial_ds, composite_ds, cfg)
    write_metadata(metadata, metadata_path, cfg)

    # ======================================================================
    # 6. QC
    # ======================================================================
    qc_path = get_path(cfg, "paths.qc")
    logger.info("Building IR5 QC.")
    qc = build_qc(temporal_ds, spatial_ds, composite_ds, cfg)
    write_qc(qc, qc_path, cfg)

    # ======================================================================
    # 7. Registry validation
    # ======================================================================
    logger.info("Validating IR5 features against registry.")
    registry = load_registry(cfg)
    validation_report = validate_features(
        temporal_ds, spatial_ds, composite_ds, registry
    )

    if validation_report["missing"] or validation_report["extra"]:
        logger.warning(
            f"Registry validation issues — missing={validation_report['missing']}, "
            f"extra={validation_report['extra']}"
        )
    else:
        logger.info("Registry validation passed with no issues.")

    # ======================================================================
    # 8. Save final IR5 feature dataset
    # ======================================================================
    output_path = get_path(cfg, "paths.output")
    logger.info(f"Saving IR5 features to: {output_path}")

    final_ds = temporal_ds.merge(spatial_ds).merge(composite_ds)
    final_ds.to_netcdf(output_path)

    logger.info("=== Stage 05: Feature Pipeline (IR5) Completed Successfully ===")


def main() -> None:
    """
    CLI entrypoint for Stage 05.
    """
    parser = argparse.ArgumentParser(description="Stage 05 Feature Pipeline")
    parser.add_argument("--config", required=True, help="Path to stage5.yml")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    run_stage05(cfg)


if __name__ == "__main__":
    main()
