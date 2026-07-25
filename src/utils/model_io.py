"""
Model I/O utilities for the ERA5 pipeline (Branch 2)

Provides minimal, deterministic model serialization using pickle. This
keeps artifact handling simple during Branch 2 while the modeling layer
is still evolving (multiple model families, metadata-rich artifacts,
and versioning planned).

Branch 2 Notes
--------------
Branch 2 introduces expanded modeling and evaluation, but model I/O
remains intentionally lightweight:
- pickle-only serialization
- no registry integration
- no versioned artifacts
- no metadata embedding beyond what callers provide

This module must remain side-effect-free and safe to import during
pytest collection and `python -m` execution.

Branch 3 Notes
--------------
Branch 3 will introduce:
- a model registry
- versioned, metadata-rich artifacts
- safer serialization formats
- lineage-aware model loading
- optional AI/LLM/RAG tooling for model summaries and diagnostics

These advanced features will live in separate modules and will not
change the deterministic behavior of this minimal pickle-based loader.

Invariant
---------
This module must remain:
- deterministic
- pickle-only
- free of heavy dependencies
- safe to import in all execution contexts
"""

import pickle
from pathlib import Path


def save_model(model, path: str | Path) -> None:
    """
    Serialize a model object using pickle.

    Parameters
    ----------
    model : object
        The model object to serialize. Must be pickle‑compatible.
    path : str or Path
        Destination file path.

    Raises
    ------
    TypeError
        If the model contains non‑pickle‑serializable components.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(p, "wb") as f:
            pickle.dump(model, f)
    except Exception as e:
        raise TypeError(f"Failed to pickle model: {e}")


def load_model(path: str | Path):
    """
    Load a model object serialized with pickle.

    Parameters
    ----------
    path : str or Path
        Path to the serialized model file.

    Returns
    -------
    object
        The deserialized model.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    Exception
        If the model cannot be unpickled (e.g., missing class definition).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")

    try:
        with open(p, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load model from {p}: {e}")
