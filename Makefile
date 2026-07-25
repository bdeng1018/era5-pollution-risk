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
#   echo $$CDSAPI_URL
#   echo $$CDSAPI_KEY
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

PYTHON := python

# ==============================================================================
# Help — Self‑Documenting Makefile (Regex-Based)
# ==============================================================================
.PHONY: help

help:
	@echo ""
	@echo "ERA5 Pollution Risk Pipeline — Branch 2"
	@echo "----------------------------------------"
	@echo "Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | sed 's/:.*##/: /' | sort
	@echo ""

# ==============================================================================
# Stage 00 — Environment Validation
# ==============================================================================
.PHONY: env
env: ## Validate environment and required tools
	$(PYTHON) -m src.utils.env_check

# ==============================================================================
# Stage 01 — ERA5 Download (GRIB)
# ==============================================================================
.PHONY: stage01 download
stage01: download ## Run Stage 01 (ERA5 GRIB download)
	@echo "Stage 01 complete."

download: ## Download monthly ERA5 GRIB files
	$(PYTHON) -m src.download_01.download_era5_monthly --config configs/config.yml

# ==============================================================================
# Stage 02 — Preprocessing
# ==============================================================================
.PHONY: stage02 preprocess
stage02: preprocess ## Run Stage 02 (unzip → inspect → convert → metadata)
	@echo "Stage 02 complete."

preprocess: ## Run preprocessing pipeline
	make clean-idx
	make clean-cache
	$(PYTHON) -m src.preprocessing_02.run_preprocessing --config configs/config.yml
	make clean-idx
	make clean-cache

# ==============================================================================
# Stage 03 — Chunked Core Processing
# ==============================================================================
.PHONY: stage03 core
stage03: core ## Run Stage 03 (chunk planner → orchestrator → worker → merge)
	@echo "Stage 03 complete."

core: ## Execute chunked core processing
	make clean-cache
	$(PYTHON) -m src.core_03 --config configs/config.yml

# ==============================================================================
# Stage 04 — Spatiotemporal Compiler
# ==============================================================================
.PHONY: stage04 spatiotemporal
stage04: spatiotemporal ## Run Stage 04 (spatiotemporal compiler)
	@echo "Stage 04 complete."

spatiotemporal: ## Execute spatiotemporal compiler driver
	$(PYTHON) -m src.spatiotemporal_04.driver --config configs/config.yml

# ==============================================================================
# Stage 05 — Feature Engineering (Placeholder)
# ==============================================================================
.PHONY: stage05 features
stage05: features ## Run Stage 05 (feature engineering)
	@echo "Stage 05 complete."

features: ## Stage 5 not yet implemented
	@echo "Stage 5 (features) is not yet implemented in Branch 2."

# ==============================================================================
# Stage 06 — Modeling (Placeholder)
# ==============================================================================
.PHONY: stage06 train
stage06: train ## Run Stage 06 (modeling)
	@echo "Stage 06 complete."

train: ## Stage 6 not yet implemented
	@echo "Stage 6 (modeling) is not yet implemented in Branch 2."

# ==============================================================================
# Stage 07 — Evaluation (Placeholder)
# ==============================================================================
.PHONY: stage07 evaluate
stage07: evaluate ## Run Stage 07 (evaluation)
	@echo "Stage 07 complete."

evaluate: ## Stage 7 not yet implemented
	@echo "Stage 7 (evaluation) is not yet implemented in Branch 2."

# ==============================================================================
# Stage 08 — Deployment (Placeholder)
# ==============================================================================
.PHONY: stage08 deploy
stage08: deploy ## Run Stage 08 (deployment)
	@echo "Stage 08 complete."

deploy: ## Stage 8 reserved for Branch 3
	@echo "Stage 8 (deployment) reserved for Branch 3."

# ==============================================================================
# Testing
# ==============================================================================
.PHONY: test
test: ## Run test suite
	pytest -q

# ==============================================================================
# Linting & Formatting
# ==============================================================================
.PHONY: lint format
lint: ## Lint all relevant directories with Ruff
	ruff check --fix src tests scripts configs models docs diagrams Makefile

format: ## Format Python code (Black → Ruff)
	black src tests scripts models
	ruff format src tests scripts models

# ==============================================================================
# Full Pipeline — Stages 01–04
# ==============================================================================
.PHONY: run all
run: stage01 stage02 stage03 stage04 ## Run full pipeline (Stages 01–04)
	@echo "Full pipeline (Stages 01–04) complete."

all: run ## Alias for full pipeline

# ==============================================================================
# Cleanup
# ==============================================================================
.PHONY: clean-cache clean-pyc clean-idx clean-intermediate \
		clean-stage1 clean-stage2 clean-stage3 clean-stage4 \
		reset-soft

clean-cache: ## Remove caches (__pycache__, pytest, ruff)
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/

clean-pyc: ## Remove Python bytecode
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

clean-idx: ## Remove GRIB index files
	find data/raw/era5 -name "*.idx" -delete

clean-intermediate: clean-cache clean-pyc clean-idx ## Remove intermediate artifacts
	rm -rf data/intermediate/*
	rm -rf data/chunks/*
	rm -rf data/chunks_metadata/*
	rm -rf data/spatiotemporal/*
	rm -rf data/features/*
	rm -rf data/logs/*
	rm -rf data/metadata/*
	rm -rf data/predictions/*

clean-stage1: ## Remove Stage 01 artifacts
	rm -rf data/raw/era5/*/*.idx

clean-stage2: ## Remove Stage 02 artifacts
	rm -rf data/intermediate/*

clean-stage3: ## Remove Stage 03 artifacts
	rm -rf data/chunks/* data/chunks_metadata/*

clean-stage4: ## Remove Stage 04 artifacts
	rm -rf data/spatiotemporal/*

reset-soft: clean-intermediate ## Soft reset (preserve raw GRIB)
	@echo "Soft reset complete (raw GRIB preserved)."
