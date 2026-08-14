# ==============================================================================
# ERA5 Pollution‑Risk Pipeline — Branch 1 (v1.0.0)
# ==============================================================================
# This Makefile provides a reproducible, stage‑driven interface for running the
# ERA5 Pollution‑Risk pipeline. Branch 1 focuses on minimal ingestion, fast
# smoke‑testing, and deterministic execution. No real GRIB/Parquet validation,
# skip‑logic correctness, or multi‑variable ingestion occurs in this branch.
#
# Pipeline Stages (Branch 1)
# --------------------------
#   00. Environment validation
#   01. ERA5 monthly download (mock‑friendly, minimal ingestion)
#   02. GRIB → Parquet preprocessing (no schema validation)
#   03. Feature engineering (no deterministic feature checks)
#   04. Baseline model training (MeanPredictor)
#   05. Evaluation + predictions (no artifact validation)
#
# Developer Ergonomics
# --------------------
#   - help:            discover available targets
#   - test:            run Branch 1 smoke tests
#   - format/lint:     CMS‑style code quality (Black + Ruff)
#   - diagnostics:     CDS API connectivity check
#   - clean-cache:     remove Python/pytest/ruff caches
#   - clean-all:       remove all pipeline artifacts (non-interactive)
#   - reset:           interactive artifact cleanup (safe)
#   - freeze:          freeze pip dependencies
#   - run:             alias for full pipeline execution
#
# Branch 1 Philosophy
# -------------------
# Keep everything fast, deterministic, and environment‑agnostic. Avoid:
#   - real CDS API ingestion logic
#   - schema/metadata validation
#   - multi‑variable ingestion
#   - GRIB/Parquet correctness checks
#   - skip‑logic correctness
#
# Environment Requirements
# ------------------------
# Use .venv for all pipeline runs. Do NOT activate Conda unless using GRIB CLI tools.
#
# Branch 2 will introduce full ingestion validation, fixtures, schema checks,
# metadata extraction, skip‑logic correctness, and multi‑variable ingestion.
# ==============================================================================

SHELL := /bin/bash
PYTHON := .venv/bin/python

# ==============================================================================
# Help
# ==============================================================================
help: ## Show available Makefile targets
	@echo ""
	@echo "ERA5 Pollution‑Risk Pipeline — Branch 1 (v1.0.0)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ==============================================================================
# Build / Environment
# ==============================================================================
build: ## Create .venv environment and install dependencies (Branch 1)
	rm -rf .venv
	python3 -m venv .venv --copies
	.venv/bin/pip install --upgrade pip
	@echo "Branch 1: no requirements.txt — using environment.yml only."
	@echo "Environment built."

conda-build: ## Build Conda environment (Docker parity)
	conda env create -f environment.yml -n era5
	@echo "Conda environment 'era5' created."

env: ## Validate Python environment, packages, and directory structure
	$(PYTHON) -m src.utils.env_check

# ==============================================================================
# Stage 01 — Download ERA5 data
# ==============================================================================
download: env ## Download ERA5 monthly GRIB files (Branch 1: minimal ingestion)
	$(PYTHON) -m src.download_01.download_era5_monthly

# ==============================================================================
# Stage 02 — Preprocessing (GRIB → Parquet)
# ==============================================================================
preprocess: env ## Unzip, inspect, and convert GRIB → Parquet (no schema validation)
	$(PYTHON) -m src.preprocessing_02.unzip_grib
	$(PYTHON) -m src.preprocessing_02.inspect_grib
	$(PYTHON) -m src.preprocessing_02.convert_grib_to_parquet

# ==============================================================================
# Stage 03 — Feature Engineering
# ==============================================================================
features: env ## Build ML‑ready features (Branch 1: no deterministic checks)
	$(PYTHON) -m src.features_03.build_features

# ==============================================================================
# Stage 04 — Modeling
# ==============================================================================
train: env ## Train baseline MeanPredictor model (Branch 1: minimal modeling)
	$(PYTHON) -m src.modeling_04.train_model

# ==============================================================================
# Stage 05 — Evaluation
# ==============================================================================
evaluate: env ## Evaluate model and generate predictions (Branch 1: no artifact validation)
	$(PYTHON) -m src.evaluation_05.evaluate_model

# ==============================================================================
# Full pipeline (Stages 01 → 05)
# ==============================================================================
all: download preprocess features train evaluate ## Run full ERA5 Branch 1 pipeline

run: ## Alias for full pipeline execution
	make all

# ==============================================================================
# Testing
# ==============================================================================
test: ## Run all Branch 1 smoke tests (imports + minimal execution)
	.venv/bin/pytest -q

# ==============================================================================
# Linting / Formatting (CMS‑style: Ruff + Black)
# ==============================================================================
format: ## Format code using Black + Ruff autofix
	.venv/bin/black src configs scripts
	.venv/bin/ruff check src configs scripts --fix

lint: ## Run Ruff linting across the repo (excluding notebooks)
	.venv/bin/ruff check src configs scripts

check: ## Run tests first, then lint (Branch 1 CI-style check)
	.venv/bin/pytest -q
	.venv/bin/ruff check src configs scripts

# ==============================================================================
# Diagnostics
# ==============================================================================
diagnostics: ## Run CDS API connectivity test (Branch 1: minimal external validation)
	$(PYTHON) scripts/diagnostics/test_cds.py

diagnostics-all: ## Run all diagnostics (env + CDS connectivity)
	make env
	make diagnostics

# ==============================================================================
# Freeze dependencies
# ==============================================================================
freeze: ## Freeze pip dependencies for reproducibility
	$(PYTHON) -m pip freeze > requirements-freeze.txt
	@echo "Frozen requirements written to requirements-freeze.txt"

# ==============================================================================
# Clean cache / temporary files
# ==============================================================================
clean-cache: ## Remove Python cache, pytest cache, ruff cache, and temp logs
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf data/logs/*
	rm -rf data/temp/*
	@echo "Cache cleaned."

# ==============================================================================
# Clean ALL pipeline artifacts (non-interactive)
# ==============================================================================
clean-all: ## Remove ALL pipeline artifacts (non-interactive)
	rm -rf data/intermediate/*
	rm -rf data/features/*
	rm -rf data/predictions/*
	rm -rf models/*
	rm -rf data/logs/*
	rm -rf data/temp/*
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "All pipeline artifacts cleaned."

# ==============================================================================
# Reset pipeline artifacts (interactive + safe)
# ==============================================================================
reset: ## Interactive reset — ask y/n before deleting artifacts
	@read -p "Are you sure you want to reset ERA5 Branch 1 artifacts? (y/n): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		echo "Resetting pipeline artifacts..."; \
		rm -rf data/intermediate/*; \
		rm -rf data/features/*; \
		rm -rf data/predictions/*; \
		rm -rf models/*; \
		rm -rf data/logs/*; \
		rm -rf data/temp/*; \
		echo "Pipeline reset complete."; \
	else \
		echo "Reset aborted."; \
	fi
