"""
Stage 4 – Metadata Invariant (Upgraded)
======================================

Purpose
-------
Define, validate, and assemble the Stage 4 metadata contract.
Metadata must be deterministic, schema-consistent, reproducible,
and sufficiently rich for downstream ML pipelines and diagnostics.

Responsibilities
----------------
- Validate presence and type of all required metadata blocks
- Validate deeper schema fields (grid, mask, temporal, tensor, qc)
- Emit non-fatal warnings for incomplete metadata
- Ensure provenance integrity
- Produce deterministic metadata dictionary
"""

from typing import Any, Dict, List, Mapping

# ------------------------------------------------------------------------------
# Schema definition
# ------------------------------------------------------------------------------

STAGE4_METADATA_SCHEMA: Mapping[str, type] = {
    "grid": dict,
    "mask": dict,
    "qc": dict,
    "temporal": dict,
    "tensor": dict,
    "provenance": dict,
}

# ------------------------------------------------------------------------------
# Deep field requirements
# ------------------------------------------------------------------------------

GRID_REQUIRED_FIELDS = ["lat", "lon"]
MASK_REQUIRED_FIELDS = ["mask"]
TEMPORAL_REQUIRED_FIELDS = ["aligned_time", "frequency"]
TENSOR_REQUIRED_FIELDS = ["variables", "shape", "dtype_summary"]
QC_REQUIRED_FIELDS = [
    "qc_pass",
    "issues",
    "nan_count",
    "inf_count",
    "outlier_count",
    "zero_fields",
    "constant_fields",
    "physical_range_violations",
    "temporal_jumps",
    "spatial_jumps",
]
PROVENANCE_REQUIRED_FIELDS = ["source", "stage"]

# ------------------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------------------

def _validate_block(name: str, block: Mapping[str, Any], required_fields: List[str]):
    missing = [f for f in required_fields if f not in block]
    if missing:
        raise ValueError(
            f"[Stage 4][metadata] Missing required fields in '{name}': {missing}"
        )

def _warn_if(condition: bool, message: str, warnings: List[str]):
    if condition:
        warnings.append(message)

# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------

def validate_metadata(meta: Mapping[str, Any]) -> None:
    """
    Validate that metadata conforms to the Stage 4 schema and deep field requirements.
    """

    # 1. Required top-level keys
    for key, expected_type in STAGE4_METADATA_SCHEMA.items():
        if key not in meta:
            raise ValueError(f"[Stage 4][metadata] Missing metadata key: '{key}'")

        if not isinstance(meta[key], expected_type):
            raise ValueError(
                f"[Stage 4][metadata] Key '{key}' must be of type {expected_type.__name__}, "
                f"got {type(meta[key]).__name__}"
            )

    warnings: List[str] = []

    # 2. Deep validation
    _validate_block("grid", meta["grid"], GRID_REQUIRED_FIELDS)
    _validate_block("mask", meta["mask"], MASK_REQUIRED_FIELDS)
    _validate_block("temporal", meta["temporal"], TEMPORAL_REQUIRED_FIELDS)
    _validate_block("tensor", meta["tensor"], TENSOR_REQUIRED_FIELDS)
    _validate_block("qc", meta["qc"], QC_REQUIRED_FIELDS)
    _validate_block("provenance", meta["provenance"], PROVENANCE_REQUIRED_FIELDS)

    # 3. Soft checks (non-fatal)
    grid_meta = meta["grid"]
    _warn_if(len(grid_meta["lat"]) == 0, "grid_lat_empty", warnings)
    _warn_if(len(grid_meta["lon"]) == 0, "grid_lon_empty", warnings)

    mask_meta = meta["mask"]
    _warn_if(mask_meta["mask"] is None, "mask_array_none", warnings)

    temporal_meta = meta["temporal"]
    _warn_if(len(temporal_meta["aligned_time"]) == 0, "temporal_empty_aligned_time", warnings)

    tensor_meta = meta["tensor"]
    _warn_if(tensor_meta["shape"] is None, "tensor_missing_shape", warnings)

    qc_meta = meta["qc"]
    _warn_if(len(qc_meta["issues"]) > 0, "qc_has_issues", warnings)

    provenance = meta["provenance"]
    _warn_if(provenance["stage"] != "stage4", "provenance_stage_mismatch", warnings)

    if warnings:
        print("[Stage 4][metadata] warnings:", warnings)

# ------------------------------------------------------------------------------
# Construction
# ------------------------------------------------------------------------------

def build_metadata(
    grid_meta: Mapping[str, Any],
    mask_meta: Mapping[str, Any],
    qc_meta: Mapping[str, Any],
    temporal_meta: Mapping[str, Any],
    tensor_meta: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Construct Stage 4 metadata in a deterministic, schema-consistent format.
    """

    meta: Dict[str, Any] = {
        "grid": grid_meta,
        "mask": mask_meta,
        "qc": qc_meta,
        "temporal": temporal_meta,
        "tensor": tensor_meta,
        "provenance": provenance,
    }

    validate_metadata(meta)

    print("[Stage 4][metadata] Metadata validated successfully.")

    return meta
