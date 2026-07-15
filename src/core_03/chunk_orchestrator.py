"""
Stage 3: Chunk Orchestrator (Branch 2 — Single‑Variable, Race‑Free)
===================================================================

This orchestrator coordinates Stage 3:

1. Load config.yml
2. Load Stage 2 metadata.json
3. Build ChunkSpecs using ChunkPlanner
4. Execute ChunkWorker tasks in parallel (no shared schema)
5. Merge chunk outputs
"""

import argparse
import json
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.core_03.chunk_merge import merge_chunks
from src.core_03.chunk_planner import ChunkPlanner
from src.core_03.chunk_spec import ChunkSpec
from src.core_03.chunk_worker import ChunkWorker

# ------------------------------------------------------------------------------
# CONFIG LOADING
# ------------------------------------------------------------------------------

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    # Required blocks
    if "paths" not in cfg:
        raise ValueError("Missing 'paths' block in config.yml")

    if "metadata_dir" not in cfg["paths"]:
        raise ValueError("Missing 'paths.metadata_dir' in config.yml")

    if "stage3" not in cfg:
        raise ValueError("Missing 'stage3' block in config.yml")

    stage3 = cfg["stage3"]

    if "variables" not in stage3:
        raise ValueError("Missing 'stage3.variables' in config.yml")

    if "chunk" not in stage3:
        raise ValueError("Missing 'stage3.chunk' in config.yml")

    chunk_cfg = stage3["chunk"]

    if "size" not in chunk_cfg or "time" not in chunk_cfg["size"]:
        raise ValueError("Missing 'stage3.chunk.size.time' in config.yml")

    if "stride" not in chunk_cfg or "time" not in chunk_cfg["stride"]:
        raise ValueError("Missing 'stage3.chunk.stride.time' in config.yml")

    if "output" not in stage3:
        raise ValueError("Missing 'stage3.output' in config.yml")

    if "chunk_metadata_dir" not in stage3["output"]:
        raise ValueError("Missing 'stage3.output.chunk_metadata_dir' in config.yml")

    # Orchestrator settings
    orch_cfg = stage3.get("orchestrator", {})
    stage3["orchestrator"] = {
        "max_workers": orch_cfg.get("max_workers", 6),
        "max_retries": orch_cfg.get("max_retries", 2),
    }

    # Normalize windowing parameters
    chunk_cfg["window_size_hours"] = chunk_cfg["size"]["time"]
    chunk_cfg["window_stride_hours"] = chunk_cfg["stride"]["time"]

    return cfg


# ------------------------------------------------------------------------------
# SPEC BUILDING (NO SHARED SCHEMA)
# ------------------------------------------------------------------------------

def build_specs(config: Dict[str, Any]) -> List[ChunkSpec]:
    metadata_path = Path(config["paths"]["metadata_dir"]) / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata.json at {metadata_path}")

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    # Planner builds specs and injects schema per variable internally
    planner = ChunkPlanner(config)
    specs = planner.build(metadata=metadata, dtypes={})

    return specs


# ------------------------------------------------------------------------------
# ORCHESTRATOR CLASS (NO SHARED SCHEMA)
# ------------------------------------------------------------------------------

class ChunkOrchestrator:
    def __init__(
        self,
        metadata_dir: Path,
        max_workers: int,
        max_retries: int,
        logger: Optional[logging.Logger] = None,
    ):
        self.metadata_dir = metadata_dir
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger("chunk_orchestrator")

    # --------------------------------------------------------------------------
    # Worker execution (schema is per‑chunk inside worker)
    # --------------------------------------------------------------------------

    def _run_once(self, spec: ChunkSpec) -> ChunkSpec:
        worker = ChunkWorker()  # no shared schema
        worker.process(spec, metadata_dir=self.metadata_dir)
        return spec

    def _run_with_retries(self, spec: ChunkSpec) -> ChunkSpec:
        for attempt in range(1, self.max_retries + 2):
            try:
                return self._run_once(spec)
            except Exception as e:
                self.logger.error(
                    f"Chunk failed (attempt {attempt}/{self.max_retries + 1}): "
                    f"{spec.describe()} — {e}"
                )
                if attempt > self.max_retries:
                    raise
        raise RuntimeError("Unreachable retry loop")

    # --------------------------------------------------------------------------
    # Parallel execution
    # --------------------------------------------------------------------------

    def run(self, specs: List[ChunkSpec]) -> List[ChunkSpec]:
        results: List[ChunkSpec] = []

        self.logger.info(f"Starting Stage 3 with {len(specs)} chunks")

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_with_retries, spec): spec
                for spec in specs
            }

            for future in as_completed(futures):
                spec = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.info(f"Completed: {spec.describe()}")
                except Exception as e:
                    self.logger.error(f"Failed permanently: {spec.describe()} — {e}")

        self.logger.info("Stage 3 chunk processing complete")
        return results


# ------------------------------------------------------------------------------
# CLI ENTRYPOINT
# ------------------------------------------------------------------------------

def main():
    import multiprocessing
    multiprocessing.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser(description="Stage 3 Chunk Orchestrator")
    parser.add_argument("--config", required=True, help="Path to config.yml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("chunk_orchestrator")

    config = load_config(args.config)
    specs = build_specs(config)

    metadata_dir = Path(config["stage3"]["output"]["chunk_metadata_dir"])
    orch_cfg = config["stage3"]["orchestrator"]

    orchestrator = ChunkOrchestrator(
        metadata_dir=metadata_dir,
        max_workers=orch_cfg["max_workers"],
        max_retries=orch_cfg["max_retries"],
        logger=logger,
    )

    results = orchestrator.run(specs)

    logger.info("Merging chunk outputs into merged.nc")
    merge_chunks(results, config)


if __name__ == "__main__":
    main()
