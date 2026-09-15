"""
Stage 05 — Feature Engineering (IR5)
====================================

This package exposes the public API for Stage 05 feature engineering.
It provides access to:

    - IR5 orchestration (run_stage05)
    - IR5 temporal features
    - IR5 spatial features
    - IR5 composite features
    - IR5 metadata + QC builders
    - IR5 registry utilities

All heavy logic lives in the respective modules. This file simply
provides a clean import surface for downstream stages (06–08).
"""

from .composites import compute_composites
from .driver import run_stage05

# Metadata + QC
from .metadata import build_metadata, write_metadata
from .qc import build_qc, write_qc

# Registry utilities
from .registry import load_registry, validate_features
from .spatial import compute_spatial_features

# Feature layers
from .temporal import compute_temporal_features, load_tensor

__all__ = [
    "build_metadata",
    "build_qc",
    "compute_composites",
    "compute_spatial_features",
    "compute_temporal_features",
    "load_registry",
    "load_tensor",
    "run_stage05",
    "validate_features",
    "write_metadata",
    "write_qc",
]
