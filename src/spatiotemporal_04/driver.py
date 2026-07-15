"""
Stage 4 – Spatiotemporal Compiler Orchestrator
==============================================

Executes all Stage 4 invariants in strict compiler order:

1. grid.py                 – grid normalization & spatial contract
2. mask.py                 – spatial mask & spatial consistency invariant
3. temporal_align.py       – temporal alignment invariant
4. temporal_interpolate.py – temporal interpolation invariant
5. tensor_builder.py       – canonical tensor construction
6. qc.py                   – final QC invariant
7. metadata.py             – metadata contract assembly

Supports:
    python -m src.spatiotemporal_04.driver --config configs/config.yml

Outputs:
- Stage 4 canonical tensor (time × lat × lon × variables)
- QC report (dict)
- Stage 4 metadata (dict)
"""

import argparse
import pickle
from typing import Dict, List, Optional

import xarray as xr
import yaml

import src.spatiotemporal_04.grid as grid
import src.spatiotemporal_04.mask as mask
import src.spatiotemporal_04.metadata as metadata
import src.spatiotemporal_04.qc as qc
import src.spatiotemporal_04.temporal_align as temporal_align
import src.spatiotemporal_04.temporal_interpolate as temporal_interpolate
import src.spatiotemporal_04.tensor_builder as tensor_builder

# ------------------------------------------------------------------------------
# CONFIG LOADER
# ------------------------------------------------------------------------------

def load_config(path: str) -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ------------------------------------------------------------------------------
# STAGE 4 EXECUTION
# ------------------------------------------------------------------------------

def run_stage4(
    config: Optional[Dict] = None,
    path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    out_dataset: Optional[str] = None,
    out_qc: Optional[str] = None,
    out_meta: Optional[str] = None,
):
    """
    Execute Stage 4 either via:
        - YAML config (Branch 2 pipeline)
        - direct arguments (system test)
    """

    # --------------------------------------------------------------------------
    # 1. Resolve configuration source
    # --------------------------------------------------------------------------
    if config is not None:
        stage3_path = config["paths"]["stage3_merged"]
        fields = config["stage4"]["fields"]
        out_dataset = config["paths"]["stage4_dataset"]
        out_qc = config["paths"]["stage4_qc"]
        out_meta = config["paths"]["stage4_metadata"]
    else:
        stage3_path = path
        assert stage3_path is not None, "path must be provided"
        assert fields is not None, "fields must be provided"
        assert out_dataset is not None, "out_dataset must be provided"
        assert out_qc is not None, "out_qc must be provided"
        assert out_meta is not None, "out_meta must be provided"

    # Pyright narrowing
    from typing import List, cast

    fields = cast(List[str], fields)
    stage3_path = cast(str, stage3_path)
    out_dataset = cast(str, out_dataset)
    out_qc = cast(str, out_qc)
    out_meta = cast(str, out_meta)

    # --------------------------------------------------------------------------
    # 2. Load Stage 3 dataset
    # --------------------------------------------------------------------------
    ds_raw = xr.open_dataset(stage3_path)

    # --------------------------------------------------------------------------
    # 3. GRID
    # --------------------------------------------------------------------------
    ds_grid, grid_contract = grid.process_grid(ds_raw)

    # --------------------------------------------------------------------------
    # 4. MASK
    # --------------------------------------------------------------------------
    ds_masked, mask_contract = mask.process_spatial_consistency(ds_grid, fields)

    # --------------------------------------------------------------------------
    # 5. TEMPORAL ALIGNMENT
    # --------------------------------------------------------------------------
    ds_aligned, temporal_contract = temporal_align.process_temporal_alignment(
        ds_masked, fields
    )

    # --------------------------------------------------------------------------
    # 6. TEMPORAL INTERPOLATION
    # --------------------------------------------------------------------------
    ds_interpolated, interp_contract = temporal_interpolate.process_interpolation(
        ds_aligned, fields
    )

    # --------------------------------------------------------------------------
    # 7. TENSOR BUILDER (contract‑driven)
    # --------------------------------------------------------------------------
    ds_stage4 = tensor_builder.process_spatiotemporal_merge(
        ds_interpolated,
        grid_contract,
        mask_contract,
        temporal_contract,
        fields,
    )

    # --------------------------------------------------------------------------
    # 8. QC (destructive cleaning)
    # --------------------------------------------------------------------------
    ds_clean, qc_report = qc.process_qc(ds_stage4, fields)

    # --------------------------------------------------------------------------
    # 9. METADATA
    # --------------------------------------------------------------------------
    tensor_meta = {
        "variables": fields,
        "shape": ds_clean.to_array().shape,
        "dtype_summary": {field: str(ds_clean[field].dtype) for field in fields},
        "units": {
            "t2m": "K",
            "d2m": "K",
            "u10": "m/s",
            "v10": "m/s",
            "msl": "hPa",
            "sp": "hPa",
            "tcc": "fraction",
            "blh": "m",
            "cape": "J/kg",
            "cin": "J/kg",
            "tco3": "kg/m^2",
            "tcwv": "kg/m^2",
        },
    }

    stage4_metadata = metadata.build_metadata(
        grid_meta=grid_contract,
        mask_meta=mask_contract,
        qc_meta=qc_report,
        temporal_meta=temporal_contract,
        tensor_meta=tensor_meta,
        provenance={"source": stage3_path, "stage": "stage4"},
    )

    # --------------------------------------------------------------------------
    # 10. SAVE OUTPUTS
    # --------------------------------------------------------------------------
    ds_clean.to_netcdf(out_dataset)

    with open(out_qc, "wb") as f:
        pickle.dump(qc_report, f)

    with open(out_meta, "wb") as f:
        pickle.dump(stage4_metadata, f)

    print("[Stage 4] Complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    run_stage4(config=cfg)
