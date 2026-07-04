"""
Stage 3: Chunk Specification

Defines the atomic unit of work for parallel preprocessing.
A ChunkSpec describes one deterministic processing task:
- variable
- time window
- optional spatial tile
- input paths (from Stage 2)
- output paths (intermediate chunk parquet)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass(frozen=True)
class ChunkSpec:
    variable: str
    time_window: Tuple[str, str]  # ("2023-09-01", "2023-09-01")
    spatial_tile: Optional[str]   # e.g., "tile_001" or None
    input_path: Path
    output_path: Path
    metadata_path: Path

    def describe(self) -> str:
        """Human-readable description for logging."""
        tile = self.spatial_tile or "full-domain"
        return (
            f"ChunkSpec(variable={self.variable}, "
            f"time_window={self.time_window}, "
            f"tile={tile})"
        )
