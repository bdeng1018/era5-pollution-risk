# ERA5 Pollution‑Risk Pipeline — Branch 1

## Software Bill of Materials (SBOM) — v1.0.0

---

## Overview

This Software Bill of Materials (SBOM) enumerates all runtime dependencies,
libraries, tools, and components used in the ERA5 Pollution‑Risk Pipeline
(Branch 1). It provides transparency into the software supply chain and supports
deterministic, reproducible builds across local development, Docker, and CI/CD.

Branch 1 intentionally uses a minimal dependency set to support fast
smoke‑testing and environment‑agnostic execution. Branch 2 will introduce
additional ingestion, validation, and modeling dependencies.

---

## 1. Environment Definition

The environment is defined in:

```code
environment.yml
```

Branch 1 uses a deterministic Conda environment named:

```code
era5
```

---

## 2. Core Dependencies

| Component | Version | Source | Notes |
| ---------- | --------- | -------- | ------- |
| Python | 3.10 | CPython | Primary runtime |
| numpy | pinned | PyPI | Numerical operations |
| pandas | pinned | PyPI | Data manipulation |
| xarray | pinned | PyPI | GRIB/NetCDF handling |
| pygrib | pinned | PyPI | GRIB inspection (Branch 1 minimal use) |
| pyarrow | pinned | PyPI | Parquet conversion |
| scikit‑learn | pinned | PyPI | Baseline MeanPredictor |
| requests | pinned | PyPI | CDS API connectivity |
| tqdm | pinned | PyPI | Progress bars |
| black | pinned | PyPI | Formatting |
| ruff | pinned | PyPI | Linting |
| pytest | pinned | PyPI | Smoke tests |

All versions are pinned in `environment.yml` for deterministic builds.

---

## 3. System‑Level Components

| Component | Version | Source |
| ---------- | --------- | -------- |
| Miniconda | latest | continuumio/miniconda3 Docker image |
| Bash | system | Ubuntu base image |
| Make | system | Ubuntu base image |
| Docker Engine | n/a | Host system |

Branch 1 does **not** require:

- GRIB CLI tools
- ecCodes
- libeccodes-dev
- parallel ingestion tools

These will appear in Branch 2.

---

## 4. Pipeline Components

| Component | Location | Purpose |
| ---------- | ---------- | --------- |
| Makefile | root | Deterministic pipeline orchestration |
| src/ | src/ | Pipeline logic (Stages 01–05) |
| configs/ | configs/ | Pipeline configuration |
| tests/ | tests/ | Smoke tests |
| scripts/diagnostics/ | scripts/diagnostics/ | CDS connectivity checks |
| deployment/Dockerfile | deployment/ | Deterministic container build |
| deployment/ci/ci.yml | deployment/ci/ | CI/CD workflow |

---

## 5. Docker Image Contents

The Docker image includes:

- Conda environment (`era5`)
- All pinned Python dependencies
- Makefile
- Pipeline source code
- Configuration files
- Diagnostics scripts
- Test suite

Excluded from the image:

- Large GRIB files
- Intermediate artifacts
- Predictions
- Logs
- Models

This keeps the container lightweight and reproducible.

---

## 6. Security Considerations

Branch 1 intentionally avoids:

- external ingestion of real CDS data
- multi‑variable ingestion
- schema validation
- metadata extraction
- GRIB correctness checks

This reduces the attack surface and simplifies dependency management.

Branch 2 will introduce:

- stricter validation
- metadata lineage
- ingestion correctness checks
- expanded dependency set

---

## 7. Reproducibility Guarantees

ERA5 Branch 1 v1.0.0 guarantees:

- deterministic environment creation
- deterministic pipeline execution
- deterministic Docker builds
- deterministic CI/CD runs

All dependencies are pinned and documented.

---

## 8. Versioning

This SBOM corresponds to:

```code
ERA5 Pollution‑Risk Pipeline — Branch 1 — v1.0.0
```

Future SBOMs will be versioned alongside Branch 2 and Branch 3 releases.

---

## 9. Maintainer

Brian Deng <br>
ERA5 Pollution‑Risk Pipeline Maintainer <br>
August 2026
