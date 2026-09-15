"""
Stage 05 — CLI Entrypoint (IR5 Orchestration)
=============================================

This module provides the command‑line interface for Stage 05. It simply
parses arguments and delegates execution to the Stage 05 driver.

Architecture Notes
------------------
- This file must remain minimal and import‑safe.
- All heavy logic lives in driver.py.
- This mirrors Stage 02 and Stage 04 entrypoints.
- Deterministic, side‑effect‑free imports are required for pytest collection.

Usage
-----
    python -m src.features_05 --config configs/stage5.yml

This triggers the full IR5 feature pipeline:
    IR4 tensor → temporal → spatial → composite → metadata → QC → registry → IR5 output
"""

from __future__ import annotations

import argparse
import logging

from src.utils.config import load_yaml

from .driver import run_stage05

logger = logging.getLogger(__name__)


def main() -> None:
    """
    CLI entrypoint for Stage 05.

    Notes
    -----
    - Uses load_yaml() instead of load_config() because Stage 05 is
      config‑driven and must load stage5.yml explicitly.
    - Delegates all orchestration to run_stage05().
    """
    parser = argparse.ArgumentParser(description="Stage 05 Feature Pipeline (IR5)")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to stage5.yml (e.g., configs/stage5.yml)",
    )
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    run_stage05(cfg)


if __name__ == "__main__":
    main()
