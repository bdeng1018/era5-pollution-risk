#!/usr/bin/env bash
# ==============================================================================
# ERA5 Pollution‑Risk Pipeline — Branch 1 (v1.0.0)
# ==============================================================================
# Container Entrypoint Script
#
# This entrypoint provides a deterministic interface for running the ERA5
# Branch 1 pipeline inside Docker. It mirrors CMS deployment conventions:
#
#   - environment validation on startup
#   - Makefile-driven execution
#   - minimal ingestion (Branch 1)
#   - fast smoke-testing
#   - deterministic artifact generation
#
# Branch 1 intentionally avoids:
#   - full CDS ingestion logic
#   - schema/metadata validation
#   - multi-variable ingestion
#   - GRIB/Parquet correctness checks
#   - skip-logic correctness
#
# Branch 2 will introduce full ingestion validation, fixtures, schema checks,
# metadata extraction, skip-logic correctness, and multi-variable ingestion.
# ==============================================================================

set -e

echo "=============================================================="
echo " ERA5 Pollution‑Risk Pipeline — Branch 1 (v1.0.0)"
echo " Container Entrypoint"
echo "=============================================================="
echo ""

# ==============================================================================
# Validate environment
# ==============================================================================
echo "[1/4] Validating environment..."
make env
echo ""

# ==============================================================================
# If no arguments provided, run full pipeline
# ==============================================================================
if [ $# -eq 0 ]; then
    echo "[2/4] No arguments provided — running full pipeline (make all)..."
    make all
    echo ""
    echo "[3/4] Pipeline execution complete."
    echo ""
    echo "[4/4] Entrypoint finished."
    exit 0
fi

# ==============================================================================
# If arguments provided, treat them as Makefile targets
# ==============================================================================
echo "[2/4] Running custom Makefile target: $@"
make "$@"
echo ""
echo "[3/4] Custom target execution complete."
echo ""
echo "[4/4] Entrypoint finished."
