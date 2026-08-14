# ==============================================================================
# ERA5 Pollution‑Risk Pipeline — Branch 1 (v1.0.0)
# ==============================================================================
# Deterministic Docker image for running the ERA5 Branch 1 pipeline.
#
# This container mirrors CMS v1.x.x deployment architecture:
#   - reproducible environment
#   - Makefile‑driven execution
#   - minimal ingestion (Branch 1)
#   - fast smoke‑testing
#   - deterministic artifact generation
#
# Branch 1 intentionally avoids:
#   - full CDS ingestion logic
#   - schema/metadata validation
#   - multi‑variable ingestion
#   - GRIB/Parquet correctness checks
#   - skip‑logic correctness
#
# Branch 2 will introduce full ingestion validation, fixtures, schema checks,
# metadata extraction, skip‑logic correctness, and multi‑variable ingestion.
# ==============================================================================

FROM continuumio/miniconda3:latest

# ==============================================================================
# Working directory
# ==============================================================================
WORKDIR /app

# ==============================================================================
# Create environment
# ==============================================================================
COPY environment.yml .
RUN conda env create -f environment.yml -n era5 && conda clean -afy

# ==============================================================================
# Use the environment for all subsequent commands
# ==============================================================================
SHELL ["conda", "run", "-n", "era5", "/bin/bash", "-c"]

# ==============================================================================
# Install pip-only packages (pyarrow must be pip-installed)
# ==============================================================================
RUN pip install --no-cache-dir pyarrow aiohttp python-dotenv

# ==============================================================================
# Copy pipeline code
# ==============================================================================
COPY Makefile .
COPY src/ src/
COPY configs/ configs/
COPY scripts/ scripts/

# ==============================================================================
# Copy deployment metadata (for reproducibility)
# ==============================================================================
COPY deployment/RELEASE_NOTES.md deployment/RELEASE_NOTES.md
COPY deployment/SBOM.md deployment/SBOM.md
COPY deployment/provenance.json deployment/provenance.json

# ==============================================================================
# Copy entrypoint
# ==============================================================================
COPY deployment/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ==============================================================================
# Default entrypoint: deterministic execution
# ==============================================================================
ENTRYPOINT ["/entrypoint.sh"]
