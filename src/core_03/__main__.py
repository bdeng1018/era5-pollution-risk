"""
Stage 3: __main__ Entrypoint (Branch 2 — Config‑Driven Windowing)
=================================================================

Purpose
-------
Allows Stage 3 to be executed via:

    python -m src.core_03

This thin wrapper simply delegates execution to the Chunk Orchestrator,
which performs:

- config loading & validation
- Stage 2 metadata loading
- ChunkSpec construction (config‑driven windowing)
- parallel chunk processing
- final merged.nc + metadata + QC output

Why this file exists
--------------------
Python packages can expose a module‑level entrypoint by defining
`__main__.py`. This keeps the orchestrator logic inside
`chunk_orchestrator.py` while enabling clean CLI execution.
"""

from .chunk_orchestrator import main

if __name__ == "__main__":
    main()
