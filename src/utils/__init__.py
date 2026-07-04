"""
Utilities Package (Branch 2)
----------------------------

This package contains lightweight, side‑effect‑free helpers used across
later pipeline stages (Branch 3+). The Branch 2 ingestion and preprocessing
pipeline does NOT rely on this package.

Current contents:
- environment validation (env_check)
- lightweight logging helpers (logging)
- simple metadata utilities (metadata)
- minimal path helpers (ensure_dir)

Important:
- This initializer intentionally performs no imports.
- This prevents side effects during pytest discovery and `python -m` execution.
- Heavy configuration loading from Branch 1 has been removed.
"""
