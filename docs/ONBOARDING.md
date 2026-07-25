# Developer Onboarding — ERA5 Pollution Risk Pipeline

Welcome to the ERA5 Pollution Risk Pipeline.
This document provides everything you need to set up your environment, run the pipeline, inspect artifacts, debug issues, and contribute code.

---

## 1. Prerequisites

Install the following:

- Python 3.10
- Conda (recommended)
- VS Code
- Git

Clone the repository:

```bash
git clone https://github.com/bdeng1018/era5-pollution-risk
cd era5-pollution-risk
```

---

## 2. VS Code Workspace Setup

Open the workspace file at the repo root:

```code
era5-pollution-risk.code-workspace
```

This loads:

- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/launch.json`
- `.vscode/extensions.json`

### Recommended Extensions

These are auto-loaded:

- Python + Pylance
- Black
- Ruff
- Pytest
- Rainbow CSV
- YAML Support
- Makefile Tools
- GitLens

---

## 3. Environment Setup

Create the environment:

```bash
make env
```

Activate it:

```bash
conda activate era5-pollution-risk
```

Install local dependencies:

```bash
pip install -e .
```

---

## 4. Running the Pipeline (Stages 01–08)

The pipeline is stage‑aligned and IR‑aligned.
Each stage has a Makefile target and produces a well-defined artifact.

### Stage 01 — ERA5 Download

```bash
make stage01
```

Downloads ERA5 variables defined in `configs/era5.yml` and stores them under:

```code
data/raw/era5/
```

### Stage 02 — Preprocessing

```bash
make stage02
```

Cleans, harmonizes, and normalizes raw ERA5 + pollution data.
Outputs stored under:

```code
data/intermediate/
```

### Stage 03 — Chunk Engine

```bash
make stage03
```

Builds spatial/temporal chunks and metadata:

```code
data/chunks/
data/chunks_metadata/
```

### Stage 04 — Spatiotemporal Compiler

```bash
make stage04
```

Compiles IR₄ canonical tensors:

```code
data/spatiotemporal/
```

### Stage 05 - Feature Engineering

```bash
make stage05
```

Generates IR₅ feature tensors:

```code
data/features/
```

### Stage 06 — Modeling

```bash
make stage06
```

Builds IR₆ model-ready datasets:

```code
data/model_ready/
```

### Stage 07 — Evaluation

```bash
make stage07
```

Runs evaluation, metrics, residuals, and predictions:

```code
data/evaluation/
data/predictions/
```

### Stage 08 — Deployment Artifacts

```bash
make stage08
```

Builds IR₈ deployment artifacts:

```code
data/deployment/
```

---

## 5. Diagnostics (All Stages)

Run all diagnostics:

```bash
make diagnostics
```

Run individual diagnostics:

```bash
make diag-stage01
make diag-stage02
make diag-stage03
make diag-stage04
make diag-stage05
make diag-stage06
make diag-stage07
make diag-stage08
```

Diagnostics output to:

```code
data/logs/
```

---

## 6. Testing & Linting

Run tests:

```bash
make test
```

Run linting:

```bash
make lint
```

Tests should always be run **before** linting.

---

## 7. Resetting Pipeline Artifacts

### Safe cleanup (recommended)

```bash
make clean-cache
```

Removes Python caches only.

### Full artifact reset (destructive)

```bash
make reset
```

Removes pipeline artifacts for Stages 01–08.
Use with caution.

---

## 8. Folder Structure Overview

```code
src/
  download_01/
  preprocessing_02/
  core_03/
  spatiotemporal_04/
  features_05/
  modeling_06/
  evaluation_07/
  deployment_08/
  api/
  utils/

scripts/
  diagnostics/

data/
  raw/
  intermediate/
  chunks/
  chunks_metadata/
  spatiotemporal/
  features/
  model_ready/
  evaluation/
  predictions/
  deployment/
  logs/
  metadata/

configs/
diagrams/
tests/
docs/
```

---

## 9. Contributing Code

### Formatting

Black + Ruff are enforced:

```bash
make lint
```

### Testing

All new code must include tests:

```bash
make test
```

### Diagnostics

Every stage must include a diagnostics script under:

```code
scripts/diagnostics/
```

### Pull Requests

- Include a description of changes
- Include test coverage
- Update diagnostics if needed
- Update diagrams if architecture changes

---

## 10. Debugging Tips

### VS Code Launchers

Use:

- “Run Stage 01 Download”
- “Run Stage 02 Preprocessing”
- “Run Stage 03 Chunk Engine”
- “Run Stage 04 Compiler”
- “Run Stage 05 Features”
- “Run Stage 06 Modeling”
- “Run Stage 07 Evaluation”
- “Run Stage 08 Deployment”
- “Pytest: Full Workspace”

### Common Issues

- Missing ERA5 raw data → run Stage 01
- Intermediate artifacts missing → run Stage 02
- Chunk metadata missing → run Stage 03
- IR₄ tensors missing → run Stage 04
- Feature tensors missing → run Stage 05
- Model-ready dataset missing → run Stage 06
- Predictions missing → run Stage 07
- Deployment artifacts missing → run Stage 08

---

## 11. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
