"""
Deterministic SHA‑256 hashing module.

This module provides a *safe Python fallback* for hashing pipeline artifacts
while also attempting to load the compiled C++ extension (`boundary_hash.so`)
when available.

Design goals:
    • deterministic output across platforms
    • safe fallback when C++ extension is missing or fails to load
    • identical API for both Python and C++ implementations
    • minimal dependencies
    • streaming reads for large files

Tests across Stage 01–04 import `sha256_file` from this module. This wrapper
ensures the import always succeeds, even if the compiled extension is not yet
built or not importable in the current environment.
"""

import hashlib
from collections.abc import Callable


# ==============================================================================
# Pure‑Python deterministic SHA‑256 implementation
# ==============================================================================
def _sha256_file_python(path: str) -> str:
    """
    Compute a deterministic SHA‑256 digest of a file using pure Python.

    Parameters
    ----------
    path : str
        Path to the file to hash.

    Returns
    -------
    str
        Hexadecimal SHA‑256 digest.

    Notes
    -----
    • Uses a streaming 8 KB buffer to avoid memory spikes.
    • Deterministic across all platforms and Python versions.
    • Serves as a fallback when the C++ extension is unavailable.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# Attempt to load the compiled C++ extension
# ==============================================================================
try:
    # If the compiled extension exists and loads correctly, use it.
    from boundary_hash import sha256_file as _sha256_file_cpp  # type: ignore

    sha256_file: Callable[[str], str] = _sha256_file_cpp

except Exception:
    # Fallback: use pure Python implementation.
    sha256_file = _sha256_file_python
