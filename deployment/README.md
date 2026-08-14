# ERA5 Pollution‑Risk Pipeline — Branch 1

## Deployment Directory Overview — v1.0.0

---

## Purpose

The `deployment/` directory contains all artifacts required to **validate, package, and release** the ERA5 Pollution‑Risk Pipeline (Branch 1) in deterministic environments.
Branch 1 is intentionally lightweight: ingestion is optional, tests are fully mocked, and execution is offline and reproducible.

This directory mirrors the structure used in larger ingestion pipelines (such as
CMS), but Branch 1 uses it primarily for:

- reproducible local execution
- CI/CD validation
- deterministic environment setup
- release metadata and provenance

Heavy ingestion validation, schema checks, metadata extraction, multi‑variable
ingestion, and skip‑logic correctness will be introduced in **Branch 2**.

---

## Directory Contents

```text
deployment/
    Dockerfile
    entrypoint.sh
    RELEASE_NOTES.md
    DEPLOYMENT.md
    SBOM.md
    provenance.json
    ci/
        ci.yml
```

Each file is described below.

---

## 1. Dockerfile

**Path:** `deployment/Dockerfile`

Defines the deterministic container used for Branch 1.
Key features:

- Conda environment (`era5`)
- Reproducible build from `environment.yml`
- Makefile-driven execution
- Environment validation on startup

Used primarily for CI/CD and reproducible local runs.
Branch 1 does **not** deploy this container to production.

---

## 2. entrypoint.sh

**Path:** `deployment/entrypoint.sh`

Container entrypoint script.
Responsibilities:

- Validate environment (`make env`)
- Run full pipeline if no arguments provided
- Run specific Makefile targets when arguments are passed

---

## 3. RELEASE_NOTES.md

**Path:** `deployment/RELEASE_NOTES.md`

Versioned release notes for:

- Branch 1 architecture
- v1.0.0 features
- limitations
- roadmap
- developer ergonomics
- CI/CD behavior

Included in GitHub releases.

---

## 4. DEPLOYMENT.md

**Path:** `deployment/DEPLOYMENT.md`

Comprehensive deployment guide covering:

- local development
- Docker execution
- CI/CD workflow
- directory structure
- production-style execution
- known limitations

This is the main user-facing deployment document.

---

## 5. SBOM.md

**Path:** `deployment/SBOM.md`

Software Bill of Materials documenting:

- Python dependencies
- system-level components
- pipeline components
- Docker image contents
- reproducibility guarantees

Supports supply-chain transparency and deterministic builds.

---

## 6. provenance.json

**Path:** `deployment/provenance.json`

Frozen metadata for the v1.0.0 release:

- pipeline version
- environment details
- build artifacts
- stage definitions
- artifact directories
- limitations
- roadmap

Used by CI/CD, release automation, and reproducibility workflows.

---

## 7. ci/ci.yml

**Path:** `deployment/ci/ci.yml`

GitHub Actions workflow providing:

- environment creation
- linting
- smoke tests (CDS API fully mocked)
- diagnostics
- optional Docker build
- Makefile integrity checks

Ensures deterministic execution across all environments.

---

## Versioning

This deployment directory corresponds to:

```code
ERA5 Pollution‑Risk Pipeline — Branch 1 — v1.0.0
```

Future branches (2 and 3) will extend this structure with additional ingestion,
validation, and modeling artifacts.

---

## Maintainer

Brian Deng <br>
ERA5 Pollution‑Risk Pipeline Maintainer <br>
August 2026
