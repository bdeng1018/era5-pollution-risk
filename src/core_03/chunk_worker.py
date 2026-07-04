"""
Stage 3: Chunk Worker

Processes a single ChunkSpec:
- loads Stage 2 preprocessed data (Parquet)
- applies deterministic transforms
- enforces schema
- writes chunked Parquet
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec

DTYPE_MAP = {
    "string": pd.StringDtype(),
    "float64": np.float64,
    "int64": np.int64,
}

class ChunkWorker:
    def __init__(self, schema: ChunkSchema):
        self.schema = schema

    # --------------------------------------------------------------------------
    # Load Parquet (Stage 2 output)
    # --------------------------------------------------------------------------
    def load(self, input_path: Path) -> pd.DataFrame:
        """Load Stage 2 hourly Parquet file."""
        return pd.read_parquet(input_path)

    # --------------------------------------------------------------------------
    # Deterministic transforms
    # --------------------------------------------------------------------------
    def normalize_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """Example deterministic transform: convert units if needed."""
        if "t2m" in df.columns:
            df["t2m"] = df["t2m"] - 273.15
        return df

    def clean_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values deterministically."""
        return df.fillna(df.mean(numeric_only=True))

    # --------------------------------------------------------------------------
    # Schema enforcement
    # --------------------------------------------------------------------------
    def enforce_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[self.schema.columns]

        for col, dtype in self.schema.dtypes.items():
            df[col] = df[col].astype(DTYPE_MAP[dtype])

        return df

    # --------------------------------------------------------------------------
    # Write chunk
    # --------------------------------------------------------------------------
    def write(self, df: pd.DataFrame, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)

    # --------------------------------------------------------------------------
    # Full pipeline
    # --------------------------------------------------------------------------
    def process(self, spec: ChunkSpec):
        df = self.load(spec.input_path)
        df = self.normalize_units(df)
        df = self.clean_missing(df)
        df = self.enforce_schema(df)
        self.write(df, spec.output_path)
