"""
ERA5 Pollution Risk Pipeline — Branch 2
=======================================

This package initializer is intentionally minimal.

Purpose
-------
The `src/` package defines the top‑level namespace for all deterministic
pipeline stages (Stage 1–5). To keep import behavior predictable and
test‑friendly, this file must not import heavy modules or perform any side
effects.

Design Goals
------------
- Preserve stable namespace resolution across all pipeline stages.
- Avoid importing heavy dependencies (xarray, numpy, eccodes) at package load.
- Ensure `python -m` execution works cleanly for all stage drivers.
- Prevent side effects during pytest collection for Stage 1–5.
- Mark `src/` as a Python package without altering import semantics.

Branch 2 Architecture
---------------------
- Stage 1: ERA5 download (GRIB ingestion)
- Stage 2: preprocessing (unzip → inspect → convert → metadata)
- Stage 3: chunked core processing (parallelized merge)
- Stage 4: spatiotemporal compiler
    - grid → mask → temporal_align → temporal_interpolate → qc → metadata → tensor_builder
- Stage 5: feature engineering (temporal → spatial → composite → metadata → qc → registry)

Branch 3 Note
-------------
Future Branch 3 may introduce optional AI/LLM/RAG tooling for diagnostics,
metadata search, or reporting. These components will live in separate modules
and will not modify the deterministic import behavior of `src/`.

Invariant
---------
Each module imports only what it needs, when it needs it.
This file must remain minimal to preserve that invariant.
"""

# ==============================================================================
# Minimal import‑path patch
# ==============================================================================
# Rationale:
#     Many pipeline modules import lightweight utilities such as:
#         from boundary_hash import sha256_file
#
#     Python does not automatically include the `src/` directory in sys.path
#     during pytest collection or when running drivers via `python -m`.
#
#     This patch adds *only* the directory containing this file to sys.path.
#     It does NOT import any pipeline modules, does NOT load heavy dependencies,
#     and does NOT violate deterministic behavior.
#
#     This ensures that lightweight modules (e.g., boundary_hash.py) are
#     discoverable without altering import semantics for any stage.
#
#     This is the minimal, safe fix required for test collection.
#
import os
import sys

# Add the directory containing this file (i.e., `src/`) to Python's module path.
# This enables imports like `from boundary_hash import sha256_file` to succeed.
sys.path.append(os.path.dirname(__file__))
