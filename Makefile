# ==============================================================================
# ERA5 Pollution Risk Pipeline — Branch 2
# Makefile for running pipeline stages in correct sequence.
#
# CDS API Credentials (Required for Stage 1)
# ------------------------------------------------------------------------------
# ERA5 downloads require valid CDS API credentials exported in your shell:
#
#   export CDSAPI_URL="https://cds.climate.copernicus.eu/api"
#   export CDSAPI_KEY="<your-key-here>"
#
# Add these lines to ~/.zshrc (macOS) or ~/.bashrc (bash), then reload:
#
#   source ~/.zshrc
#
# Verify credentials:
#
#   echo $CDSAPI_URL
#   echo $CDSAPI_KEY
#
# Without these variables, Stage 1 (download) will fail immediately.
#
# Branch 2 Status Summary
# ------------------------------------------------------------------------------
#   ✓ Stage 1: GRIB-only ERA5 download (monthly + single-variable)
#   ✓ Stage 1: Metadata, retry logic, and full test suite
#
#   ✓ Stage 2: unzip / inspect / convert modules complete
#   ✓ Stage 2: Full test suite and pipeline orchestration
#
#   ✓ Stage 3: Chunked core processing modules complete
#   ✓ Stage 3: Orchestration via ChunkOrchestrator
#
#   ✓ Stage 4: Spatiotemporal compiler implemented
#       (grid → mask → temporal_align → temporal_interpolate → qc → metadata → tensor_builder)
#
#   (Stage 5: Feature engineering — planned)
#   (Stage 6: Dataset assembly + modeling — planned)
#   (Stage 7: Evaluation + inference — planned)
#   (Stage 8: Deployment — reserved for Branch 3)
#
# Notes
# ------------------------------------------------------------------------------
# - This Makefile provides a clean, reproducible interface for running each
#   pipeline stage individually or end-to-end.
# - Targets are intentionally simple and shell-friendly.
# - Branch 3 will introduce deployment targets (docker, fastapi, mlflow).
# ==============================================================================

.PHONY: env download preprocess core spatiotemporal features train evaluate test all clean-cache clean-pyc clean-idx clean-intermediate

# ------------------------------------------------------------------------------
# Stage 00 — Environment validation
# ------------------------------------------------------------------------------
env:
	python -m src.utils.env_check

# ------------------------------------------------------------------------------
# Stage 01 — Download ERA5 data (Branch 2)
# ------------------------------------------------------------------------------
download: env
	python -m src.download_01.download_era5_monthly --config configs/config.yml

# ------------------------------------------------------------------------------
# Stage 02 — Preprocessing (Branch 2)
# ------------------------------------------------------------------------------
preprocess: download
    # Clean stale eccodes index files BEFORE preprocessing
	make clean-idx

    # Clean Python caches BEFORE Stage 2
	make clean-cache

	python -m src.preprocessing_02.run_preprocessing --config configs/config.yml

    # Clean stale eccodes index files AFTER preprocessing
	make clean-idx

    # Clean Python caches AFTER Stage 2
	make clean-cache

# ------------------------------------------------------------------------------
# Stage 03 — Chunked Core Processing (Branch 2)
# ------------------------------------------------------------------------------
core: preprocess
    # Clear caches BEFORE Stage 3 (double safety)
	make clean-cache

	python -m src.core_03 --config configs/config.yml

# ------------------------------------------------------------------------------
# Stage 04 — Spatiotemporal Compiler (Branch 2)
# Note: Stage 4 is pure library code; no cache cleanup required.
# ------------------------------------------------------------------------------
spatiotemporal: core
	python -m src.spatiotemporal_04.driver --config configs/config.yml

# ------------------------------------------------------------------------------
# Stage 05 — Features (Branch 2 -- NOT Implemented Yet)
# ------------------------------------------------------------------------------
features:
	@echo "Stage 5 features is not yet implemented in Branch 2."

# ------------------------------------------------------------------------------
# Stage 06 — Modeling (Branch 2 -- NOT Implemented Yet)
# ------------------------------------------------------------------------------
train:
	@echo "Stage 6 modeling is not yet implemented in Branch 2."

# ------------------------------------------------------------------------------
# Stage 07 — Evaluation (Branch 2 -- NOT Implemented Yet)
# ------------------------------------------------------------------------------
evaluate:
	@echo "Stage 7 evaluation is not yet implemented in Branch 2."

# ------------------------------------------------------------------------------
# Run all tests (Branch 2)
# ------------------------------------------------------------------------------
test:
	pytest -q

# ------------------------------------------------------------------------------
# Full pipeline (Stages 01 → 07)
# ------------------------------------------------------------------------------
all: download preprocess core spatiotemporal
	@echo "Stages 5–7 are not yet implemented in Branch 2."

# ------------------------------------------------------------------------------
# Clean Python caches (pyc + __pycache__ + pytest cache)
# ------------------------------------------------------------------------------
clean-cache:
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache/

# ------------------------------------------------------------------------------
# Clean only Python bytecode caches
# ------------------------------------------------------------------------------
clean-pyc:
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

# ------------------------------------------------------------------------------
# Manual cleanup of stale eccodes index files
# ------------------------------------------------------------------------------
clean-idx:
	find data/raw/era5 -name "*.idx" -delete

# ------------------------------------------------------------------------------
# Clean intermediate data (intermediate, chunks, chunks_metadata, spatiotemporal)
# ------------------------------------------------------------------------------
clean-intermediate: clean-cache clean-pyc clean-idx
	rm -rf data/intermediate/*
	rm -rf data/chunks/*.parquet
	rm -rf data/chunks_metadata/*.json
	rm -rf data/spatiotemporal/*
