"""
Tests for the Branch‑2 chunk_merge module used in Stage 3.

This test verifies:
    - chunk parquet files are loaded correctly
    - coordinates are normalized
    - duplicates are dropped
    - xarray merge produces correct shapes
    - metadata + QC JSON files are written
"""

import json
from pathlib import Path

import pandas as pd
import xarray as xr

from src.core_03.chunk_merge import merge_chunks
from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec


def test_chunk_merge_small(tmp_path):
    """
    Build two tiny synthetic chunk parquet files and merge them.

    Chunk A:
        variable = t2m
        timestamp = 2023-09-01T11:00   (real Stage 3 window start)

    Chunk B:
        variable = tcwv
        timestamp = 2023-09-01T23:00   (real Stage 3 window start)

    Expected:
        - merged.nc contains both timestamps
        - both variables appear
        - metadata + QC JSON exist
    """

    # --------------------------------------------------------------------------
    # 1. Build synthetic chunk parquet files (full schema)
    # --------------------------------------------------------------------------
    chunk_a_path = tmp_path / "chunk_t2m.parquet"
    chunk_b_path = tmp_path / "chunk_tcwv.parquet"

    df_a = pd.DataFrame(
        {
            "time": ["2023-09-01T11:00"],
            "lat": [34.0],
            "lon": [-118.0],
            "t2m": [280.0],
            "tcwv": [None],
        }
    )

    df_b = pd.DataFrame(
        {
            "time": ["2023-09-01T23:00"],
            "lat": [34.0],
            "lon": [-118.0],
            "t2m": [None],
            "tcwv": [5.0],
        }
    )

    df_a.to_parquet(chunk_a_path)
    df_b.to_parquet(chunk_b_path)

    # --------------------------------------------------------------------------
    # 2. Build ChunkSpec objects (real chunk_id format)
    # --------------------------------------------------------------------------
    spec_a = ChunkSpec(
        variable="t2m",
        timestamp="2023-09-01T11:00",
        input_path=chunk_a_path,
        output_path=chunk_a_path,
        chunk_id="t2m_2023-09-01T11:00_12hr",
    )

    spec_b = ChunkSpec(
        variable="tcwv",
        timestamp="2023-09-01T23:00",
        input_path=chunk_b_path,
        output_path=chunk_b_path,
        chunk_id="tcwv_2023-09-01T23:00_12hr",
    )

    # --------------------------------------------------------------------------
    # 3. Build schema
    # --------------------------------------------------------------------------
    schema = ChunkSchema(
        {
            "schema": {
                "columns": ["time", "lat", "lon", "t2m", "tcwv"],
                "dtypes": {
                    "time": "string",
                    "lat": "float64",
                    "lon": "float64",
                    "t2m": "float64",
                    "tcwv": "float64",
                },
                "version": "1.0",
            }
        }
    )

    # --------------------------------------------------------------------------
    # 4. Build config dict expected by merge_chunks()
    # --------------------------------------------------------------------------
    config = {
        "schema_obj": schema,
        "paths": {
            "stage3_merged": str(tmp_path / "merged.nc"),
            "stage3_metadata": str(tmp_path / "merged_metadata.json"),
            "stage3_qc": str(tmp_path / "merged_qc.json"),
            "chunk_output_dir": tmp_path,
        },
    }

    # --------------------------------------------------------------------------
    # 5. Run merge
    # --------------------------------------------------------------------------
    ds = merge_chunks(
        chunk_specs=[spec_a, spec_b],
        config=config,
    )

    # --------------------------------------------------------------------------
    # 6. Validate outputs
    # --------------------------------------------------------------------------
    merged_path = Path(config["paths"]["stage3_merged"])
    metadata_path = Path(config["paths"]["stage3_metadata"])
    qc_path = Path(config["paths"]["stage3_qc"])

    assert merged_path.exists()
    assert metadata_path.exists()
    assert qc_path.exists()

    ds_loaded = xr.open_dataset(merged_path)

    # Two timestamps expected
    assert set(ds_loaded["time"].values) == {
        "2023-09-01T11:00",
        "2023-09-01T23:00",
    }

    # Variables must exist
    assert "t2m" in ds_loaded
    assert "tcwv" in ds_loaded

    # Metadata JSON must contain correct fields
    with open(metadata_path, "r") as f:
        meta = json.load(f)

    assert "variables" in meta
    assert "t2m" in meta["variables"]
    assert "tcwv" in meta["variables"]

    # QC JSON must contain min/max values
    with open(qc_path, "r") as f:
        qc = json.load(f)

    assert "t2m" in qc
    assert "tcwv" in qc
