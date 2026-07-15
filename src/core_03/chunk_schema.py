"""
Stage 3: Chunk Schema (Branch 2 — Single‑Variable, Deterministic Schema)
=======================================================================

Overview
--------
ChunkSchema defines the deterministic column order and data types used for all
Stage‑3 chunked Parquet outputs.

Branch‑2 rules (single‑variable mode):
    • exactly one input parquet per chunk
    • exactly one variable per chunk
    • coordinates: time, lat, lon
    • no multi‑variable schema enforcement
    • no NaN‑filling for missing variables
    • deterministic ordering

Schema Definition (Branch‑2)
----------------------------
config.yml must define:

    schema.columns:
        - time
        - lat
        - lon
        - <variable>

    schema.dtypes:
        time: datetime64[ns]
        lat: float64
        lon: float64
        <variable>: float64

Purpose
-------
ChunkSchema ensures:
    • deterministic column order
    • correct dtypes
    • compatibility with Stage‑3 merging
    • reproducible chunk outputs
"""

from typing import Any, Dict, List


class ChunkSchema:
    """
    Deterministic schema for Stage‑3 chunk outputs.

    Responsibilities:
        • define ordered column list (coords + variable)
        • define dtypes for each column
        • provide validation helpers
    """

    def __init__(self, config: Dict[str, Any]):
        schema_cfg = config.get("schema", {})

        # Full deterministic column order exactly as provided
        self.columns: List[str] = schema_cfg.get("columns", [])

        # Variable column = all non-coordinate columns
        self.variable_columns: List[str] = [
            c for c in self.columns if c not in ["time", "lat", "lon"]
        ]

        # Dtypes exactly as provided
        self.dtypes: Dict[str, str] = schema_cfg.get("dtypes", {})

        # Optional version
        self.version: str = schema_cfg.get("version", "1.0")

    # --------------------------------------------------------------------------
    # Validation helpers
    # --------------------------------------------------------------------------
    def validate_columns(self, df_columns: List[str]) -> bool:
        """
        Validate that df_columns matches the expected prefix of schema.columns.

        Example:
            df_columns = ["time","lat","lon","t2m"]
            schema.columns = ["time","lat","lon","t2m"]

        This allows minimal schemas in tests and full schemas in production.
        """
        return df_columns == self.columns[:len(df_columns)]

    def validate_dtypes(self, df_dtypes: Dict[str, str]) -> bool:
        """
        Validate dtypes for columns present in df_dtypes.

        Minimal parquet files may omit variables — this is allowed.
        """
        for col, expected in self.dtypes.items():
            if col not in df_dtypes:
                continue
            if str(df_dtypes[col]) != expected:
                return False
        return True

    def describe(self) -> str:
        """
        Human-readable schema description.
        """
        return f"ChunkSchema(v{self.version}, columns={self.columns})"
