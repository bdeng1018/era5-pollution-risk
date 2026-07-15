"""
Tests for the Branch‑2 ChunkSpec class used in Stage 3.

Your current ChunkSpec API (as implemented in src/core_03/chunk_spec.py)
has the following fields:

    - variable: str
    - timestamp: str (representative timestamp for the chunk)
    - input_path: Path
    - output_path: Path
    - chunk_id: str

There is intentionally **no** time_window and **no** spatial_tile.
This test suite reflects the correct, modern API.
"""

from pathlib import Path

from src.core_03.chunk_spec import ChunkSpec


def test_chunk_spec_construction():
    """
    Basic construction test for the simplified Branch‑2 ChunkSpec.

    Ensures:
    - fields are stored correctly
    - paths resolve correctly
    - chunk_id is preserved
    """

    spec = ChunkSpec(
        variable="2m_temperature",
        timestamp="2023-09-01T00:00",
        input_path=Path("/tmp/in.parquet"),
        output_path=Path("/tmp/out.parquet"),
        chunk_id="chunk_20230901T0000",
    )

    assert spec.variable == "2m_temperature"
    assert spec.timestamp == "2023-09-01T00:00"
    assert spec.input_path.name == "in.parquet"
    assert spec.output_path.name == "out.parquet"
    assert spec.chunk_id == "chunk_20230901T0000"


def test_chunk_spec_description():
    """
    The describe() method should return a human‑readable summary
    containing the variable name and chunk_id.
    """

    spec = ChunkSpec(
        variable="wind_speed",
        timestamp="2023-09-01T12:00",
        input_path=Path("/tmp/in.parquet"),
        output_path=Path("/tmp/out.parquet"),
        chunk_id="chunk_20230901T1200",
    )

    desc = spec.describe()

    assert "wind_speed" in desc
    assert "chunk_20230901T1200" in desc
