"""
Feature engineering stage (Branch 1).

This package contains minimal placeholder functionality for generating
basic features from ERA5 Parquet data. Branch 1 keeps this intentionally
lightweight: only two modules are included, and both provide simple,
non-destructive feature scaffolding.

Branch 1 modules:
    - feature_definitions.py — placeholder feature registry
    - build_features.py      — minimal feature engineering entrypoint

Branch 2 will add:
    - full feature registry with transformations
    - variable-level metadata tracking
    - schema validation
    - multi-file feature generation
    - parallel feature computation
    - feature provenance + logging
"""

# Optional: expose the main entrypoint for convenience
from .build_features import build_features as build_features
