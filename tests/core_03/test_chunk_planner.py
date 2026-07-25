"""
Stage 3 – ChunkPlanner Tests (Branch‑2: Hourly Timeline, Single‑Variable)

This test suite is aligned with your ACTUAL Stage‑2 metadata.json format:

    {
        "2023-09-01T00:00:00::t2m": {
            "timestamp": "2023-09-01T00:00:00",
            "variable": "t2m",
            "path": "/path/to/parquet",
            "dtype": "float64",
            "shape": [153]
        },
        ...
    }

Stage‑3 ChunkPlanner contract:
    • planner.build(metadata, dtypes) → List[ChunkSpec]
    • ChunkSpec fields:
        - variable
        - timestamp
        - input_path
        - output_path
        - chunk_id

Branch‑2 behavior:
    • One chunk per time window
    • window_size_hours = 12
    • window_stride_hours = 12
    • 24 hourly timestamps → TWO windows → TWO chunks
    • No spatial tiling logic inside planner (tiles ignored)
"""

from pathlib import Path

import pandas as pd

from src.core_03.chunk_planner import ChunkPlanner
from src.core_03.chunk_spec import ChunkSpec

# ----------------------------------------------------------------------
# Synthetic Stage‑2 metadata generator (matches your real metadata.json)
# ----------------------------------------------------------------------


def build_stage2_metadata(tmp_path):
    """
    Build synthetic Stage‑2 metadata in the EXACT shape required by Stage‑3:

        metadata = {
            "timestamp::variable": {
                "timestamp": "...",
                "variable": "...",
                "path": "/path/to/parquet",
                "dtype": "...",
                "shape": [...]
            },
            ...
        }
    """

    timestamps = [f"2023-09-01T{str(h).zfill(2)}:00" for h in range(24)]

    metadata = {}

    for ts in timestamps:
        fname = f"in_{ts.replace(':', '').replace('-', '')}.parquet"
        fpath = tmp_path / fname

        df = pd.DataFrame(
            {
                "time": [ts],
                "t2m": [280.0],
                "wind_speed": [5.0],
            }
        )
        df.to_parquet(fpath)

        metadata[f"{ts}::t2m"] = {
            "timestamp": ts,
            "variable": "t2m",
            "path": str(fpath),
            "dtype": "float64",
            "shape": [1],
        }

        metadata[f"{ts}::wind_speed"] = {
            "timestamp": ts,
            "variable": "wind_speed",
            "path": str(fpath),
            "dtype": "float64",
            "shape": [1],
        }

    return metadata


# ----------------------------------------------------------------------
# Test 1 — Daily planner, no tiles
# ----------------------------------------------------------------------


def test_chunk_planner_daily_no_tiles(tmp_path):
    metadata = build_stage2_metadata(tmp_path)

    config = {
        "paths": {
            "input_dir": Path("/tmp"),
            "metadata_dir": Path("/tmp/meta"),
            "chunk_output_dir": Path("/tmp/out"),
            "chunk_metadata_dir": Path("/tmp/meta"),
        },
        "stage3": {
            "variables": ["t2m"],
            "chunk": {
                "window_size_hours": 12,
                "window_stride_hours": 12,
                "spatial_tiles": None,
            },
        },
    }

    dtypes = {"time": "string", "t2m": "float64"}

    planner = ChunkPlanner(config)
    specs = planner.build(metadata, dtypes)

    # EXPECT TWO CHUNKS: 00:00 and 12:00
    assert len(specs) == 2

    timestamps = {spec.timestamp for spec in specs}
    assert "2023-09-01T00:00" in timestamps
    assert "2023-09-01T12:00" in timestamps

    for spec in specs:
        assert isinstance(spec, ChunkSpec)
        assert spec.variable == "t2m"
        expected_chunk_id = f"{spec.variable}_{spec.timestamp}_12hr"
        assert spec.chunk_id == expected_chunk_id


# ----------------------------------------------------------------------
# Test 2 — Daily planner, with tiles
# ----------------------------------------------------------------------


def test_chunk_planner_with_tiles(tmp_path):
    metadata = build_stage2_metadata(tmp_path)

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
                "window_size_hours": 12,
                "window_stride_hours": 12,
                "spatial_tiles": ["tile_001", "tile_002"],  # ignored by planner
            },
        },
    }

    dtypes = {"time": "string", "wind_speed": "float64"}

    planner = ChunkPlanner(config)
    specs = planner.build(metadata, dtypes)

    # EXPECT TWO CHUNKS: 00:00 and 12:00
    assert len(specs) == 2

    timestamps = {spec.timestamp for spec in specs}
    assert "2023-09-01T00:00" in timestamps
    assert "2023-09-01T12:00" in timestamps

    for spec in specs:
        assert spec.variable == "wind_speed"
        expected_chunk_id = f"{spec.variable}_{spec.timestamp}_12hr"
        assert spec.chunk_id == expected_chunk_id
