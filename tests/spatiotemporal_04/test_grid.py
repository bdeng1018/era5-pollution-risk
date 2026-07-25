"""
Unit Test – Stage 4 Grid Invariant

Purpose:
    Validate that grid.process_grid() produces:
    - a normalized grid-aligned dataset
    - a deterministic grid contract containing lat/lon arrays
    - CRS / spatial metadata required by downstream invariants

This test does NOT check interpolation, masks, temporal alignment,
or tensor construction. It isolates the grid invariant only.
"""

import numpy as np
import xarray as xr

from src.spatiotemporal_04 import grid


def test_grid_process_grid_basic():
    """
    Ensure grid.process_grid() returns:
    - ds_grid (xarray.Dataset)
    - grid_contract (dict with required keys)
    """

    # --------------------------------------------------------------------------
    # Synthetic dataset for testing
    # --------------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)
    time = np.array(["2020-01-01"], dtype="datetime64[ns]")

    ds = xr.Dataset(
        {"temp": (("time", "lat", "lon"), np.random.rand(1, 5, 4))},
        coords={"time": time, "lat": lat, "lon": lon},
    )

    # --------------------------------------------------------------------------
    # Run grid invariant
    # --------------------------------------------------------------------------
    ds_grid, grid_contract = grid.process_grid(ds)

    # --------------------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------------------

    # 1. Output dataset type
    assert isinstance(ds_grid, xr.Dataset)

    # 2. Contract type
    assert isinstance(grid_contract, dict)

    # 3. Required contract keys
    for key in ["lat", "lon", "crs"]:
        assert key in grid_contract, f"Missing key in grid contract: {key}"

    # 4. lat/lon arrays must be numpy arrays
    assert isinstance(grid_contract["lat"], np.ndarray)
    assert isinstance(grid_contract["lon"], np.ndarray)

    # 5. lat/lon shapes must match the dataset
    assert grid_contract["lat"].shape[0] == ds_grid.lat.shape[0]
    assert grid_contract["lon"].shape[0] == ds_grid.lon.shape[0]

    # 6. CRS must be a string or dict (depending on your implementation)
    assert isinstance(grid_contract["crs"], (str, dict))

    # 7. Dataset must contain lat/lon coordinates
    assert "lat" in ds_grid.coords
    assert "lon" in ds_grid.coords
