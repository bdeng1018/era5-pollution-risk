# CONTRIBUTING.md

Thank you for your interest in contributing to **era5-pollution-risk**.
This project implements a reproducible, multi‑stage ERA5 ingestion and modeling pipeline.
**Branch 1** covers Stages 01–05 (download → preprocessing → features → modeling → evaluation).

This document describes how to contribute code, documentation, tests, and diagnostics.

---

## 📦 Repository Structure

The project is organized into five pipeline stages:

```text
src/
  download_01/
  preprocessing_02/
  features_03/
  modeling_04/
  evaluation_05/
```

Each stage has:

- a dedicated README
- module-level docstrings
- lightweight logging
- smoke tests
- Makefile targets

Data artifacts are stored under:

```text
data/raw/era5/
data/intermediate/
data/features/
data/predictions/
```

Model artifacts are stored under:

```text
models/
```

Diagnostics scripts live under:

```text
scripts/diagnostics/
```

---

## 🧰 Development Environment

Branch 1 uses a **project‑local virtual environment** (`.venv`) for all pipeline
execution, testing, and development. Conda is optional and only required for
GRIB CLI tools (`grib_ls`, `grib_dump`) or exploratory notebook workflows.

### Create the environment

```bash
python3 -m venv .venv --copies
```

### Activate it

```bash
source .venv/bin/activate
```

### Install development dependencies

```bash
pip install pytest black ruff mypy
```

### Optional: Conda environment (GRIB CLI tools only)

An `environment.yml` is included for contributors who prefer Conda when working
with GRIB CLI utilities or notebooks:

```bash
conda env create -f environment.yml
conda activate era5-pollution-risk
```

- **Do NOT use Conda to run the pipeline**
Pipeline execution must occur inside `.venv` to avoid conflicts with Conda’s
`eccodes` and GRIB indexing.

### Validate the environment

```bash
make env
```

### Important Note

- Branch 1 is **environment‑agnostic** — smoke tests do not require CDS API credentials, network access, or real GRIB files.

### Environment Summary

- Always activate `.venv` **before** running any pipeline stage.
- **Never** activate Conda unless using GRIB CLI tools.
- Branch 1 smoke tests require **no** CDS API credentials or network access.

---

## 📊 Diagram Workflow

All diagrams are maintained in Mermaid (`.md`) and exported to PNG.

Both files are committed:

- `diagrams/*.md`  → source of truth
- `diagrams/*.png` → rendered artifact

Use VS Code Mermaid preview or Mermaid CLI for PNG export.

---

## 🛠 Running the Pipeline

Each stage can be executed individually via Makefile:

```bash
make download
make preprocess
make features
make train
make evaluate
```

Diagnostics scripts live under:

```text
scripts/diagnostics/
```

Example:

```bash
python scripts/diagnostics/test_cds.py
```

---

## 🧪 Testing

All tests are located under:

```text
tests/
```

Run the full suite:

```bash
make test
```

Or run a specific stage:

```bash
pytest tests/test_preprocess.py
```

Branch 1 tests are **smoke tests only**:

- modules import correctly
- no skip logic validation
- no network-dependent tests
- no schema validation
- no multi-variable ingestion tests

Branch 2 will introduce full validation, fixtures, and integration tests.

---

## 🧼 Code Style

This project follows:

- **Black** for formatting
- **ruff** for linting
- **mypy** for type checking (optional)

Recommended workflow:

```bash
black src tests configs scripts/diagnostics
ruff check src tests configs scripts/diagnostics --fix
```

---

## 📘 Documentation

Each stage should include:

- a `README.md` describing inputs, outputs, and architecture
- module‑level docstrings
- function‑level docstrings using NumPy‑style format

Example docstring:

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
2. Add or update the stage `README.md`
3. Add `__init__.py`
4. Add engine modules (download, preprocess, features, model, evaluate)
5. Add diagnostics under `scripts/diagnostics/`
6. Add tests under `tests/`
7. Update the Makefile
8. Update the root README
9. Update `CHANGELOG.md` under `[Unreleased]`

### Branch 1 Note

Branch 1 is **fully deterministic** and intentionally minimal.
Parallelization, multi-variable ingestion, metadata tracking, and advanced modeling arrive in **Branch 2**.

---

## 🔄 Makefile Workflow

The Makefile defines:

- environment validation
- stage execution
- testing
- full pipeline run

Contributors should annotate new targets using:

```make
target: ## Description
```

This enables `make help`.

---

## 🧭 Branching & Versioning

This project uses semantic versioning:

- `0.1.x` — Branch 1 (Stages 01–05)
- `0.2.x` — Multi-variable ingestion + metadata
- `0.3.x` — Modeling expansion + evaluation reports

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

Maintainer: **Brian Deng**  <br>
Location: Los Angeles, CA <br>
Email: **<bdeng.data.pipelines@gmail.com>** <br>
Focus: climate data engineering, scientific computing, reproducible pipelines, technical writing
