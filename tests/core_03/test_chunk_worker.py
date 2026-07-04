from pathlib import Path

import pandas as pd

from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec
from src.core_03.chunk_worker import ChunkWorker


def test_worker_full_pipeline(tmp_path):
    schema = ChunkSchema({
        "schema": {
            "columns": ["time", "t2m"],
            "dtypes": {"time": "string", "t2m": "float64"},
            "version": "1.0",
        }
    })

    worker = ChunkWorker(schema)

    # Fake Parquet input file
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

    worker.process(spec)

    out_df = pd.read_parquet(spec.output_path)
    assert list(out_df.columns) == ["time", "t2m"]
    assert out_df["t2m"].dtype == "float64"
