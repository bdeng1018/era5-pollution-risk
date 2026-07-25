"""
Tests for the Branch‑2 ChunkOrchestrator used in Stage 3.

ChunkOrchestrator API:
    - schema: ChunkSchema
    - metadata_dir: Path
    - max_workers: int
    - max_retries: int

ChunkSpec API:
    - variable: str
    - timestamp: str
    - input_path: Path
    - output_path: Path
    - chunk_id: str

Worker writes metadata to:
    metadata_dir / f"{chunk_id}.json"
"""

import pandas as pd

from src.core_03.chunk_orchestrator import ChunkOrchestrator
from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec


def test_orchestrator_smoke(tmp_path):
    """
    Basic smoke test:
        - Create a valid parquet input file
        - Build a ChunkSpec
        - Run orchestrator
        - Expect one successful result
        - Metadata JSON must be written to metadata_dir
    """

    # Schema is NOT used by orchestrator, but test keeps it for completeness
    schema = ChunkSchema(
        {
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
        }
    )

    # Create input parquet
    input_path = tmp_path / "in.parquet"
    df = pd.DataFrame(
        {
            "time": ["2023-09-01T00:00"],
            "lat": [34.0],
            "lon": [-118.0],
            "t2m": [280.0],
        }
    )
    df.to_parquet(input_path)

    chunk_id = "t2m_2023-09-01T00:00_24hr"

    spec = ChunkSpec(
        variable="t2m",
        timestamp="2023-09-01T00:00",
        input_path=input_path,
        output_path=tmp_path / "out.parquet",
        chunk_id=chunk_id,
    )

    orchestrator = ChunkOrchestrator(
        metadata_dir=tmp_path,
        max_workers=1,
        max_retries=1,
    )

    results = orchestrator.run([spec])

    assert len(results) == 1
    assert results[0].output_path.exists()

    # Worker writes metadata JSON
    meta_path = tmp_path / f"{chunk_id}.json"
    assert meta_path.exists()


def test_orchestrator_retry_logic(tmp_path):
    """
    Retry logic test:
        - Provide a ChunkSpec with a missing input file
        - Worker should fail
        - Orchestrator should retry up to max_retries
        - No successful results should be returned
    """

    chunk_id = "t2m_2023-09-01T00:00_24hr"

    spec = ChunkSpec(
        variable="t2m",
        timestamp="2023-09-01T00:00",
        input_path=tmp_path / "missing.parquet",
        output_path=tmp_path / "out.parquet",
        chunk_id=chunk_id,
    )

    orchestrator = ChunkOrchestrator(
        metadata_dir=tmp_path,
        max_workers=1,
        max_retries=3,
    )

    results = orchestrator.run([spec])

    assert len(results) == 0
