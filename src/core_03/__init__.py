"""
Stage 3: Chunked Core Processing (Branch 2)
===========================================

Overview
--------
Stage 3 implements the parallel, deterministic chunk‑processing engine that
transforms Stage 2 preprocessed ERA5 data into stable, schema‑validated
intermediate artifacts. These artifacts form the foundation for all downstream
spatiotemporal structuring (Stage 4) and feature engineering (Stage 5).

Branch 2 Modules
----------------
    - chunk_spec.py         — defines the atomic unit of work
    - chunk_planner.py      — builds deterministic ChunkSpec lists using
                               config‑driven temporal windowing
    - chunk_worker.py       — processes a single chunk (load → transform → write)
    - chunk_orchestrator.py — parallel execution engine with retry + logging
    - chunk_schema.py       — deterministic column order + dtype enforcement
    - chunk_merge.py        — merges all chunk outputs into merged.nc + metadata + QC

Branch 2 Goals
--------------
    - metadata‑driven chunk planning
    - deterministic transforms
    - schema‑validated Parquet outputs
    - parallel‑safe worker isolation
    - reproducible intermediate artifacts
    - final merged.nc dataset for Stage 4

Branch 3 Roadmap
----------------
    - distributed execution backends (Ray/Dask/cluster multiprocessing)
    - spatial tiling strategies for large‑domain parallelism
    - advanced retry + failure isolation
    - chunk lineage + provenance tracking
    - performance instrumentation + metrics
    - multi‑file chunk stitching + partitioning

Entrypoint
----------
The orchestrator is exposed as the main entrypoint for convenience:

    python -m src.core_03

This delegates execution to chunk_orchestrator.main().
"""

from .chunk_orchestrator import ChunkOrchestrator
