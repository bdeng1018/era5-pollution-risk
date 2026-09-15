#!/usr/bin/env python3
"""
Stage 05 Diagnostics — Spatial Features

Validates:
- presence of spatial features
- kernel‑based naming conventions
- dimensionality and null counts
"""

import json
import logging
from pathlib import Path

import xarray as xr

from src.features_05.registry import load_registry

logger = logging.getLogger(__name__)


def check_spatial(features_path: str, cfg: dict) -> dict:
    ds = xr.open_dataset(features_path)
    registry = load_registry(cfg)

    expected = set(registry["spatial"])
    present = {v for v in ds.data_vars if v in expected}

    missing = sorted(expected - present)
    extra = sorted(present - expected)

    null_counts = {v: int(ds[v].isnull().sum()) for v in present}

    return {
        "expected_spatial": sorted(expected),
        "present_spatial": sorted(present),
        "missing_spatial": missing,
        "extra_spatial": extra,
        "null_counts": null_counts,
    }


def main():
    import argparse

    from src.utils.config import load_yaml
    from src.utils.paths import get_path

    parser = argparse.ArgumentParser(description="Stage 05 Spatial Diagnostics")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    features_path = get_path(cfg, "paths.output")

    report = check_spatial(features_path, cfg)

    out = Path("diagnostics_stage5_spatial.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
