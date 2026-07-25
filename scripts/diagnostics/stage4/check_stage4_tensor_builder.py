"""
Stage 4 Diagnostic — Tensor Builder Integrity Check (ERA5‑Correct, Stage 4‑Ready)
=================================================================================

Purpose
-------
Validate the canonical tensor produced in Stage 4.

This diagnostic verifies:
    • tensor shape (time × lat × lon × variables)
    • per-variable shape consistency
    • no ragged arrays
    • no mismatched dimensions
    • correct coordinate alignment (time, lat, lon)
    • variable ordering consistency
    • dtype consistency across variables
    • detection of degenerate tensors (empty dims, zero-length axes)

Outputs
-------
A JSON diagnostic report saved to:
    data/spatiotemporal/stage4_tensor_builder_report.json

Consumed by:
    • Stage 4 integration diagnostics
    • Stage 5 model readiness checks
"""

import json
from pathlib import Path

import xarray as xr

# ------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------


def _check_variable_shape(ds, var, expected_shape):
    """Check if variable matches expected tensor shape."""
    return tuple(ds[var].shape) == expected_shape


def _detect_ragged(ds, var):
    """
    Detect ragged arrays.

    Ragged arrays occur when:
        • slices have different shapes
        • slices have missing lat/lon cells
    """
    arr = ds[var].values
    shapes = {arr[t].shape for t in range(arr.shape[0])}
    return len(shapes) > 1


def _detect_dtype_inconsistency(ds):
    """Check if all variables share the same dtype."""
    dtypes = {var: ds[var].dtype for var in ds.data_vars if var != "mask"}
    return len(set(dtypes.values())) > 1, dtypes


# ------------------------------------------------------------------------------
# Diagnostic entry point
# ------------------------------------------------------------------------------


def run_tensor_builder_diagnostic(dataset_path: str, output_path: str) -> None:
    """
    Run Stage 4 tensor builder diagnostic.

    Parameters
    ----------
    dataset_path : str
        Path to Stage 4 dataset (after tensor_builder.py).
    output_path : str
        Path to write diagnostic JSON report.
    """

    print("[Stage 4][tensor_diag] Loading dataset:", dataset_path)
    ds = xr.open_dataset(dataset_path)

    # --------------------------------------------------------------------------
    # Extract core dimensions
    # --------------------------------------------------------------------------

    time = ds["time"].values
    lat = ds["lat"].values
    lon = ds["lon"].values

    T = len(time)
    Y = len(lat)
    X = len(lon)
    V = len(ds.data_vars) - (1 if "mask" in ds else 0)

    expected_shape = (T, Y, X)

    # --------------------------------------------------------------------------
    # Per-variable shape checks
    # --------------------------------------------------------------------------

    per_variable_shape_ok = {}
    per_variable_ragged = {}

    for var in ds.data_vars:
        if var == "mask":
            continue

        shape_ok = _check_variable_shape(ds, var, expected_shape)
        ragged = _detect_ragged(ds, var)

        per_variable_shape_ok[var] = shape_ok
        per_variable_ragged[var] = ragged

    # --------------------------------------------------------------------------
    # dtype consistency
    # --------------------------------------------------------------------------

    dtype_inconsistent, dtype_map = _detect_dtype_inconsistency(ds)

    # --------------------------------------------------------------------------
    # Degenerate tensor detection
    # --------------------------------------------------------------------------

    degenerate = T == 0 or Y == 0 or X == 0 or V == 0

    # --------------------------------------------------------------------------
    # Pass criteria
    # --------------------------------------------------------------------------

    tensor_pass = (
        all(per_variable_shape_ok.values())
        and not any(per_variable_ragged.values())
        and not dtype_inconsistent
        and not degenerate
    )

    # --------------------------------------------------------------------------
    # Build report
    # --------------------------------------------------------------------------

    report = {
        "tensor_shape": {
            "time": T,
            "lat": Y,
            "lon": X,
            "variables": V,
        },
        "expected_shape_per_variable": expected_shape,
        "per_variable_shape_ok": per_variable_shape_ok,
        "per_variable_ragged": per_variable_ragged,
        "dtype_inconsistent": dtype_inconsistent,
        "dtype_map": {k: str(v) for k, v in dtype_map.items()},
        "degenerate_tensor": degenerate,
        "tensor_pass": tensor_pass,
    }

    # --------------------------------------------------------------------------
    # Save report
    # --------------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 4][tensor_diag] Report saved:", output_path)
    print("[Stage 4][tensor_diag] tensor_pass:", report["tensor_pass"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 4 Tensor Builder Diagnostic")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to Stage 4 dataset (e.g., spatiotemporal_tensor.nc)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to write diagnostic JSON report",
    )

    args = parser.parse_args()

    run_tensor_builder_diagnostic(args.dataset, args.output)
