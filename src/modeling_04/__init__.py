"""
Model training stage (Branch 1).

This package provides a minimal placeholder workflow for training a baseline
model using the features generated in features_03. Branch 1 keeps modeling
intentionally simple so the pipeline remains runnable end‑to‑end without
introducing real ML complexity.

Branch 1 Scope
--------------
- Load features.parquet from features_03
- Load minimal model configuration from model_config.yml
- Train a trivial baseline model defined in baseline_models.py
- Save a lightweight model artifact to models/model.pkl for downstream evaluation (stage 05)
- Provide a clean function signature for future expansion
- No hyperparameter tuning, model registry, metrics, or experiment tracking

Branch 2 Preview
----------------
Branch 2 will introduce:
- Multiple model classes and a full model registry
- Config‑driven training workflows
- Hyperparameter tuning and search strategies
- Train/validation/test splits
- Metrics, evaluation reports, and plots
- Model persistence, versioning, and experiment tracking
- Integration with feature metadata and transformation graphs

Modules
-------
train_model.py
    Branch 1 training entrypoint. Loads features, trains a trivial baseline
    model, and writes a minimal model artifact.

baseline_models.py
    Contains simple baseline model classes used in Branch 1 (e.g., MeanPredictor).
    Will expand in Branch 2 to include real model architectures.

Model artifacts are written to the top-level models/ directory (not data/).

Notes
-----
Branch 1 modeling is intentionally minimal. The purpose is to maintain a clean
pipeline structure and ensure downstream modules have predictable interfaces
without committing to a full ML training framework yet.
"""

# Optional: expose the main entrypoint for convenience
from .train_model import train_model