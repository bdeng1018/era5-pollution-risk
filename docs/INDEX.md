# Documentation Index — ERA5 Pollution Risk Pipeline

This index provides a structured entry point into all documentation for the ERA5 Pollution Risk Pipeline.
Use this page to navigate architecture, onboarding, pipeline flow, schemas, and diagrams.

---

## 1. Core Documentation

- **Architecture Overview**
  `docs/ARCHITECTURE.md`
  High‑level system design, stage responsibilities, IR boundaries, and directory structure.

- **Developer Onboarding**
  `docs/ONBOARDING.md`
  Environment setup, Makefile usage, diagnostics, testing, and development workflow.

- **Pipeline Flow**
  `docs/PIPELINE_FLOW.md`
  Stage‑by‑stage execution flow, artifact dependencies, and IR transitions.

- **Data Dictionary**
  `docs/DATA_DICTIONARY.md`
  Definitions for all 21 ERA5 variables, metadata fields, IR₄/IR₅ tensors, and pollution features.

- **Schema Reference**
  `docs/SCHEMA_REFERENCE.md`
  Structural schemas for raw ERA5, chunk metadata, IR₄, IR₅, and placeholders for IR₆–IR₈.

---

## 2. Diagrams (Architecture Visuals)

All diagrams live under:

```code
diagrams/
```

Key diagrams include:

- `pipeline_overview.md`
- `ir_boundaries.md`
- `compiler_contract_graph.md`
- `feature_registry_dag.md`
- `model_lineage.md`
- `model_registry_flow.md`
- `deployment_promotion_flow.md`
- `api_flow.md`
- `makefile_target_flow.md`
- Stage‑specific diagrams (`stage02_preprocessing.md`, `stage03_chunk_engine.md`, etc.)

---

## 3. Configuration Files

All configs live under:

```code
configs/
```

These files define ERA5 variables, spatial regions, temporal ranges, pipeline paths, and stage‑specific parameters.

| File | Purpose |
|------|---------|
| `config.yml` | Top‑level pipeline configuration and global settings |
| `era5.yml` | ERA5 variable definitions, normalization rules, and download parameters |
| `months.yml` | Month ranges used for ERA5 download and preprocessing |
| `paths.yml` | Canonical directory structure for raw, intermediate, IR₄, IR₅, and diagnostics outputs |
| `region.yml` | Spatial region definitions (lat/lon bounds, masks, grid selection) |
| `variables.yml` | Master list of ERA5 variables (21 GRIB fields) and feature engineering variable groups |
| `years.yml` | Year ranges used for ERA5 download and temporal slicing |

All configuration files are declarative and stage‑aligned.
They ensure reproducibility across:

- Stage 01 (ERA5 download)
- Stage 02 (preprocessing)
- Stage 03 (chunk engine)
- Stage 04 (IR₄ compiler)
- Stage 05 (IR₅ feature engineering)(future)
- Stage 06 (IR₆ modeling)(future)
- Stage 07 (IR₇ evaluation)(future)
- Stage 08 (IR₈ deployment)(future)

Configuration is intentionally minimal, explicit, and fully separated from code.

---

## 4. Makefile Targets

The Makefile provides the primary developer interface:

```bash
make env
make stage01
make stage02
make stage03
make stage04
make test
make lint
make reset
```

See `ONBOARDING.md` for full details.

---

## 5. Tests

All tests live under:

```code
tests/
```

Tests cover:

- Stage logic
- Diagnostics
- IR tensor correctness
- Feature engineering (future)
- Modeling (future)
- Deployment (future)

---

## 6. API Documentation (Future)

Once IR₈ stabilizes, add:

- `API_REFERENCE.md`
- `/predict` schema
- `/metadata` schema
- `/health` endpoint
- Model versioning rules

---

## 8. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
