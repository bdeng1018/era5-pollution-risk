"""
Stage 4 – Spatiotemporal Compiler (Package Initializer)
=======================================================

This package consumes Stage 3 outputs:

- merged.nc              (xarray.Dataset: time × lat × lon × variables)
- merged_metadata.json   (global metadata for the merged dataset)
- merged_qc.json         (QC summary for all variables)

High-level responsibilities:
- Load Stage 3 merged.nc
- Attach Stage 3 metadata and QC as dataset attributes
- Provide a clean entry point for Stage 4 compiler modules
"""

import json
from pathlib import Path
from typing import Any, Dict, Mapping

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

    metadata: Dict[str, Any] = {}
    qc: Dict[str, Any] = {}

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
