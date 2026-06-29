# ==============================================================================
# ERA5 Pollution Risk Pipeline — Branch 1
# Makefile for running each stage of the pipeline in sequence.
#
# This Makefile provides a simple, reproducible interface for:
#   1. Validating the environment
#   2. Downloading ERA5 data
#   3. Converting GRIB → Parquet
#   4. Building features
#   5. Training a baseline model
#   6. Evaluating model performance
#
# Each stage depends on the previous one, ensuring correct execution order.
# ==============================================================================

.PHONY: env download preprocess features train evaluate test all

# ------------------------------------------------------------------------------
# Stage 00 — Environment validation
# ------------------------------------------------------------------------------
# Checks that required packages, directories, and configuration files exist.
# This runs before any other stage to prevent pipeline failures.
env:
    python -m src.utils.env_check

# ------------------------------------------------------------------------------
# Stage 01 — Download ERA5 data
# ------------------------------------------------------------------------------
# Downloads ERA5 monthly data using the CDS API.
# Output: GRIB files stored in data/raw/era5/
download: env
    python -m src.download_01.download_era5_monthly

# ------------------------------------------------------------------------------
# Stage 02 — Preprocessing (GRIB → Parquet)
# ------------------------------------------------------------------------------
# 1. Unzips downloaded ERA5 archives
# 2. Inspects GRIB metadata for correctness
# 3. Converts GRIB → Parquet for downstream processing
# Output: Parquet files stored in data/intermediate/
preprocess: download
    python -m src.preprocessing_02.unzip_grib
    python -m src.preprocessing_02.inspect_grib
    python -m src.preprocessing_02.convert_grib_to_parquet

# ------------------------------------------------------------------------------
# Stage 03 — Feature Engineering
# ------------------------------------------------------------------------------
# Builds derived features from intermediate Parquet files.
# Output: features.parquet stored in data/features/
features: preprocess
    python -m src.features_03.build_features

# ------------------------------------------------------------------------------
# Stage 04 — Modeling
# ------------------------------------------------------------------------------
# Trains a baseline model using engineered features.
# Output: model.pkl stored in models/
train: features
    python -m src.modeling_04.train_model

# ------------------------------------------------------------------------------
# Stage 05 — Evaluation
# ------------------------------------------------------------------------------
# Evaluates the trained model and generates metrics.
# Output: predictions.parquet stored in data/predictions/
evaluate: train
    python -m src.evaluation_05.evaluate_model

# ------------------------------------------------------------------------------
# Run all tests
# ------------------------------------------------------------------------------
# Executes unit tests for each pipeline stage.
test:
    pytest -q

# ------------------------------------------------------------------------------
# Full pipeline (Stages 01 → 05)
# ------------------------------------------------------------------------------
# Runs the entire pipeline end‑to‑end.
all: download preprocess features train evaluate