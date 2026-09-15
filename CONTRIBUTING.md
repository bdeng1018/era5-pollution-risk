# CONTRIBUTING.md - ERA5 Pollution‑Risk Pipeline (Branch 2)

Thank you for your interest in contributing to **era5-pollution-risk**.
Branch 2 implements a **deterministic, multi‑stage ERA5 compiler pipeline** defined by its Intermediate Representations (IR₀ → IR₅).
This document describes how to contribute code, documentation, tests, diagnostics, and tooling.

---

## 📦 Repository Structure

Branch 2 currently implements IR₀ → IR₅:

```text
src/
  download_01/           # Stage 01 — IR₀: Raw ERA5 GRIB ingestion
  preprocessing_02/      # Stage 02 — IR₀ → IR₁: Hourly Parquet + metadata.json
  core_03/               # Stage 03 — IR₁ → IR₂ → IR₃: Chunk workers + merge
  spatiotemporal_04/     # Stage 04 — IR₂/IR₃ → IR₄: Spatiotemporal tensor + contracts
  features_05/           # Stage 05 — IR₄ → IR₅: Feature tensors (completed)
  modeling_06/           # Stage 06 — IR₅ → IR₆: Model-ready datasets (planned)
  evaluation_07/         # Stage 07 — IR₆ → IR₇: Predictions + evaluation (planned)
  deployment_08/         # Stage 08 — IR₇ → IR₈: Deployment artifacts (planned)
```

Data artifacts:

```text
data/raw/era5/           # IR₀
data/intermediate/       # IR₁ + IR₃
data/chunks/             # IR₂
data/chunks_metadata/    # IR₂ metadata
data/spatiotemporal/     # IR₄
data/features/           # IR₅
data/datasets/           # IR₆ (future)
data/predictions/        # IR₇ (future)
deployment/              # IR₈ (future)
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

## 🧰 Development Environment (Import‑Time Purity)

Branch 2 uses a **project‑local virtual environment** (`.venv`) for pipeline execution, testing, and development.

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

Stage 2 must remain **import‑time lightweight**:

- No heavy imports (`cfgrib`, `eccodes`, `xarray`) at module load
- Heavy imports allowed **only inside conversion helpers**

Pipeline execution must occur inside `.venv` to avoid conflicts with Conda’s GRIB tooling.

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
make stage01   # IR₀
make stage02   # IR₀ → IR₁
make stage03   # IR₁ → IR₂ → IR₃
make stage04   # IR₂/IR₃ → IR₄
make stage05   # IR₄ → IR₅
make stage06   # IR₅ → IR₆ (planned)
make stage07   # IR₆ → IR₇ (planned)
make stage08   # IR₇ → IR₈ (planned)
```

Full pipeline (Stages 01-05):

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
- test IR boundary transitions (`@pytest.mark.ir`)

Branch 2 introduces **full validation, fixtures, IR boundary tests, and integration tests**.

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

## 📘 Documentation Requirements

Each stage must include:

- a `README.md` describing inputs, outputs, IR boundaries, architecture, and runner behavior
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
2. Add or update the stage README.md (must define IR input/output)
3. Add `__init__.py`
4. Add engine modules (planner, orchestrator, worker, writer, etc.)
5. Add diagnostics under `scripts/diagnostics/stageXX/`
6. Add tests under `tests/` (include IR boundary tests)
7. Update the Makefile (stage target + IR comment)
8. Update the root README (IR boundary diagram)
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

- `0.2.x` — Branch 2 (IR₀ → IR₅)
- `0.3.x` — Modeling expansion + evaluation reports (IR₆ → IR₇)
- `0.4.x` — Deployment + dashboards (IR₈)

All changes must be recorded in `CHANGELOG.md` under:

```text
## [Unreleased]
```

Tags are created only when a milestone is complete.

---

## 🤝 Pull Requests

Pull requests should:

- be atomic
- include tests (unit + IR boundary + integration)
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
Location: Los Angeles, CA  <br>
Email: **<bdeng.data.pipelines@gmail.com>**  <br>
Focus: scientific computing, climate data engineering, analytics systems design, reproducible pipelines, technical writing
