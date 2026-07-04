"""
Stage 3: Chunk Schema

Defines deterministic column order and dtypes for chunked Parquet outputs.
Used by ChunkWorker and validated in tests.
"""

from typing import Any, Dict, List


class ChunkSchema:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize schema from config.

        Expected config structure (example):
        config["schema"]["columns"] -> List[str]
        config["schema"]["dtypes"]  -> Dict[str, str]
        config["schema"]["version"] -> str (optional)
        """
        schema_cfg = config.get("schema", {})

        self.columns: List[str] = schema_cfg.get("columns", [])
        self.dtypes: Dict[str, str] = schema_cfg.get("dtypes", {})
        self.version: str = schema_cfg.get("version", "1.0")

    def validate_columns(self, df_columns: List[str]) -> bool:
        """Check that DataFrame columns match expected order."""
        return df_columns == self.columns

    def validate_dtypes(self, df_dtypes: Dict[str, str]) -> bool:
        """Check that DataFrame dtypes match expected types."""
        for col, expected in self.dtypes.items():
            if col not in df_dtypes:
                return False
            if str(df_dtypes[col]) != expected:
                return False
        return True

    def describe(self) -> str:
        """Human-readable schema description."""
        return f"ChunkSchema(v{self.version}, columns={self.columns})"
