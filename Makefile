# ==============================================================================
# ERA5 Pollution Risk Pipeline — Branch 2
# Makefile for running pipeline stages in correct sequence.
#
# IMPORTANT — CDS API Credentials (required for Stage 01)
# ------------------------------------------------------------------------------
# ERA5 downloads require valid CDS API credentials stored in shell environment:
#
#   export CDSAPI_URL="https://cds.climate.copernicus.eu/api"
#   export CDSAPI_KEY="<your-key-here>"
#
# Add these lines to ~/.zshrc (macOS default) or ~/.bashrc if using bash.
# Reload your shell:
#
#   source ~/.zshrc
#
# Verify:
#
#   echo $$CDSAPI_URL
#   echo $$CDSAPI_KEY
#
# Without these variables, Stage 01 (download) will fail.
#
# Branch 2 status:
#   ✓ Stage 1 (Download) complete
#   ✓ Stage 1 metadata + retry logic complete
#   ✓ Stage 1 test suite complete
#   ✓ Stage 2 unzip/inspect/convert modules complete
#   ✓ Stage 2 test suite complete
#   ✓ Stage 3 chunked core processing modules complete
#   → Stage 3 orchestration via ChunkOrchestrator
# ==============================================================================

.PHONY: env download preprocess core features train evaluate test all clean-cache clean-pyc

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
	python -m src.preprocessing_02.run_preprocessing --config configs/config.yml

# ------------------------------------------------------------------------------
# Stage 03 — Chunked Core Processing (Branch 2)
# ------------------------------------------------------------------------------
core: preprocess
	python -m src.core_03.chunk_orchestrator --config configs/config.yml

# ------------------------------------------------------------------------------
# Stage 04 — Feature Engineering (Branch 1 baseline)
# ------------------------------------------------------------------------------
features: core
	python -m src.features_03.build_features

# ------------------------------------------------------------------------------
# Stage 05 — Modeling (Branch 1 baseline)
# ------------------------------------------------------------------------------
train: features
	python -m src.modeling_04.train_model

# ------------------------------------------------------------------------------
# Stage 06 — Evaluation (Branch 1 baseline)
# ------------------------------------------------------------------------------
evaluate: train
	python -m src.evaluation_05.evaluate_model

# ------------------------------------------------------------------------------
# Run all tests (Branch 2)
# ------------------------------------------------------------------------------
test:
	pytest -q

# ------------------------------------------------------------------------------
# Full pipeline (Stages 01 → 06)
# ------------------------------------------------------------------------------
all: download preprocess core features train evaluate

# ------------------------------------------------------------------------------
# Branch 2 only (Stages 01 → 03)
# ------------------------------------------------------------------------------
branch2:
	make download
	make preprocess
	make core

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
