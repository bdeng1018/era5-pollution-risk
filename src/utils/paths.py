"""
Paths Utility (Branch 2)
------------------------

Provides deterministic, side‑effect‑free path resolution for the ERA5
pipeline. All directory paths are loaded from `configs/paths.yml` and
resolved relative to the project root unless `ERA5_BASE_DIR` is set,
which enables Stage 2 test isolation.

Branch 2 Notes
--------------
- All directory paths originate from configs/paths.yml.
- project_root is resolved automatically (never stored in YAML).
- No directory creation occurs in this module.
- All attributes must be pathlib.Path objects (required by Stage 1–3 tests).
- ERA5_BASE_DIR overrides project_root for deterministic test isolation.

Branch 3 Notes
--------------
Future AI/LLM/RAG tooling may read paths from this utility but will not
modify deterministic path resolution. Any AI‑specific storage locations
will live in separate modules to preserve Branch 2 invariants.

Invariant
---------
This module must remain:
- deterministic
- side‑effect‑free
- import‑safe during pytest collection
- free of heavy dependencies
"""

import os
from pathlib import Path

from src.utils.config import load_paths


class Paths:
    """
    Branch 2 path manager.
    Loads all required directories from configs/paths.yml and resolves
    them relative to the project root, unless ERA5_BASE_DIR is set
    (used by Stage 2 tests for isolation).
    """

    def __init__(self):
        cfg = load_paths()

        # Test isolation: ERA5_BASE_DIR overrides project root
        base_override = os.getenv("ERA5_BASE_DIR")

        if base_override:
            root = Path(base_override)
        else:
            # Normal pipeline mode: resolve project root
            root = Path(__file__).resolve().parents[2]

        # All attributes must be Path objects (required by Stage 2 regression tests)
        self.raw_dir = root / cfg["raw_dir"]
        self.metadata_dir = root / cfg["metadata_dir"]
        self.intermediate_dir = root / cfg["intermediate_dir"]
        self.logs_dir = root / cfg["logs_dir"]
        self.features_dir = root / cfg["features_dir"]
        self.model_artifact_dir = root / cfg["model_artifact_dir"]
        self.predictions_dir = root / cfg["predictions_dir"]
        self.config_dir = root / cfg["config_dir"]

        # Stage 3 chunk outputs + metadata
        self.chunk_output_dir = root / cfg["chunk_output_dir"]
        self.chunk_metadata_dir = root / cfg["chunk_metadata_dir"]

        # Stage 3 merge outputs
        self.stage3_merged = root / cfg["stage3_merged"]
        self.stage3_metadata = root / cfg["stage3_metadata"]
        self.stage3_qc = root / cfg["stage3_qc"]

    def __repr__(self):
        return (
            "Paths(\n"
            f"  raw_dir={self.raw_dir},\n"
            f"  metadata_dir={self.metadata_dir},\n"
            f"  intermediate_dir={self.intermediate_dir},\n"
            f"  logs_dir={self.logs_dir},\n"
            f"  features_dir={self.features_dir},\n"
            f"  model_artifact_dir={self.model_artifact_dir},\n"
            f"  predictions_dir={self.predictions_dir},\n"
            f"  config_dir={self.config_dir},\n"
            f"  chunk_output_dir={self.chunk_output_dir},\n"
            f"  chunk_metadata_dir={self.chunk_metadata_dir},\n"
            f"  stage3_merged={self.stage3_merged},\n"
            f"  stage3_metadata={self.stage3_metadata},\n"
            f"  stage3_qc={self.stage3_qc}\n"
            ")"
        )
