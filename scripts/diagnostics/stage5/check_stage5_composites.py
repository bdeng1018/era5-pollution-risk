#!/usr/bin/env python3
"""
Stage 05 Diagnostics — Composite Features

Validates:
- presence of composite features
- formula consistency (all referenced features exist)
- null counts
"""

import json
import logging
from pathlib import Path

import xarray as xr

from src.features_05.registry import load_registry

logger = logging.getLogger(__name__)


def check_composites(features_path: str, cfg: dict) -> dict:
    ds = xr.open_dataset(features_path)
    registry = load_registry(cfg)

    expected = set(registry["composite"])
    present = {v for v in ds.data_vars if v in expected}

    missing = sorted(expected - present)
    extra = sorted(present - expected)

    # Validate formulas reference existing features
    formula_issues = {}
    for name, spec in cfg["composites"].items():
        refs = set(spec["temporal"] + spec["spatial"])
        missing_refs = sorted([r for r in refs if r not in ds.data_vars])
        if missing_refs:
            formula_issues[name] = missing_refs

    null_counts = {v: int(ds[v].isnull().sum()) for v in present}

    return {
        "expected_composites": sorted(expected),
        "present_composites": sorted(present),
        "missing_composites": missing,
        "extra_composites": extra,
        "formula_missing_references": formula_issues,
        "null_counts": null_counts,
    }


def main():
    import argparse

    from src.utils.config import load_yaml
    from src.utils.paths import get_path

    parser = argparse.ArgumentParser(description="Stage 05 Composite Diagnostics")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    features_path = get_path(cfg, "paths.output")

    report = check_composites(features_path, cfg)

    out = Path("diagnostics_stage5_composites.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
