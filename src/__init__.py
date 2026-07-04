"""
ERA5 pipeline source package (Branch 2).

This initializer intentionally defines no imports or execution logic.
Keeping this file empty ensures:

- clean namespace resolution for all pipeline stages
- predictable behavior during `python -m` execution
- fast, side‑effect‑free pytest discovery
- no accidental loading of heavy modules during Stage 1–3

Branch 2 modules import only what they need, when they need it.
This file exists solely to mark `src/` as a Python package.
"""
