"""
Stage 3: Chunk Planner (Branch 2)

Builds deterministic ChunkSpec objects from Stage 2 metadata.
Responsible for:
- time window segmentation (fixed-size windows)
- variable segmentation
- optional spatial tiling
- constructing input/output paths
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core_03.chunk_spec import ChunkSpec


class ChunkPlanner:
    def __init__(self, config: Dict[str, Any]):
        """
        Branch 2 Stage 3 config structure:

        config["stage3"]["variables"] -> List[str] (ERA5 shortNames)
        config["stage3"]["chunk"]["size"]["time"] -> int (hours)
        config["stage3"]["chunk"]["stride"]["time"] -> int (hours)

        config["paths"]["chunk_output_dir"] -> str
        config["paths"]["chunk_metadata_dir"] -> str
        """

        self._cfg = config

        stage3 = config["stage3"]

        # Variables are ERA5 shortNames (t2m, u10, v10, etc.)
        self.variables: List[str] = stage3["variables"]

        chunk_cfg = stage3["chunk"]
        self.chunk_size_hours: int = chunk_cfg["size"]["time"]
        self.chunk_stride_hours: int = chunk_cfg["stride"]["time"]

        self.spatial_tiles: Optional[List[str]] = stage3.get("spatial_tiles")

        paths_cfg = config["paths"]
        self.output_dir: Path = Path(paths_cfg["chunk_output_dir"])
        self.metadata_dir: Path = Path(paths_cfg["chunk_metadata_dir"])

        self.metadata: Dict[str, Any] = {}

    # --------------------------------------------------------------------------
    # Time window builder
    # --------------------------------------------------------------------------

    def _build_time_windows(self) -> List[Tuple[str, str]]:
        timestamps = sorted(self.metadata["timestamps"])
        windows: List[Tuple[str, str]] = []

        n = len(timestamps)
        size = self.chunk_size_hours
        stride = self.chunk_stride_hours

        i = 0
        while i + size <= n:
            start_ts = timestamps[i]
            end_ts = timestamps[i + size - 1]
            windows.append((start_ts, end_ts))
            i += stride

        return windows

    # --------------------------------------------------------------------------
    # Build ChunkSpecs
    # --------------------------------------------------------------------------

    def build(self, metadata: Dict[str, Any], dtypes: Dict[str, Any]) -> List[ChunkSpec]:
        """
        Stage 2 metadata format:

        metadata = {
            "variables": {
                "<shortName>": {
                    "<timestamp>": "/path/to/parquet",
                    ...
                },
                ...
            },
            "timestamps": [...]
        }
        """

        self.metadata = metadata

        specs: List[ChunkSpec] = []
        time_windows = self._build_time_windows()

        for variable in self.variables:

            # Skip variables missing from Stage 2 metadata
            if variable not in self.metadata["variables"]:
                continue

            variable_files = self.metadata["variables"][variable]

            for start_ts, end_ts in time_windows:

                # Skip windows missing required timestamps
                if start_ts not in variable_files:
                    continue

                for tile in self.spatial_tiles or [None]:

                    input_path = Path(variable_files[start_ts])

                    output_name = f"{variable}_{start_ts}_{tile or 'full'}.parquet"
                    output_path = self.output_dir / output_name

                    metadata_name = f"{variable}_{start_ts}_{tile or 'full'}.json"
                    metadata_path = self.metadata_dir / metadata_name

                    spec = ChunkSpec(
                        variable=variable,
                        time_window=(start_ts, end_ts),
                        spatial_tile=tile,
                        input_path=input_path,
                        output_path=output_path,
                        metadata_path=metadata_path,
                    )
                    specs.append(spec)

        return specs
