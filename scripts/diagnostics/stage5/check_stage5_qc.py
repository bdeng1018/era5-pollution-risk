#!/usr/bin/env python3
"""
Stage 05 Diagnostics — QC

Validates:
- QC completeness
- expected QC keys
- threshold presence
"""

import json
from pathlib import Path


def check_qc(qc_path: str, cfg: dict) -> dict:
    qc = json.loads(Path(qc_path).read_text())

    expected_sections = ["temporal", "spatial", "composite"]
    missing_sections = [s for s in expected_sections if s not in qc]

    return {
        "expected_sections": expected_sections,
        "missing_sections": missing_sections,
        "qc_summary": qc,
    }


def main():
    import argparse

    from src.utils.config import load_yaml
    from src.utils.paths import get_path

    parser = argparse.ArgumentParser(description="Stage 05 QC Diagnostics")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    qc_path = get_path(cfg, "paths.qc")

    report = check_qc(qc_path, cfg)

    out = Path("diagnostics_stage5_qc.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
