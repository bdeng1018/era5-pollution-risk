#!/usr/bin/env python3
"""
Stage 05 Diagnostics — Feature Integrity

Validates:
- all IR5 features exist
- no unexpected variables
- dataset shape consistency
"""

import json
from pathlib import Path

import xarray as xr

from src.features_05.registry import load_registry


def check_integrity(features_path: str, cfg: dict) -> dict:
    ds = xr.open_dataset(features_path)
    registry = load_registry(cfg)

    expected = (
        set(registry["temporal"])
        | set(registry["spatial"])
        | set(registry["composite"])
    )
    present = set(ds.data_vars)

    missing = sorted(expected - present)
    extra = sorted(present - expected)

    dims = {v: list(ds[v].dims) for v in present}

    return {
        "expected_features": sorted(expected),
        "present_features": sorted(present),
        "missing_features": missing,
        "extra_features": extra,
        "dimensions": dims,
    }


def main():
    import argparse

    from src.utils.config import load_yaml
    from src.utils.paths import get_path

    parser = argparse.ArgumentParser(
        description="Stage 05 Feature Integrity Diagnostics"
    )
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    features_path = get_path(cfg, "paths.output")

    report = check_integrity(features_path, cfg)

    out = Path("diagnostics_stage5_feature_integrity.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
