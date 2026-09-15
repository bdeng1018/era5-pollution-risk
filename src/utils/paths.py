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


# ==============================================================================
# Branch 2‑compatible helper for Stage 05–08
# ==============================================================================


def get_path(cfg: dict, dotted_key: str) -> str:
    """
    Lightweight deterministic path resolver for Stage 05–08.

    This helper reads nested config keys using dotted notation and resolves
    the resulting relative path against the project root. It does NOT modify
    or interfere with the Branch 2 Paths class.

    Example
    -------
        cfg:
            paths:
                input: "data/spatiotemporal/stage4_tensor.nc"

        get_path(cfg, "paths.input")
        → "/Users/.../era5-pollution-risk/data/spatiotemporal/stage4_tensor.nc"

    Architecture Notes
    ------------------
    - Deterministic: always resolves relative to project root.
    - Side‑effect‑free: no directory creation.
    - Import‑safe: no heavy dependencies.
    - Branch‑2‑compatible: does not alter Paths() behavior.
    - Designed for Stage 05–08, which are config‑driven.

    Parameters
    ----------
    cfg : dict
        Loaded YAML configuration dictionary.
    dotted_key : str
        Dotted key path (e.g., "paths.output").

    Returns
    -------
    str
        Absolute path resolved against project root.
    """
    parts = dotted_key.split(".")
    node = cfg
    for p in parts:
        node = node.get(p, {})

    if not isinstance(node, str):
        raise ValueError(f"Config key '{dotted_key}' did not resolve to a string path.")

    project_root = Path(__file__).resolve().parents[2]
    return str(project_root / node)
