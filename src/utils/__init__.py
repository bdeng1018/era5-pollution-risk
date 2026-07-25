"""
Utilities Package (Branch 2)
----------------------------

This package contains lightweight, side‑effect‑free helpers used across
deterministic pipeline stages (Branch 2) and optional AI/LLM/RAG tooling
introduced in Branch 3. Utilities are intentionally minimal and safe to
import in all execution contexts.

Current contents:
- environment validation (env_check)
- lightweight logging helpers (logging)
- simple metadata utilities (metadata)
- minimal path helpers (ensure_dir)

Branch 2 Note
-------------
The ingestion and preprocessing pipeline (Stages 1–2) does not rely on this
package. Utilities are used primarily in later deterministic stages (Stages 3–4)
and general tooling.

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
