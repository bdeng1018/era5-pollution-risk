"""
Unit Test – Stage 4 Tensor Builder Invariant (Aligned with actual tensor_builder.py)

Purpose:
    Validate that tensor_builder.process_spatiotemporal_merge() produces:
    - a canonical Stage 4 tensor dataset
    - correct shape and dtype
    - correct merging of spatial, temporal, and interpolation contracts
"""

import numpy as np
import xarray as xr

from src.spatiotemporal_04 import tensor_builder


def test_tensor_builder_basic():
    """
    Ensure tensor_builder.process_spatiotemporal_merge() returns:
    - ds_stage4 (xarray.Dataset)
    """

    # --------------------------------------------------------------------------
    # Synthetic spatial grid (actual Stage 4 contract requires full arrays)
    # --------------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)

    grid_contract = {
        "lat": lat,
        "lon": lon,
        "crs": "EPSG:4326",
    }

    # --------------------------------------------------------------------------
    # Synthetic mask contract
    # --------------------------------------------------------------------------
    mask_contract = {
        "mask": np.ones((5, 4), dtype=bool),
        "valid_fraction": 1.0,
    }

    # --------------------------------------------------------------------------
    # Synthetic temporal alignment contract
    # --------------------------------------------------------------------------
    aligned_time = np.array(
        ["2020-01-01T00:00", "2020-01-01T01:00", "2020-01-01T02:00"],
        dtype="datetime64[ns]",
    )

    temporal_contract = {
        "aligned_time": aligned_time,
        "frequency": "1H",
        "missing_timestamps": [],
    }

    # --------------------------------------------------------------------------
    # Synthetic interpolation contract (not used directly by tensor builder)
    # --------------------------------------------------------------------------
    interp_contract = {
        "method": "linear",
        "added_timestamps": [],
        "interpolated_fraction": 0.0,
    }

    # --------------------------------------------------------------------------
    # Synthetic aligned + interpolated dataset
    # --------------------------------------------------------------------------
    temp_data = np.random.rand(3, 5, 4)

    ds_interpolated = xr.Dataset(
        {"temp": (("time", "lat", "lon"), temp_data)},
        coords={"time": aligned_time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # --------------------------------------------------------------------------
    # Run tensor builder invariant (correct argument order)
    # --------------------------------------------------------------------------
    ds_stage4 = tensor_builder.process_spatiotemporal_merge(
        ds_interpolated,
        grid_contract,
        mask_contract,
        temporal_contract,
        fields,
    )

    # --------------------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------------------

    # 1. Output dataset type
    assert isinstance(ds_stage4, xr.Dataset)

    # 2. Dataset must contain all variables
    for field in fields:
        assert field in ds_stage4.data_vars

    # 3. Tensor must have correct dimensions
    assert set(ds_stage4.dims.keys()) == {"time", "lat", "lon"}

    # 4. Shape must match contracts
    assert ds_stage4.lat.size == lat.size
    assert ds_stage4.lon.size == lon.size
    assert ds_stage4.time.size == aligned_time.size

    # 5. No illegal values introduced
    assert not np.isnan(ds_stage4.temp.values).any()

    # 6. dtype must be float
    assert ds_stage4.temp.dtype == float
