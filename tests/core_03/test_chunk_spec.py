from pathlib import Path

from src.core_03.chunk_spec import ChunkSpec


def test_chunk_spec_construction():
    spec = ChunkSpec(
        variable="2m_temperature",
        time_window=("2023-09-01", "2023-09-01"),
        spatial_tile=None,
        input_path=Path("/tmp/in.nc"),
        output_path=Path("/tmp/out.parquet"),
        metadata_path=Path("/tmp/meta.json"),
    )

    assert spec.variable == "2m_temperature"
    assert spec.time_window == ("2023-09-01", "2023-09-01")
    assert spec.spatial_tile is None
    assert spec.input_path.name == "in.nc"
    assert spec.output_path.name == "out.parquet"
    assert spec.metadata_path.name == "meta.json"


def test_chunk_spec_description():
    spec = ChunkSpec(
        variable="wind_speed",
        time_window=("2023-09-01", "2023-09-02"),
        spatial_tile="tile_001",
        input_path=Path("/tmp/in.nc"),
        output_path=Path("/tmp/out.parquet"),
        metadata_path=Path("/tmp/meta.json"),
    )

    desc = spec.describe()
    assert "wind_speed" in desc
    assert "tile_001" in desc
