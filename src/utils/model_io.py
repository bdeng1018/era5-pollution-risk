"""
Minimal model I/O utilities for Branch 1.

Branch 1 uses a trivial baseline model (mean predictor), so model
serialization is intentionally simple and relies solely on pickle.
This keeps the artifact format lightweight and easy to inspect.

Branch 2 will introduce:
- a model registry
- versioned artifacts
- metadata-rich model files
- support for multiple model classes
- safer serialization formats
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