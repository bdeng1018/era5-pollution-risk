"""
Stage 3: Chunk Orchestrator (Branch 2)

Responsibilities:
- Load full Branch 2 config.yml
- Validate stage3 block
- Load Stage 2 metadata.json
- Build ChunkSpecs via ChunkPlanner
- Run ChunkWorker tasks in parallel with retries
- Structured logging and deterministic behavior
"""

import argparse
import json
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.core_03.chunk_planner import ChunkPlanner
from src.core_03.chunk_schema import ChunkSchema
from src.core_03.chunk_spec import ChunkSpec
from src.core_03.chunk_worker import ChunkWorker

# ------------------------------------------------------------------------------
# CONFIG LOADING
# ------------------------------------------------------------------------------

def load_config(config_path: str) -> Dict[str, Any]:
    """Load full Branch 2 config.yml."""
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    if "paths" not in cfg:
        raise ValueError("Missing 'paths' block in config.yml")

    if "stage3" not in cfg:
        raise ValueError("Missing 'stage3' block in config.yml")

    if "variables" not in cfg["stage3"]:
        raise ValueError("Missing 'stage3.variables' in config.yml")

    return cfg


# ------------------------------------------------------------------------------
# SPEC BUILDING
# ------------------------------------------------------------------------------

def build_specs(config: Dict[str, Any]) -> List[ChunkSpec]:
    """Build ChunkSpecs using metadata.json + ChunkPlanner."""

    # Stage 2 metadata location
    metadata_path = Path(config["paths"]["metadata_dir"]) / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata.json at {metadata_path}")

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    # Schema + planner
    schema = ChunkSchema(config)
    planner = ChunkPlanner(config)

    specs = planner.build(metadata=metadata, dtypes=schema.dtypes)
    return specs


# ------------------------------------------------------------------------------
# ORCHESTRATOR CLASS
# ------------------------------------------------------------------------------

class ChunkOrchestrator:
    def __init__(
        self,
        schema: ChunkSchema,
        max_workers: int = 4,
        max_retries: int = 2,
        logger: Optional[logging.Logger] = None,
    ):
        self.schema = schema
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger("chunk_orchestrator")

    def _run_once(self, worker: ChunkWorker, spec: ChunkSpec) -> ChunkSpec:
        worker.process(spec)
        return spec

    def _run_with_retries(self, worker: ChunkWorker, spec: ChunkSpec) -> ChunkSpec:
        for attempt in range(1, self.max_retries + 2):
            try:
                return self._run_once(worker, spec)
            except Exception as e:
                self.logger.error(
                    f"Chunk failed (attempt {attempt}/{self.max_retries + 1}): "
                    f"{spec.describe()} — {e}"
                )
                if attempt > self.max_retries:
                    raise

        raise RuntimeError("Unreachable retry loop")

    def run(self, specs: List[ChunkSpec]) -> List[ChunkSpec]:
        worker = ChunkWorker(self.schema)
        results: List[ChunkSpec] = []

        self.logger.info(f"Starting Stage 3 with {len(specs)} chunks")

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_with_retries, worker, spec): spec
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

        self.logger.info("Stage 3 complete")
        return results


# ------------------------------------------------------------------------------
# CLI ENTRYPOINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 3 Chunk Orchestrator")
    parser.add_argument("--config", required=True, help="Path to config.yml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Load config.yml
    config = load_config(args.config)

    # Build chunk specs
    specs = build_specs(config)

    # Run orchestrator
    schema = ChunkSchema(config)
    orchestrator = ChunkOrchestrator(schema)
    orchestrator.run(specs)
