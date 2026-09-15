#!/usr/bin/env python3
"""
Stage 05 Diagnostics — Metadata

Validates:
- metadata completeness
- expected keys
- IR5 version alignment
"""

import json
from pathlib import Path


def check_metadata(metadata_path: str, cfg: dict) -> dict:
    metadata = json.loads(Path(metadata_path).read_text())

    expected_keys = ["temporal", "spatial", "composite", "ir4_version"]
    missing = [k for k in expected_keys if k not in metadata]

    version_ok = metadata.get("ir4_version") == cfg["ir4"]["version"]

    return {
        "expected_keys": expected_keys,
        "missing_keys": missing,
        "version_matches": version_ok,
        "metadata_summary": metadata,
    }


def main():
    import argparse

    from src.utils.config import load_yaml
    from src.utils.paths import get_path

    parser = argparse.ArgumentParser(description="Stage 05 Metadata Diagnostics")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    metadata_path = get_path(cfg, "paths.metadata")

    report = check_metadata(metadata_path, cfg)

    out = Path("diagnostics_stage5_metadata.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
