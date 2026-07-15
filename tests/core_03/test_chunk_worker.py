"""
Tests for the Branch‑2 ChunkWorker used in Stage 3.

ChunkWorker API:
    - Loads a single parquet file (spec.input_path)
    - Applies deterministic transforms
    - Enforces schema (column order + dtypes)
    - Writes cleaned parquet (spec.output_path)
    - Writes metadata JSON to: metadata_dir / f"{chunk_id}.json"
    - Returns the same ChunkSpec on success
"""

import json
from pathlib import Path

import pandas as pd

from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec
from src.core_03.chunk_worker import ChunkWorker


def test_worker_full_pipeline(tmp_path):
    """
    Full end‑to‑end test of the Branch‑2 ChunkWorker.

    Steps:
        1. Create synthetic parquet input.
        2. Build ChunkSpec.
        3. Run worker.process(spec, metadata_dir).
        4. Validate:
            - output parquet exists
            - metadata JSON exists at metadata_dir / chunk_id.json
            - schema enforced
            - returned spec matches input spec
    """

    # --------------------------------------------------------------------------
    # 1. Create synthetic parquet input (must include full schema columns)
    # --------------------------------------------------------------------------
    input_path = tmp_path / "in.parquet"
    df = pd.DataFrame({
        "time": ["2023-09-01T11:00"],
        "lat": [34.0],
        "lon": [-118.0],
        "t2m": [280.0],
    })
    df.to_parquet(input_path)

    # --------------------------------------------------------------------------
    # 2. Build schema + ChunkSpec
    # --------------------------------------------------------------------------
    schema = ChunkSchema({
        "schema": {
            "columns": ["time", "lat", "lon", "t2m"],
            "dtypes": {
                "time": "string",
                "lat": "float64",
                "lon": "float64",
                "t2m": "float64",
            },
            "version": "1.0",
        }
    })

    chunk_id = "t2m_2023-09-01T11:00_12hr"

    spec = ChunkSpec(
        variable="t2m",
        timestamp="2023-09-01T11:00",
        input_path=input_path,
        output_path=tmp_path / "out.parquet",
        chunk_id=chunk_id,
    )

    # --------------------------------------------------------------------------
    # 3. Run worker (Branch‑2 API: no schema passed to constructor)
    # --------------------------------------------------------------------------
    worker = ChunkWorker()  # ← FIXED: no schema argument
    result_spec = worker.process(spec, metadata_dir=tmp_path)

    # --------------------------------------------------------------------------
    # 4. Validate outputs
    # --------------------------------------------------------------------------

    # Returned spec should match input spec
    assert isinstance(result_spec, ChunkSpec)
    assert result_spec.variable == "t2m"
    assert result_spec.timestamp == "2023-09-01T11:00"
    assert result_spec.chunk_id == chunk_id

    # Output parquet must exist
    assert result_spec.output_path.exists()

    # Metadata JSON must exist at metadata_dir / chunk_id.json
    meta_path = tmp_path / f"{chunk_id}.json"
    assert meta_path.exists()

    # Metadata JSON must contain correct fields
    with open(meta_path, "r") as f:
        meta = json.load(f)

    assert meta["variable"] == "t2m"
    assert meta["timestamp"] == "2023-09-01T11:00"
    assert meta["chunk_id"] == chunk_id

    # Output parquet must contain correct columns
    out_df = pd.read_parquet(result_spec.output_path)
    assert list(out_df.columns) == ["time", "lat", "lon", "t2m"]

    # Schema dtypes must be enforced
    assert out_df["t2m"].dtype == "float64"
