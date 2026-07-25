"""
Stage 3 Diagnostic — Chunk Integrity & Coordinate Schema Validator
==================================================================

Purpose
-------
Validate Stage 3 chunk parquet files and cross-check them against the
Stage 2 metadata.json (key-indexed schema):

    "<timestamp>::<variable>": {
        "timestamp": "...",
        "variable": "...",
        "path": "...",
        "year": ...,
        "month": ...,
        "dtype": "...",
        "shape": [...]
    }

Checks performed:
    1. Chunk directory scan
    2. Chunk parquet readability
    3. Empty-file detection
    4. Coordinate presence (time, lat, lon)
    5. Chunk filename → (variable, timestamp) extraction
    6. Stage 2 metadata key lookup
    7. Stage 2 parquet existence/readability
    8. Stage 2 coordinate schema validation

Usage:
    python scripts/diagnostics/stage3/check_chunk_integrity.py
"""

import json
from pathlib import Path

import pandas as pd
import yaml

REQUIRED_COORDS = {"time", "lat", "lon"}


# ------------------------------------------------------------------------------
# Loaders
# ------------------------------------------------------------------------------


def load_config():
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    cfg_path = PROJECT_ROOT / "configs/config.yml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"config.yml not found at {cfg_path}")
    with open(cfg_path) as f:
        return yaml.safe_load(f)


def load_metadata():
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    meta_path = PROJECT_ROOT / "data/metadata/metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError("metadata.json not found.")
    with open(meta_path) as f:
        return json.load(f)


# ------------------------------------------------------------------------------
# Chunk Validation
# ------------------------------------------------------------------------------


def validate_chunk_file(chunk_path: Path):
    """Validate a single Stage 3 chunk parquet file."""
    try:
        df = pd.read_parquet(chunk_path)
    except Exception as e:
        return {
            "file": chunk_path,
            "status": "error",
            "error": str(e),
            "columns": None,
        }

    cols = set(df.columns)

    if df.empty:
        return {
            "file": chunk_path,
            "status": "empty",
            "columns": list(cols),
        }

    missing = REQUIRED_COORDS - cols
    if missing:
        return {
            "file": chunk_path,
            "status": "missing_coords",
            "missing": list(missing),
            "columns": list(cols),
        }

    return {
        "file": chunk_path,
        "status": "healthy",
        "columns": list(cols),
    }


# ------------------------------------------------------------------------------
# Stage 2 Cross‑Check (Key‑Indexed Schema)
# ------------------------------------------------------------------------------


def parse_chunk_name(chunk_name: str):
    """
    Chunk filename format:
        <variable>_<timestamp>_<window>.parquet

    Example:
        tcwv_2024-12-31T06-00_12hr.parquet

    Extract:
        variable = tcwv
        timestamp = 2024-12-31T06:00
    """
    try:
        variable, ts_part, _ = chunk_name.split("_", 2)
        ts = ts_part.replace("-", ":")
        return variable, ts
    except Exception:
        return None, None


def crosscheck_stage2(chunk_name: str, metadata: dict):
    """Cross-check chunk against Stage 2 metadata.json (key-indexed)."""
    variable, ts = parse_chunk_name(chunk_name)

    if variable is None:
        return {"stage2_status": "unparseable_chunk_name"}

    key = f"{ts}::{variable}"

    if key not in metadata:
        return {"stage2_status": "metadata_key_missing", "metadata_key": key}

    entry = metadata[key]
    stage2_path = Path(entry["path"])

    if not stage2_path.exists():
        return {
            "stage2_status": "missing_stage2_file",
            "stage2_path": str(stage2_path),
        }

    try:
        df2 = pd.read_parquet(stage2_path)
    except Exception as e:
        return {
            "stage2_status": "stage2_load_error",
            "stage2_path": str(stage2_path),
            "error": str(e),
        }

    cols2 = set(df2.columns)

    if df2.empty:
        return {
            "stage2_status": "stage2_empty",
            "stage2_path": str(stage2_path),
            "columns": list(cols2),
        }

    missing2 = REQUIRED_COORDS - cols2
    if missing2:
        return {
            "stage2_status": "stage2_missing_coords",
            "stage2_path": str(stage2_path),
            "missing": list(missing2),
            "columns": list(cols2),
        }

    return {
        "stage2_status": "stage2_healthy",
        "stage2_path": str(stage2_path),
        "columns": list(cols2),
    }


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


def main():
    print(
        "\n=== Stage 3 Chunk Integrity Diagnostic (Key‑Indexed Metadata Schema) ===\n"
    )

    cfg = load_config()
    metadata = load_metadata()

    chunk_dir = Path(cfg["paths"]["chunk_output_dir"])
    print(f"Chunk directory: {chunk_dir.resolve()}")

    if not chunk_dir.exists():
        print("❌ Chunk directory does not exist.")
        return

    chunk_files = list(chunk_dir.glob("*.parquet"))
    print(f"Found {len(chunk_files)} chunk files.\n")

    if not chunk_files:
        print("⚠️ No chunk files found. Nothing to validate.")
        return

    for f in chunk_files:
        print(f"\n--- Checking {f.name} ---")

        result = validate_chunk_file(f)
        print("Chunk status:", result["status"])
        print("Columns:", result["columns"])

        stage2_info = crosscheck_stage2(f.name, metadata)
        print("Stage 2:", stage2_info["stage2_status"])

        if "metadata_key" in stage2_info:
            print("Missing metadata key:", stage2_info["metadata_key"])

        if "stage2_path" in stage2_info:
            print("Stage 2 path:", stage2_info["stage2_path"])

        if "missing" in stage2_info:
            print("Missing Stage 2 coords:", stage2_info["missing"])

        if result["status"] != "healthy":
            print("❌ PROBLEM DETECTED in chunk:", f.name)

    print("\n=== Diagnostic Complete ===\n")


if __name__ == "__main__":
    main()
