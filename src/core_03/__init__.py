"""
Stage 3: Chunked Core Processing (Branch 2)

This package implements the parallel, deterministic chunk-processing
engine that transforms Stage 2 preprocessed ERA5 data into stable,
schema‑validated intermediate artifacts. Stage 3 is the foundation for
all downstream spatiotemporal structuring (Stage 4) and feature
engineering (Stage 5).

Branch 2 modules:
    - chunk_spec.py         — defines the atomic unit of work
    - chunk_planner.py      — builds deterministic ChunkSpec lists
    - chunk_worker.py       — processes a single chunk (load → transform → write)
    - chunk_orchestrator.py — parallel execution engine with retry + logging
    - chunk_schema.py       — deterministic column order + dtype enforcement

Branch 2 goals:
    - metadata‑driven chunk planning
    - deterministic transforms
    - schema‑validated Parquet outputs
    - parallel‑safe worker isolation
    - reproducible intermediate artifacts

Branch 3 will add:
    - distributed execution backends (Ray/Dask/Multiprocessing clusters)
    - spatial tiling strategies for large‑domain parallelism
    - advanced retry + failure isolation
    - chunk lineage + provenance tracking
    - performance instrumentation + metrics
    - multi‑file chunk stitching + partitioning

The orchestrator is exposed as the main entrypoint for convenience.
"""

from .chunk_orchestrator import ChunkOrchestrator
