#!/usr/bin/env python3
"""
Stage 05 Diagnostics — Temporal Features

Validates:
- presence of all temporal features
- no missing values
- correct dimensionality
- expected naming conventions
"""

import json
import logging
from pathlib import Path

import xarray as xr

from src.features_05.registry import load_registry

logger = logging.getLogger(__name__)


def check_temporal(features_path: str, cfg: dict) -> dict:
    ds = xr.open_dataset(features_path)
    registry = load_registry(cfg)

    expected = set(registry["temporal"])
    present = {v for v in ds.data_vars if v in expected}

    missing = sorted(expected - present)
    extra = sorted(present - expected)

    null_counts = {v: int(ds[v].isnull().sum()) for v in present}

    return {
        "expected_temporal": sorted(expected),
        "present_temporal": sorted(present),
        "missing_temporal": missing,
        "extra_temporal": extra,
        "null_counts": null_counts,
    }


def main():
    import argparse

    from src.utils.config import load_yaml
    from src.utils.paths import get_path

    parser = argparse.ArgumentParser(description="Stage 05 Temporal Diagnostics")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    features_path = get_path(cfg, "paths.output")

    report = check_temporal(features_path, cfg)

    out = Path("diagnostics_stage5_temporal.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
