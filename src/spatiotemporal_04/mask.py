"""
Stage 4 – Spatial Mask Invariant
================================

Purpose
-------
Establish spatial consistency across all variables by detecting spatial holes
(NaNs across the time dimension), constructing a boolean mask (lat × lon),
and applying this mask to the dataset.

This invariant ensures that downstream temporal alignment, interpolation,
tensor assembly, and QC operate only on valid spatial pixels.

Responsibilities
----------------
- Detect spatial holes (NaNs across time)
- Construct a boolean mask (True = valid pixel, False = invalid pixel)
- Apply the mask to all fields (preserving NaNs where appropriate)
- Compute valid_fraction
- Detect hole coordinates
- Produce a deterministic mask metadata contract
- Do NOT modify spatial resolution or coordinate structure
- Do NOT modify temporal structure
"""

import numpy as np
import xarray as xr

# ------------------------------------------------------------------------------
# Core mask computation
# ------------------------------------------------------------------------------


def compute_spatial_mask(ds: xr.Dataset, fields: list[str]) -> np.ndarray:
    """
    Compute a boolean mask indicating valid spatial pixels.

    A pixel is valid if *all* fields have at least one non-NaN value
    across the entire time dimension.

    Shape: (lat, lon)
    """

    masks = []

    for field in fields:
        arr = ds[field].values  # shape: (time, lat, lon)

        # True if ANY time slice is valid at that pixel
        field_mask = ~np.isnan(arr).all(axis=0)

        masks.append(field_mask)

    # Intersection across all fields
    combined = np.logical_and.reduce(masks)

    return combined


# ------------------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------------------


def compute_valid_fraction(mask: np.ndarray) -> float:
    total = mask.size
    valid = np.sum(mask)
    return float(valid / total)


def detect_holes(mask: np.ndarray) -> list[tuple[int, int]]:
    holes = np.argwhere(~mask)
    return [(int(i), int(j)) for i, j in holes]


# ------------------------------------------------------------------------------
# Contract builder
# ------------------------------------------------------------------------------


def build_mask_contract(mask: np.ndarray) -> dict:
    """
    Construct Stage 4 mask metadata contract.
    """

    return {
        "mask": mask,
        "valid_fraction": compute_valid_fraction(mask),
        "holes": detect_holes(mask),
        "mask_shape": mask.shape,
    }


# ------------------------------------------------------------------------------
# Mask application
# ------------------------------------------------------------------------------


def apply_mask(ds: xr.Dataset, mask: np.ndarray, fields: list[str]) -> xr.Dataset:
    """
    Apply the spatial mask to all fields.

    Invalid pixels become NaN for all time slices.

    This preserves:
    - spatial resolution
    - coordinate structure
    - temporal structure
    """

    ds_masked = ds.copy()

    for field in fields:
        arr = ds_masked[field].values  # (time, lat, lon)

        # Broadcast mask to (time, lat, lon)
        mask3d = np.broadcast_to(mask, arr.shape)

        # Apply mask: invalid pixels → NaN
        arr[~mask3d] = np.nan

        ds_masked[field].values[:] = arr

    return ds_masked


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------


def process_spatial_consistency(
    ds: xr.Dataset,
    fields: list[str],
) -> tuple[xr.Dataset, dict]:
    """
    Stage 4 mask invariant entry point.

    Returns
    -------
    (xr.Dataset, dict)
        Masked dataset + mask metadata contract.
    """

    # 1. Compute mask
    mask = compute_spatial_mask(ds, fields)

    # 2. Apply mask
    ds_masked = apply_mask(ds, mask, fields)

    # 3. Attach mask to dataset
    ds_masked["mask"] = (("lat", "lon"), mask)

    # 4. Build contract
    contract = build_mask_contract(mask)

    # Logging hook
    print("[Stage 4][mask] valid_fraction:", contract["valid_fraction"])
    print("[Stage 4][mask] holes:", len(contract["holes"]))

    return ds_masked, contract
