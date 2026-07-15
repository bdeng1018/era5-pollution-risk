"""
Stage 2 Health Diagnostic Suite (Directory-First Sampling + Parallel)

This diagnostic is optimized for extremely large Stage 2 datasets
(e.g., 500k–1M parquet files). It avoids scanning the entire directory tree,
which is slow on macOS APFS, and instead samples directories first.

Key Improvements
----------------
1. **Avoid full directory scan**:
   - Instead of scanning 600k+ parquet files, we first list top-level
     variable/month directories (usually ~100–200).
   - Then we sample directories and only scan inside them.

2. **Optional sampling**:
   - If --pct is omitted → full scan *within sampled directories*.
   - If --pct is provided → sample N% of files inside sampled directories.

3. **Optional parallel scanning**:
   - Uses multiprocessing to accelerate parquet checks.

4. **Strong validation**:
   - Parquet readability
   - Required coordinate columns
   - Variable column presence
   - File size anomalies
   - metadata.json consistency
   - Timestamp → parquet alignment

Usage
-----
    python check_stage2_health.py
        → full scan (directory-first, fast)

    python check_stage2_health.py --pct 5
        → sample 5% of files inside sampled directories

    python check_stage2_health.py --pct 5 --parallel
        → sample 5% + parallel scanning

Arguments
---------
--pct N        Optional. Sample N% of parquet files (0.01–99.99).
--parallel     Optional. Enable multiprocessing.
"""

from __future__ import annotations

import argparse
import json
import random
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

import pandas as pd

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

INTERMEDIATE_ROOT = Path("data/intermediate")
METADATA_PATH = Path("data/metadata/metadata.json")

REQUIRED_COORDS = {"latitude", "longitude", "valid_time"}


# ------------------------------------------------------------------------------
# Directory-First Sampling
# ------------------------------------------------------------------------------

def list_stage2_directories(root: Path) -> List[Path]:
    dirs = []
    for year_dir in root.iterdir():
        if not year_dir.is_dir():
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue
            for var_dir in month_dir.iterdir():
                if var_dir.is_dir():
                    dirs.append(var_dir)
    return dirs


def sample_directories(dirs: List[Path], pct: float) -> List[Path]:
    n = max(1, int(len(dirs) * (pct / 100.0)))
    return random.sample(dirs, n)


def list_parquet_in_dirs(dirs: List[Path]) -> List[Path]:
    files = []
    for d in dirs:
        files.extend(d.glob("*.parquet"))
    return files


def sample_files(files: List[Path], pct: float) -> List[Path]:
    n = max(1, int(len(files) * (pct / 100.0)))
    return random.sample(files, n)


# ------------------------------------------------------------------------------
# Parquet Checks
# ------------------------------------------------------------------------------

def read_parquet_safe(path: Path) -> Optional[pd.DataFrame]:
    try:
        return pd.read_parquet(path)
    except Exception:
        return None


def check_required_columns(df: pd.DataFrame) -> Set[str]:
    missing = set()

    for col in ["latitude", "longitude"]:
        if col not in df.columns:
            missing.add(col)

    if ("time" not in df.columns) and ("valid_time" not in df.columns):
        missing.add("valid_time")

    return missing


def detect_variable_columns(df: pd.DataFrame) -> Set[str]:
    ignore = {"latitude", "longitude", "time", "valid_time", "number", "step", "surface"}
    return set(df.columns) - ignore


def diagnose_single_file(path: Path) -> Optional[Tuple[Path, str]]:
    df = read_parquet_safe(path)
    if df is None:
        return (path, "Unreadable parquet file")

    if df.shape[0] == 0:
        return (path, "Empty parquet file (0 rows)")

    missing = check_required_columns(df)
    if missing:
        return (path, f"Missing required columns: {missing}")

    vars_found = detect_variable_columns(df)
    if len(vars_found) == 0:
        return (path, "No variable column detected")

    if path.stat().st_size < 1024:
        return (path, "Suspiciously small file (<1 KB)")

    return None


# ------------------------------------------------------------------------------
# Metadata Checks (Key‑Indexed Schema)
# ------------------------------------------------------------------------------

