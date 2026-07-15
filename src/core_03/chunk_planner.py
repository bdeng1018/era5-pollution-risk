"""
Stage 3: Chunk Planner (Branch 2 — Hourly Timeline, Single‑Variable)
====================================================================

This planner constructs ChunkSpec objects using the FULL hourly timestamp
timeline produced by Stage 2 metadata.json.

Branch‑2 constraints:
    • exactly one input parquet per chunk
    • no time_window field
    • no spatial tiling
    • no multi‑input lists
    • no metadata_path field

Single‑variable mode:
    • each chunk contains: time, lat, lon, <variable>
    • worker derives schema per chunk (no shared schema)
"""

from pathlib import Path
from typing import Any, Dict, List

from src.core_03.chunk_spec import ChunkSpec


class ChunkPlanner:
    def __init__(self, config: Dict[str, Any]):
        stage3 = config["stage3"]

        # Variables requested by config
        self.requested_variables: List[str] = stage3["variables"]

        # Window parameters
        chunk_cfg = stage3["chunk"]
        self.window_size_hours: int = chunk_cfg["window_size_hours"]
        self.window_stride_hours: int = chunk_cfg["window_stride_hours"]

        # Output directory
        paths_cfg = config["paths"]
        self.output_dir: Path = Path(paths_cfg["chunk_output_dir"])

        # Stage 2 metadata injected at build() time
        self.metadata: Dict[str, Any] = {}

        self.config = config

    # --------------------------------------------------------------------------
    # Helper: compute merge‑eligible variables
    # --------------------------------------------------------------------------
    def _compute_merge_eligible_variables(self) -> List[str]:
        eligible = []
        meta_vars = self.metadata.get("variables", {})

        for var in self.requested_variables:
            if var in meta_vars:
                eligible.append(var)

        return eligible

    # --------------------------------------------------------------------------
    # Build ChunkSpecs from Stage 2 metadata
    # --------------------------------------------------------------------------
    def build(self, metadata: Dict[str, Any], dtypes: Dict[str, Any]) -> List[ChunkSpec]:

        specs: List[ChunkSpec] = []

        # Reconstruct nested metadata structure
        variables = {}
        timestamps = set()

        for key, entry in metadata.items():
            ts, var = key.split("::")
            timestamps.add(ts)

            if var not in variables:
                variables[var] = {}

            variables[var][ts] = entry["path"]

        metadata = {
            "variables": variables,
            "timestamps": sorted(timestamps),
        }

        self.metadata = metadata

        # 1. Merge‑eligible variables
        merge_vars = self._compute_merge_eligible_variables()
        if not merge_vars:
            print("❌ No merge‑eligible variables found.")
            return specs

        # 2. Full hourly timeline
        full_ts = metadata.get("timestamps", [])
        if not full_ts:
            print("❌ metadata['timestamps'] missing or empty.")
            return specs

        # 3. Build windows
        windows: List[List[str]] = []
        n = len(full_ts)
        i = 0

        while i < n:
            window_ts = full_ts[i : i + self.window_size_hours]
            if window_ts:
                windows.append(window_ts)
            i += self.window_stride_hours

        # 4. Build ChunkSpecs for each variable and each window
        for variable in merge_vars:
            variable_files = metadata["variables"][variable]

            for window_ts in windows:
                ts = window_ts[0]  # representative timestamp

                if ts not in variable_files:
                    continue

                input_path = Path(variable_files[ts])
                safe_ts = ts.replace(":", "-")

                output_name = f"{variable}_{safe_ts}_{self.window_size_hours}hr.parquet"
                output_path = self.output_dir / output_name

                chunk_id = f"{variable}_{ts}_{self.window_size_hours}hr"

                spec = ChunkSpec(
                    input_path=input_path,
                    output_path=output_path,
                    variable=variable,
                    timestamp=ts,
                    chunk_id=chunk_id,
                )

                specs.append(spec)

        return specs
