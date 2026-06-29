"""
Metadata writing utilities for the ERA5 pipeline.

Branch 1 uses a minimal metadata system: each run writes a JSON file
containing a timestamp and any user‑provided fields such as script name,
input paths, output paths, and configuration snapshots. This supports
basic reproducibility and traceability without introducing a full
metadata registry (planned for Branch 2).

Branch 2 will expand metadata to include:
- schema information
- variable‑level metadata
- ingestion metadata
- feature metadata
- model metadata
- evaluation metadata
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
        raise TypeError(
            f"Metadata contains non‑serializable values: {e}"
        )