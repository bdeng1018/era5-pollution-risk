"""
Stage 3: Chunk Worker (Branch 2 — Single‑Variable, Merge‑Compatible Schema)
===========================================================================

This worker processes ONE Stage‑2 parquet file and produces ONE chunk parquet
file containing the exact Stage‑3 schema required for merging:

    time, lat, lon, <variable>

Key rules:
    • one input parquet per chunk
    • one variable per chunk
    • coordinates: time, lat, lon
    • no GRIB metadata columns (number, step, surface)
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.core_03.chunk_spec import ChunkSpec

DTYPE_MAP = {
    "string": pd.StringDtype(),
    "float64": np.float64,
    "int64": np.int64,
    "datetime64[ns]": "datetime64[ns]",
}


class ChunkWorker:
    def __init__(self):
        pass

    # --------------------------------------------------------------------------
    # Load Stage‑2 parquet
    # --------------------------------------------------------------------------
    def load(self, input_path: Path) -> pd.DataFrame:
        df = pd.read_parquet(input_path)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    # --------------------------------------------------------------------------
    # Deterministic transforms
    # --------------------------------------------------------------------------
    def normalize_units(self, df: pd.DataFrame) -> pd.DataFrame:
        # Convert t2m from Kelvin to Celsius if present
        if "t2m" in df.columns:
            df["t2m"] = df["t2m"] - 273.15
        return df

    def clean_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        # Simple numeric mean imputation
        return df.fillna(df.mean(numeric_only=True))

    def normalize_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Stage‑2 parquet contains:
            lat, lon, number, step, surface, time, <variable>

        Stage‑3 requires:
            time, lat, lon, <variable>
        """

        # Rename coordinates if needed
        rename_map = {}
        if "latitude" in df.columns:
            rename_map["latitude"] = "lat"
        if "longitude" in df.columns:
            rename_map["longitude"] = "lon"
        if "valid_time" in df.columns:
            # If both exist, drop the old 'time'
            if "time" in df.columns:
                df = df.drop(columns=["time"])
            rename_map["valid_time"] = "time"

        df = df.rename(columns=rename_map)

        # Ensure required coordinate columns exist
        for col in ["time", "lat", "lon"]:
            if col not in df.columns:
                df[col] = pd.NA

        # Drop GRIB metadata columns
        drop_cols = [c for c in ["number", "step", "surface"] if c in df.columns]
        if drop_cols:
            df = df.drop(columns=drop_cols)

        # Ensure time is datetime64
        try:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
        except Exception:
            df["time"] = pd.NaT

        return df

    # --------------------------------------------------------------------------
    # Schema enforcement (single‑variable)
    # --------------------------------------------------------------------------
    def enforce_schema(self, df: pd.DataFrame, variable: str) -> pd.DataFrame:
        # Keep only coordinates + target variable
        cols = ["time", "lat", "lon"]
        if variable not in df.columns:
            df[variable] = np.nan
        cols.append(variable)
        df = df[cols].copy()

        # Cast dtypes
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["lat"] = df["lat"].astype(float)
        df["lon"] = df["lon"].astype(float)
        df[variable] = df[variable].astype(float)

        return df

    # --------------------------------------------------------------------------
    # Write chunk parquet
    # --------------------------------------------------------------------------
    def write_chunk(self, df: pd.DataFrame, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)

    # --------------------------------------------------------------------------
    # Write metadata JSON
    # --------------------------------------------------------------------------
    def write_metadata(self, df: pd.DataFrame, spec: ChunkSpec, metadata_dir: Path):
        metadata = {
            "chunk_id": spec.chunk_id,
            "variable": spec.variable,
            "timestamp": spec.timestamp,
            "input_path": str(spec.input_path),
            "output_path": str(spec.output_path),
            "n_rows": len(df),
            "columns": list(df.columns),
            "time_start": str(df["time"].min()) if "time" in df.columns else None,
            "time_end": str(df["time"].max()) if "time" in df.columns else None,
        }

        metadata_dir.mkdir(parents=True, exist_ok=True)
        meta_path = metadata_dir / f"{spec.chunk_id}.json"

        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

    # --------------------------------------------------------------------------
    # Main entry point
    # --------------------------------------------------------------------------
    def process(self, spec: ChunkSpec, metadata_dir: Path) -> ChunkSpec:
        df = self.load(spec.input_path)
        df = self.normalize_units(df)
        df = self.clean_missing(df)
        df = self.normalize_coordinates(df)
        df = self.enforce_schema(df, variable=spec.variable)

        self.write_chunk(df, spec.output_path)
        self.write_metadata(df, spec, metadata_dir)

        return spec
