"""
Stage 2 Acceptance Test — Branch 2

Acceptance tests validate that the Stage 2 preprocessing pipeline produces
the correct high‑level outputs when executed end‑to‑end. Unlike system tests,
which only check that the pipeline *runs*, acceptance tests check that the
pipeline produces the expected directory structure and output artifacts.

Covered:
- run_preprocessing.main() completes without crashing
- expected Stage 2 output directories exist (raw, intermediate, logs, metadata)
- pipeline creates or touches expected Stage 2 artifacts
- pipeline initializes logging and metadata structures

Not covered (handled in regression tests):
- correctness of GRIB → Parquet conversion
- correctness of .idx metadata
- schema validation
- multi-variable ingestion correctness
- retry logic correctness
- performance characteristics
"""

import importlib
import os


def test_stage2_acceptance_pipeline_outputs(tmp_path, monkeypatch):
    """
    Acceptance test: ensure run_preprocessing.main() produces the expected
    directory structure and high‑level artifacts.

    This test uses a temporary directory to avoid touching real data.
    No GRIB files are opened and no Parquet files are written.
    """
    # Patch environment variables so Stage 2 writes into tmp_path
    monkeypatch.setenv("ERA5_BASE_DIR", str(tmp_path))

    rp = importlib.import_module("src.preprocessing_02.run_preprocessing")
    Paths = importlib.import_module("src.utils.paths").Paths

    # Run the pipeline (expected to short‑circuit gracefully with no real data)
    try:
        rp.main()
    except Exception as exc:
        raise AssertionError(
            f"Acceptance-level execution of run_preprocessing.main() failed: {exc}"
        )

    # Validate directory structure
    p = Paths()

    expected_dirs = [
        p.raw_dir,
        p.intermediate_dir,
        p.logs_dir,
        p.metadata_dir,
    ]

    for d in expected_dirs:
        assert os.path.isdir(d), f"Expected directory missing in acceptance test: {d}"

    # Validate logging file existence (Stage 2 guarantee)
    log_files = [f for f in os.listdir(p.logs_dir) if f.endswith(".log")]
    assert log_files, "Stage 2 acceptance test: no log files created by pipeline"

    # Validate logging content (startup banner or stage2 prefix)
    log_path = os.path.join(p.logs_dir, log_files[0])
    with open(log_path, "r") as lf:
        content = lf.read()
    assert "[stage2]" in content or "run_preprocessing" in content, (
        "Stage 2 acceptance test: log file missing expected startup content"
    )

    # Validate metadata directory contains metadata.json
    metadata_file = os.path.join(p.metadata_dir, "metadata.json")
    assert os.path.isfile(metadata_file), (
        "Stage 2 acceptance test: metadata.json missing from metadata directory"
    )

    # Validate metadata.json is at least initialized (non-empty file)
    assert os.path.getsize(metadata_file) > 0, (
        "Stage 2 acceptance test: metadata.json is empty"
    )
