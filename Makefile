# ==============================================================================
# ERA5 Pollution‑Risk Pipeline — Branch 1
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
#   - help:        discover available targets
#   - test:        run Branch 1 smoke tests
#   - format/lint: CMS‑style code quality (Black + Ruff)
#   - diagnostics: CDS API connectivity check
#   - clean-cache: remove Python/pytest/ruff caches
#   - reset:       remove intermediate artifacts (safe)
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
	@echo "ERA5 Pollution‑Risk Pipeline — Branch 1"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ==============================================================================
# Stage 00 — Environment validation
# ==============================================================================
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
preprocess: download ## Unzip, inspect, and convert GRIB → Parquet (no schema validation)
	$(PYTHON) -m src.preprocessing_02.unzip_grib
	$(PYTHON) -m src.preprocessing_02.inspect_grib
	$(PYTHON) -m src.preprocessing_02.convert_grib_to_parquet

# ==============================================================================
# Stage 03 — Feature Engineering
# ==============================================================================
features: preprocess ## Build ML‑ready features (Branch 1: no deterministic checks)
	$(PYTHON) -m src.features_03.build_features

# ==============================================================================
# Stage 04 — Modeling
# ==============================================================================
train: features ## Train baseline MeanPredictor model (Branch 1: minimal modeling)
	$(PYTHON) -m src.modeling_04.train_model

# ==============================================================================
# Stage 05 — Evaluation
# ==============================================================================
evaluate: train ## Evaluate model and generate predictions (Branch 1: no artifact validation)
	$(PYTHON) -m src.evaluation_05.evaluate_model

# ==============================================================================
# Full pipeline (Stages 01 → 05)
# ==============================================================================
all: download preprocess features train evaluate ## Run full ERA5 Branch 1 pipeline

# ==============================================================================
# Testing
# ==============================================================================
test: ## Run all Branch 1 smoke tests (imports + minimal execution)
	pytest -q

# ==============================================================================
# Linting / Formatting (CMS‑style: Ruff + Black)
# ==============================================================================
format: ## Format code using Black + Ruff autofix
	black src tests configs scripts/diagnostics
	ruff check src tests configs scripts/diagnostics --fix

lint: ## Run Ruff linting across the repo (excluding notebooks)
	ruff check src tests configs scripts/diagnostics

check: ## Run tests first, then lint (Branch 1 CI-style check)
	pytest -q
	ruff check src tests configs scripts/diagnostics

# ==============================================================================
# Diagnostics
# ==============================================================================
diagnostics: ## Run CDS API connectivity test (Branch 1: minimal external validation)
	$(PYTHON) scripts/diagnostics/test_cds.py

# ==============================================================================
# Clean cache / temporary files
# ==============================================================================
clean-cache: ## Remove Python cache, pytest cache, ruff cache, and temp logs
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf data/temp/*
	rm -rf data/logs/*
	@echo "Cache cleaned."

# ==============================================================================
# Reset pipeline artifacts (safe)
# ==============================================================================
reset: clean-cache ## Remove intermediate, features, predictions, and model artifacts
	rm -rf data/intermediate/*
	rm -rf data/features/*
	rm -rf data/predictions/*
	rm -rf models/*
	@echo "Pipeline reset complete (including cache cleanup)."
