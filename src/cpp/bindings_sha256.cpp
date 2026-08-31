// =============================================================================
// bindings_sha256.cpp
// =============================================================================
// Pybind11 bindings for deterministic SHA‑256 hashing.
//
// Exposes:
//     sha256_file(path: str) -> str
//
// Python module name:
//     boundary_hash
//
// Usage in Python:
//     from boundary_hash import sha256_file
//     digest = sha256_file("data/intermediate/merged.nc")
//
// This module is intentionally minimal and stable. It provides a compiled,
// deterministic boundary for artifact validation across all pipeline stages.
// =============================================================================

#include <pybind11/pybind11.h>
#include "deterministic_sha256.cpp"

namespace py = pybind11;

// =============================================================================
// PYBIND11_MODULE(boundary_hash, m)
// =============================================================================
// Defines the Python module `boundary_hash` and exposes the function
// `sha256_file` to Python callers.
// =============================================================================
PYBIND11_MODULE(boundary_hash, m) {
    m.doc() = "Deterministic SHA‑256 hashing for ERA5 pipeline artifacts.";

    m.def(
        "sha256_file",
        &sha256_file,
        "Compute deterministic SHA‑256 digest of a file at the given path."
    );
}
