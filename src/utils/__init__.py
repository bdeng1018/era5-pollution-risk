"""
Utilities Package (Branch 2)
----------------------------

This package contains lightweight, side‑effect‑free helpers used across
deterministic pipeline stages (Branch 2) and optional AI/LLM/RAG tooling
introduced in Branch 3. Utilities are intentionally minimal and safe to
import in all execution contexts.

Current contents:
- configuration loading (load_config, load_paths, load_yaml)
- deterministic path resolution (Paths, get_path)
- environment validation (env_check)
- lightweight logging helpers
- simple metadata utilities
- minimal filesystem helpers (ensure_dir)

Branch 2 Notes
--------------
The ingestion and preprocessing pipeline (Stages 1–2) does not rely on this
package. Utilities are used primarily in later deterministic stages (Stages 3–5)
and general tooling.

Stage 05 Note
-------------
Feature engineering (IR5) uses:
- load_yaml() for stage-specific configs
- get_path() for deterministic path resolution
- metadata + QC helpers
These utilities remain side‑effect‑free and import‑safe.

Branch 3 Note
-------------
Future AI/LLM/RAG components may import utilities from this package, but will
remain isolated from deterministic pipeline execution.

Important
---------
- This initializer intentionally performs no imports.
- This prevents side effects during pytest discovery and `python -m` execution.
- Heavy configuration loading from Branch 1 has been removed.
"""
