"""
Stage 3: Chunk Specification (Branch 2 — Config‑Driven Windowing)
=================================================================

Purpose
-------
ChunkSpec defines the atomic unit of work for Stage 3 chunk processing.
In Branch 2, each ChunkSpec represents one deterministic preprocessing
task for a single ERA5 variable over a *temporal window* (e.g., 12‑hour,
24‑hour), even though the worker processes only the representative
timestamp’s parquet file.

This simplified, single‑input specification is the public API required
by the Stage 3 test suite and is intentionally stable.

What a ChunkSpec Represents
---------------------------
Each ChunkSpec binds together:

- input_path   : Stage 2 parquet file for the *representative timestamp*
- output_path  : Stage 3 chunk parquet output location
- variable     : ERA5 shortName (e.g., "t2m")
- timestamp    : representative ISO timestamp string
                 (first timestamp of the window)
- chunk_id     : unique identifier used for logging, retries, orchestration

Representative Timestamp
------------------------
ChunkPlanner groups timestamps into windows using:

    stage3.chunk.size.time   → window size (hours)
    stage3.chunk.stride.time → window stride (hours)

For each window, the *first* timestamp is chosen as the representative
timestamp. ChunkWorker processes only the parquet file for that timestamp,
but the resulting chunk semantically represents the entire window.

Why ChunkSpec Stays Simple (Branch 2)
-------------------------------------
Branch 2 intentionally omits:

- multi‑input time windows
- spatial tiling
- multi‑file chunk stitching
- metadata_path fields
- window_start/window_end fields

These appear in Branch 3. The Stage 3 test suite requires the simpler,
single‑input ChunkSpec API.

Determinism & Immutability
--------------------------
ChunkSpec is immutable (frozen=True) to guarantee deterministic behavior
across retries, parallel execution, and logging.

Public API Contract (Stage 3 Tests)
-----------------------------------
Tests expect ChunkSpec to accept the following constructor signature:

    ChunkSpec(
        input_path=Path(...),
        output_path=Path(...),
        variable="t2m",
        timestamp="2020-01-01T00:00",
        chunk_id="t2m_2020-01-01T00:00"
    )

This contract must remain stable for Stage 3 regression tests.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ChunkSpec:
    """
    Atomic unit of Stage 3 work.

    Represents one variable over one temporal window, using the window’s
    representative timestamp. This is the simplified, test‑aligned version
    required by Branch 2. Advanced multi‑input or multi‑window variants
    belong in Branch 3 and are not part of this API.
    """

    input_path: Path
    output_path: Path
    variable: str
    timestamp: str
    chunk_id: str

    def describe(self) -> str:
        """
        Human-readable summary for logging and debugging.
        Used by ChunkWorker and ChunkOrchestrator.
        """
        return (
            f"ChunkSpec(variable={self.variable}, "
            f"timestamp={self.timestamp}, "
            f"input={self.input_path}, "
            f"output={self.output_path}, "
            f"chunk_id={self.chunk_id})"
        )
