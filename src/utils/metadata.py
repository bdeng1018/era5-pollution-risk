"""
Metadata writing utilities for the ERA5 pipeline (Branch 2)

This module provides a minimal JSON-based metadata writer used for
deterministic pipeline runs. It supports basic reproducibility by
recording timestamps and user-provided fields such as script name,
input paths, output paths, and configuration snapshots.

Branch 2 Note
-------------
Branch 2 expands metadata beyond the Branch 1 MVP to include:
- ingestion metadata
- GRIB metadata parquet
- chunk metadata
- IR₄ compiler metadata
- feature metadata (IR₅, in progress)
- model/evaluation metadata (planned)

This module intentionally remains lightweight and side-effect-free.
Heavier metadata structures are produced inside stage-specific modules.

Branch 3 Note
-------------
Branch 3 will introduce optional AI/LLM/RAG tooling for:
- metadata search and retrieval
- lineage exploration
- auto-generated summaries and reports

These intelligent components will live in separate modules and will not
change the deterministic behavior of this JSON writer.

Invariant
---------
This module must remain simple, JSON-only, and safe to import during
pytest collection and `python -m` execution.
"""

import json
from datetime import datetime
from pathlib import Path


def write_metadata(output_path: str | Path, info: dict) -> None:
    """
    Write a metadata JSON file for a pipeline run.

    Automatically adds:
    - timestamp (UTC ISO‑8601)

    Parameters
    ----------
    output_path : str | Path
        Destination path for the metadata JSON file.
    info : dict
        Dictionary containing metadata fields. Must be JSON‑serializable.

    Raises
    ------
    TypeError
        If `info` contains non‑serializable values.
    """
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # Add timestamp
    info["timestamp"] = datetime.utcnow().isoformat()

    try:
        with open(p, "w") as f:
            json.dump(info, f, indent=2)
    except TypeError as e:
        raise TypeError(f"Metadata contains non‑serializable values: {e}")
