"""
Stage 4 – Spatiotemporal Compiler (Package Initializer)
=======================================================

Consumes Stage 3 outputs and prepares the merged ERA5 dataset for
deterministic IR₄ compilation. Stage 4 attaches metadata and QC
artifacts as dataset attributes and provides a clean entry point for
compiler modules.

Inputs from Stage 3:
- merged.nc              (xarray.Dataset: time × lat × lon × variables)
- merged_metadata.json   (global metadata for the merged dataset)
- merged_qc.json         (QC summary for all variables)

Branch 2 Notes
--------------
Stage 4 is fully deterministic:
- no side effects beyond reading Stage 3 artifacts
- no directory creation
- no heavy imports beyond xarray/json
- safe to import during pytest collection
- attaches metadata/QC as attrs for IR₄ invariants and provenance

Branch 3 Notes
--------------
Future AI/LLM/RAG tooling may read Stage 4 outputs for:
- metadata search
- lineage exploration
- natural‑language summaries
- anomaly diagnostics

These intelligent components will live in separate modules and will not
modify deterministic Stage 4 behavior.

Invariant
---------
This package initializer must remain:
- minimal
- deterministic
- side‑effect‑free
- import‑safe
"""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict

import xarray as xr


def load_stage3_outputs(config: Mapping[str, Any]) -> xr.Dataset:
    """
    Load Stage 3 merged outputs (merged.nc) as an xarray.Dataset.

    Parameters
    ----------
    config : Mapping[str, Any]
        Must contain:
            config["paths"]["stage3_merged"]
            config["paths"]["stage3_metadata"]
            config["paths"]["stage3_qc"]

    Returns
    -------
    xr.Dataset
        The merged ERA5 dataset ready for Stage 4 compiler invariants.
    """

    merged_nc = Path(config["paths"]["stage3_merged"])
    if not merged_nc.exists():
        raise FileNotFoundError(f"[Stage 4] Stage 3 merged.nc not found: {merged_nc}")

    ds = xr.open_dataset(merged_nc)

    # Optional metadata and QC
    meta_path = Path(config["paths"]["stage3_metadata"])
    qc_path = Path(config["paths"]["stage3_qc"])

    metadata: dict[str, Any] = {}
    qc: dict[str, Any] = {}

    if meta_path.exists():
        with open(meta_path, "r") as f:
            metadata = json.load(f)

    if qc_path.exists():
        with open(qc_path, "r") as f:
            qc = json.load(f)

    # Attach metadata and QC to dataset attributes
    ds.attrs["stage3_metadata"] = metadata
    ds.attrs["stage3_qc"] = qc

    print("[Stage 4] Loaded Stage 3 dataset with metadata and QC.")

    return ds


__all__ = [
    "load_stage3_outputs",
]
