"""
Stage 4 Diagnostic — Integration Check (ERA5‑Correct, Stage 4‑Ready)
====================================================================

Purpose
-------
Aggregate all Stage 4 diagnostic reports into a single integration report.
Validates the entire Stage 4 compiler pipeline:

    grid → mask → temporal_align → temporal_interpolate → tensor_builder → qc

This diagnostic ensures:
    • All Stage 4 invariants executed successfully
    • All diagnostic reports exist and are readable
    • All invariants passed (or failed with clear reasons)
    • A single integration pass/fail flag is produced

Output:
    data/spatiotemporal/stage4_integration_report.json
"""

import json
from pathlib import Path

# ------------------------------------------------------------------------------
# Helper: load JSON diagnostic report
# ------------------------------------------------------------------------------


def _load_report(path: Path) -> dict:
    if not path.exists():
        return {"error": f"Missing diagnostic report: {path}"}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load {path}: {e}"}


# ------------------------------------------------------------------------------
# Integration diagnostic entry point
# ------------------------------------------------------------------------------


def run_stage4_integration_diagnostic(base_dir: str, output_path: str) -> None:
    """
    Run Stage 4 integration diagnostic.

    Parameters
    ----------
    base_dir : str
        Directory containing Stage 4 diagnostic reports.
    output_path : str
        Path to write integration JSON report.
    """

    print("[Stage 4][integration_diag] Running Stage 4 integration diagnostic")

    report_dir = Path(base_dir)

    # Correct Stage 4 diagnostic filenames
    paths = {
        "grid": report_dir / "stage4_grid_report.json",
        "mask": report_dir / "stage4_mask_report.json",
        "temporal_alignment": report_dir / "stage4_temporal_alignment_report.json",
        "temporal_interpolation": report_dir
        / "stage4_temporal_interpolation_report.json",
        "tensor_builder": report_dir / "stage4_tensor_builder_report.json",
        "qc": report_dir / "stage4_qc_report.json",
    }

    # Load all reports
    reports = {name: _load_report(path) for name, path in paths.items()}

    # Determine pass/fail for each invariant
    invariant_pass = {
        "grid": reports["grid"].get("grid_pass", False),
        "mask": reports["mask"].get("mask_pass", False),
        "temporal_alignment": reports["temporal_alignment"].get("temporal_pass", False),
        "temporal_interpolation": reports["temporal_interpolation"].get(
            "interp_pass", False
        ),
        "tensor_builder": reports["tensor_builder"].get("tensor_pass", False),
        "qc": reports["qc"].get("qc_pass", False),
    }

    # Integration pass criteria
    integration_pass = all(invariant_pass.values())

    # Build integration report
    integration_report = {
        "invariant_pass": invariant_pass,
        "integration_pass": integration_pass,
        "reports": reports,
    }

    # --------------------------------------------------------------------------
    # Save report
    # --------------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(integration_report, f, indent=2)

    print("[Stage 4][integration_diag] Report saved:", out_path)
    print("[Stage 4][integration_diag] integration_pass:", integration_pass)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 4 Integration Diagnostic")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to Stage 4 dataset (unused; Stage 4 diagnostics are metadata-based)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to write diagnostic JSON report",
    )

    args = parser.parse_args()

    run_stage4_integration_diagnostic(args.dataset, args.output)