def load_metadata() -> Optional[Dict]:
    if not METADATA_PATH.exists():
        return None
    try:
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return None


def parse_metadata_key(key: str) -> Tuple[str, str]:
    if "::" not in key:
        raise ValueError(f"Malformed metadata key: {key}")
    ts, var = key.split("::", 1)
    return ts, var


def diagnose_metadata_consistency() -> List[str]:
    issues = []
    metadata = load_metadata()
    if metadata is None:
        return ["metadata.json missing or unreadable"]

    for key, entry in metadata.items():
        try:
            ts, var = parse_metadata_key(key)
        except ValueError as e:
            issues.append(str(e))
            continue

        required = ["timestamp", "variable", "path"]
        missing = [f for f in required if f not in entry]
        if missing:
            issues.append(f"Entry {key} missing fields: {missing}")

        path = entry.get("path")
        if not Path(path).exists():
            issues.append(f"Metadata references missing parquet file: {path}")

        else:
            try:
                pd.read_parquet(path)
            except Exception:
                issues.append(f"Unreadable parquet file: {path}")

    return issues


def diagnose_timestamp_alignment() -> List[str]:
    issues = []
    metadata = load_metadata()
    if metadata is None:
        return ["metadata.json missing or unreadable"]

    timestamps = []
    for key in metadata.keys():
        try:
            ts, var = parse_metadata_key(key)
            timestamps.append(ts)
        except ValueError as e:
            issues.append(str(e))

    if timestamps != sorted(timestamps):
        issues.append("Timestamps not sorted")

    if len(timestamps) != len(set(timestamps)):
        issues.append("Duplicate timestamps detected")

    return issues


# ------------------------------------------------------------------------------
# Parallel Diagnostic
# ------------------------------------------------------------------------------

def parallel_diagnose(paths: List[Path]) -> List[Tuple[Path, str]]:
    with Pool(cpu_count()) as pool:
        results = pool.map(diagnose_single_file, paths)
    return [r for r in results if r is not None]


# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pct", type=float, default=None,
                        help="Optional: sample N% of parquet files (0.01–99.99).")
    parser.add_argument("--parallel", action="store_true",
                        help="Enable parallel scanning")
    args = parser.parse_args()

    print("=== Stage 2 Health Diagnostic (Key‑Indexed Metadata Schema) ===\n")

    dirs = list_stage2_directories(INTERMEDIATE_ROOT)
    print(f"Stage 2 directories: {len(dirs)}")

    if args.pct is None:
        sampled_dirs = dirs
        print("Directory sampling: none\n")
    else:
        if not (0.01 <= args.pct <= 99.99):
            print("❌ --pct must be between 0.01 and 99.99")
            return
        sampled_dirs = sample_directories(dirs, args.pct)
        print(f"Directory sampling {args.pct}% → {len(sampled_dirs)} directories\n")

    files = list_parquet_in_dirs(sampled_dirs)
    print(f"Parquet files in sampled directories: {len(files)}")

    if args.pct is None:
        sampled_files = files
        print("File sampling: none\n")
    else:
        sampled_files = sample_files(files, args.pct)
        print(f"File sampling {args.pct}% → {len(sampled_files)} files\n")

    if args.parallel:
        print("Running parallel diagnostic...\n")
        parquet_issues = parallel_diagnose(sampled_files)
    else:
        print("Running single-threaded diagnostic...\n")
        parquet_issues = [r for r in map(diagnose_single_file, sampled_files) if r is not None]

    metadata_issues = diagnose_metadata_consistency()
    timestamp_issues = diagnose_timestamp_alignment()

    if not parquet_issues and not metadata_issues and not timestamp_issues:
        print("✅ Stage 2 is healthy. No issues detected.")
        return

    print("❌ Issues detected:\n")

    if parquet_issues:
        print("Parquet File Issues:")
        for path, issue in parquet_issues:
            print(f"  - {path}: {issue}")
        print()

    if metadata_issues:
        print("Metadata Issues:")
        for issue in metadata_issues:
            print(f"  - {issue}")
        print()

    if timestamp_issues:
        print("Timestamp Alignment Issues:")
        for issue in timestamp_issues:
            print(f"  - {issue}")
        print()


if __name__ == "__main__":
    main()
