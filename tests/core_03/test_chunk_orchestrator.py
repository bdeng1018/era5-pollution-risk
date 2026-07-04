import logging
from pathlib import Path

import pandas as pd

from src.core_03.chunk_orchestrator import ChunkOrchestrator
from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec


def test_orchestrator_smoke(tmp_path):
    schema = ChunkSchema({
        "schema": {
            "columns": ["time", "t2m"],
            "dtypes": {"time": "string", "t2m": "float64"},
            "version": "1.0",
        }
    })

    orchestrator = ChunkOrchestrator(schema, max_workers=1)

    input_path = tmp_path / "in.parquet"
    df = pd.DataFrame({"time": ["2023-09-01T00:00"], "t2m": [280.0]})
    df.to_parquet(input_path)

    spec = ChunkSpec(
        variable="t2m",
        time_window=("2023-09-01T00:00", "2023-09-01T00:00"),
        spatial_tile=None,
        input_path=input_path,
        output_path=tmp_path / "out.parquet",
        metadata_path=tmp_path / "meta.json",
    )

    results = orchestrator.run([spec])
    assert len(results) == 1
    assert results[0].variable == "t2m"


def test_orchestrator_retry_logic(tmp_path):
    schema = ChunkSchema({
        "schema": {
            "columns": ["time", "t2m"],
            "dtypes": {"time": "string", "t2m": "float64"},
            "version": "1.0",
        }
    })

    orchestrator = ChunkOrchestrator(schema, max_workers=1, max_retries=1)

    spec = ChunkSpec(
        variable="t2m",
        time_window=("2023-09-01T00:00", "2023-09-01T00:00"),
        spatial_tile=None,
        input_path=tmp_path / "missing.parquet",
        output_path=tmp_path / "out.parquet",
        metadata_path=tmp_path / "meta.json",
    )

    results = orchestrator.run([spec])
    assert len(results) == 0
