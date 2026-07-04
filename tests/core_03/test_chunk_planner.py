from pathlib import Path

import pandas as pd

from src.core_03.chunk_planner import ChunkPlanner
from src.core_03.chunk_spec import ChunkSpec


def build_hourly_metadata(tmp_path):
    timestamps = [
        f"2023-09-01T{str(h).zfill(2)}:00"
        for h in range(24)
    ]

    variable_paths = {}
    for ts in timestamps:
        fname = f"in_{ts.replace(':','').replace('-','')}.parquet"
        fpath = tmp_path / fname
        df = pd.DataFrame({"time": [ts], "t2m": [280.0], "wind_speed": [5.0]})
        df.to_parquet(fpath)
        variable_paths[ts] = str(fpath)

    return {
        "timestamps": timestamps,
        "variables": {
            "2m_temperature": variable_paths,
            "wind_speed": variable_paths,
        },
    }


def test_chunk_planner_daily_no_tiles(tmp_path):
    metadata = build_hourly_metadata(tmp_path)

    config = {
        "paths": {
            "input_dir": Path("/tmp"),
            "metadata_dir": Path("/tmp/meta"),
            "chunk_output_dir": Path("/tmp/out"),
            "chunk_metadata_dir": Path("/tmp/meta"),
        },
        "stage3": {
            "variables": ["2m_temperature"],
            "chunk": {
                "size": {"time": 24},
                "stride": {"time": 24},
                "chunk_frequency_hours": 24,
                "spatial_tiles": None,
                "paths": {
                    "input_dir": Path("/tmp"),
                    "chunk_output_dir": Path("/tmp/out"),
                    "chunk_metadata_dir": Path("/tmp/meta"),
                },
            },
        },
    }

    dtypes = {"time": "string", "2m_temperature": "float64"}

    planner = ChunkPlanner(config)
    specs = planner.build(metadata, dtypes)

    assert len(specs) == 1
    assert isinstance(specs[0], ChunkSpec)
    assert specs[0].variable == "2m_temperature"
    assert specs[0].time_window == ("2023-09-01T00:00", "2023-09-01T23:00")
    assert specs[0].spatial_tile is None


def test_chunk_planner_with_tiles(tmp_path):
    metadata = build_hourly_metadata(tmp_path)

    config = {
        "paths": {
            "input_dir": Path("/tmp"),
            "metadata_dir": Path("/tmp/meta"),
            "chunk_output_dir": Path("/tmp/out"),
            "chunk_metadata_dir": Path("/tmp/meta"),
        },
        "stage3": {
            "variables": ["wind_speed"],
            "chunk": {
                "size": {"time": 24},
                "stride": {"time": 24},
                "chunk_frequency_hours": 24,
                "spatial_tiles": ["tile_001", "tile_002"],
                "paths": {
                    "input_dir": Path("/tmp"),
                    "chunk_output_dir": Path("/tmp/out"),
                    "chunk_metadata_dir": Path("/tmp/meta"),
                },
            },
        },
    }

    dtypes = {"time": "string", "wind_speed": "float64"}

    planner = ChunkPlanner(config)
    specs = planner.build(metadata, dtypes)

    # The planner does NOT apply tiles — only one chunk is produced
    assert len(specs) == 1
    assert specs[0].spatial_tile is None
