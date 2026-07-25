# CONTRIBUTING.md - ERA5 Pollution‑Risk Pipeline (Branch 2)

Thank you for your interest in contributing to **era5-pollution-risk**.
Branch 2 implements a reproducible, multi‑stage ERA5 ingestion, preprocessing, chunking, feature‑engineering, modeling, evaluation, and deployment pipeline.

This document describes how to contribute code, documentation, tests, diagnostics, and tooling.

---

## 📦 Repository Structure

Branch 2 is organized into eight pipeline stages:

```text
src/
  download_01/           # Stage 01 — ERA5 GRIB download
  preprocessing_02/      # Stage 02 — unzip → inspect → convert → metadata
  core_03/               # Stage 03 — chunk planner → orchestrator → worker → merge
  spatiotemporal_04/     # Stage 04 — grid → mask → align → interpolate → qc → tensor builder
  features_05/           # Stage 05 — feature engineering (planned)
  modeling_06/           # Stage 06 — modeling (planned)
  evaluation_07/         # Stage 07 — evaluation (planned)
  deployment_08/         # Stage 08 — deployment scaffolding (planned)
```

Data artifacts:

```text
data/raw/era5/
data/intermediate/
data/chunks/
data/chunks_metadata/
data/spatiotemporal/
data/features/
data/predictions/
data/logs/
data/metadata/
```

Diagnostics:

```text
scripts/diagnostics/
```

Tests:

```text
tests/
```

Documentation:

```text
docs/
diagrams/
```

---

## 🧰 Development Environment

Branch 2 uses a **project‑local virtual environment** (.venv) for all pipeline execution, testing, and development.

### Create the environment

```bash
python3 -m venv .venv --copies
source .venv/bin/activate
```

### Install development dependencies

```bash
pip install pytest black ruff mypy
```

### Optional: Conda (GRIB CLI tools only)

```bash
conda env create -f environment.yml
conda activate era5-pollution-risk
```

**Important:**
Pipeline execution must occur inside `.venv` to avoid conflicts with Conda’s eccodes and GRIB indexing.

### Validate the environment

```bash
make env
```

---

## 📊 Diagram Workflow

All diagrams are maintained in **Mermaid (.md)** and exported to **PNG**.

Both files are committed:

```text
diagrams/*.md   → source of truth
diagrams/*.png  → rendered artifact
```

Use:

- VS Code Mermaid preview
- Mermaid CLI (`mmdc`)

Do not commit SVG or draw.io files unless explicitly required.

---

## 🛠 Running the Pipeline

Each stage can be executed individually via Makefile:

```bash
make stage01
make stage02
make stage03
make stage04
make stage05
make stage06
make stage07
make stage08
```

Full pipeline:

```bash
make run
```

Cleanup:

```bash
make clean-cache
make clean-intermediate
make reset-soft
```

---

## 🧪 Testing

All tests live under:

```text
tests/
```

Run the full suite:

```bash
make test
```

Run a specific stage:

```bash
pytest tests/core_03
pytest tests/spatiotemporal_04
```

### Testing Guidelines

- use `tmp_path` for filesystem isolation
- avoid writing to real pipeline directories
- prefer synthetic ERA5 fixtures
- ensure deterministic outputs
- test both engine logic and writer behavior
- test chunking, merging, and tensor‑builder correctness

Branch 2 introduces **full validation, fixtures, and integration tests**.

---

## 🧼 Code Style

Branch 2 follows:

- **Black** for formatting
- **Ruff** for linting
- **isort** (Black profile) for imports
- **mypy** for optional type checking

Recommended workflow:

```bash
black src tests scripts models
ruff check src tests scripts configs models --fix
isort src tests scripts models
```

---

## 📘 Documentation

Each stage must include:

- a `README.md` describing inputs, outputs, architecture, and runner behavior
- module‑level docstrings
- function‑level docstrings (NumPy‑style)

Example:

```python
def convert_grib_to_parquet(path: Path) -> Path:
    """
    Convert a single-variable GRIB file to Parquet.

    Parameters
    ----------
    path : Path
        Input GRIB file.

    Returns
    -------
    Path
        Output Parquet file.
    """
```

---

## 🧱 Adding or Modifying a Stage

To add or modify a pipeline stage:

1. Create or update the directory under `src/`
2. Add or update the stage README.md
3. Add `__init__.py`
4. Add engine modules (planner, orchestrator, worker, writer, etc.)
5. Add diagnostics under `scripts/diagnostics/stageXX/`
6. Add tests under `tests/`
7. Update the Makefile
8. Update the root README
9. Update `CHANGELOG.md` under `[Unreleased]`

---

## 🔄 Makefile Workflow

The Makefile defines:

- environment validation
- stage execution
- testing
- formatting & linting
- cleanup & reset

Contributors should annotate new targets using:

```makefile
target: ## Description
```

This enables `make help`.

---

## 🧭 Branching & Versioning

This project uses semantic versioning:

- `0.2.x` — Branch 2 (Stages 01–08)
- `0.3.x` — Modeling expansion + evaluation reports
- `0.4.x` — Deployment + dashboards

All changes must be recorded in `CHANGELOG.md` under:

```text
## [Unreleased]
```

Tags are created only when a milestone is complete.

---

## 🤝 Pull Requests

Pull requests should:

- be atomic
- include tests
- update documentation
- update `CHANGELOG.md`
- pass linting and formatting
- avoid multi‑stage changes in a single PR

---

## 🛡 Code of Conduct

See `CODE_OF_CONDUCT.md` for community guidelines.

---

## 📬 Contact

Maintainer: **Brian Deng** <br>
Location: Los Angeles, CA <br>
Email: **<bdeng.data.pipelines@gmail.com>** <br>
Focus: scientific computing, climate data engineering, analytics systems design, reproducible pipelines, technical writing
