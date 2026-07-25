"""
ERA5 Pollution Risk Pipeline — Branch 2
=======================================

This package initializer is intentionally empty.

Purpose
-------
The `src/` package defines the top‑level namespace for all deterministic
pipeline stages (Stage 1–4). To keep import behavior predictable and
test‑friendly, this file must not import any modules or perform any side
effects.

Design Goals
------------
- Preserve stable namespace resolution across all pipeline stages.
- Avoid importing heavy dependencies (xarray, numpy, eccodes) at package load.
- Ensure `python -m` execution works cleanly for all stage drivers.
- Prevent side effects during pytest collection for Stage 1–4.
- Mark `src/` as a Python package without altering import semantics.

Branch 2 Architecture
---------------------
- Stage 1: ERA5 download (GRIB ingestion)
- Stage 2: preprocessing (unzip → inspect → convert → metadata)
- Stage 3: chunked core processing (parallelized merge)
- Stage 4: spatiotemporal compiler
    - grid → mask → temporal_align → temporal_interpolate → qc → metadata → tensor_builder

Branch 3 Note
-------------
Future Branch 3 may introduce optional AI/LLM/RAG tooling for diagnostics,
metadata search, or reporting. These components will live in separate modules
and will not modify the deterministic import behavior of `src/`.

Invariant
---------
Each module imports only what it needs, when it needs it.
This file must remain empty to preserve that invariant.
"""
