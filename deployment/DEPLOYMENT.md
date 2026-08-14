# ERA5 Pollution‑Risk Pipeline — Branch 1

## Deployment Guide — v1.0.0

---

## Overview

This document describes how to run and validate the ERA5 Pollution‑Risk Pipeline
(Branch 1) in deterministic environments, including local development, optional
Docker execution, and GitHub Actions CI/CD.

Branch 1 is intentionally lightweight: ingestion is optional, tests are fully
mocked, and execution is offline and reproducible. It avoids heavy validation
logic, schema enforcement, multi‑variable ingestion, and GRIB/Parquet correctness
checks. These capabilities will be introduced in Branch 2.

---

## 1. Local Development

### 1.1 Requirements

- Python 3.10+
- Make
- Docker (optional)
- No Conda activation required (Branch 1 uses `.venv`)

### 1.2 Create the environment

```bash
make build
```

### 1.3 Validate environment

```bash
make env
```

### 1.4 Run the full pipeline

```bash
make all
```

### 1.5 Run smoke tests (deterministic, offline)

```bash
make test
```

### 1.6 Lint and format

```bash
make lint
make format
```

### 1.7 Reset artifacts (interactive)

```bash
make reset
```

---

## 2. Docker Execution (Optional)

Branch 1 includes a deterministic container defined in:

```code
deployment/Dockerfile
```

This container is used for reproducible local runs and CI/CD validation.
Branch 1 does **not** deploy this container to production.

### 2.1 Build the image

```bash
docker build -t era5-branch1 -f deployment/Dockerfile .
```

### 2.2 Run environment validation

```bash
docker run --rm era5-branch1
```

### 2.3 Run the full pipeline inside Docker

```bash
docker run --rm era5-branch1 make all
```

### 2.4 Run tests inside Docker

```bash
docker run --rm era5-branch1 make test
```

---

## 3. CI/CD Deployment (GitHub Actions)

The CI workflow is located at:

```code
deployment/ci/ci.yml
```

It performs:

- environment creation
- linting
- deterministic smoke tests (CDS API fully mocked)
- diagnostics
- optional Docker build
- Makefile integrity checks

This ensures Branch 1 executes reproducibly across all environments.

---

## 4. Directory Structure

```text
era5-pollution-risk/
    src/
    configs/
    tests/
    scripts/
    data/
    models/
    deployment/
        Dockerfile
        DEPLOYMENT.md
        RELEASE_NOTES.md
        SBOM.md
        provenance.json
        ci/
            ci.yml
    Makefile
    environment.yml
```

---

## 5. Production‑Style Execution (Simulated)

Branch 1 is **not** intended for production ingestion. However, deterministic
execution can be achieved using:

```bash
docker run --rm era5-branch1 make all
```

This ensures:

- reproducible environment
- reproducible artifacts
- reproducible ingestion flow

Branch 2 will introduce production‑grade ingestion validation.

---

## 6. Known Deployment Limitations (Intentional for Branch 1)

- No real CDS ingestion logic
- No schema validation
- No metadata extraction
- No multi‑variable ingestion
- No GRIB/Parquet correctness checks
- No distributed chunking
- No skip‑logic correctness

These will be addressed in Branch 2.

---

## 7. Versioning

ERA5 follows semantic versioning:

- **MAJOR**: Branch‑level architectural changes
- **MINOR**: New ingestion or modeling capabilities
- **PATCH**: Deterministic fixes, formatting, diagnostics

v1.0.0 is the first stable release of Branch 1.

---

## 8. Maintainer

Brian Deng <br>
ERA5 Pollution‑Risk Pipeline Maintainer <br>
August 2026
