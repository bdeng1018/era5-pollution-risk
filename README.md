# Branch 2 — ERA5 Ingestion, Preprocessing, Core Processing & Spatiotemporal Structuring Pipeline (Current Architecture)

Branch 2 is the production‑aligned ERA5 pipeline built around **single‑variable ingestion**, **deterministic preprocessing**, **parallel‑safe chunking**, and **dense spatiotemporal tensor construction**. It replaces the Branch 1 MVP with a compiler-style architecture designed for multi-year, multi‑variable ERA5 analytics and downstream ML workflows.

Branch 2 establishes:

- deterministic, restart-safe multi-stage processing
- stable hourly metadata construction
- parallel-safe chunk planning and execution
- structured logging and diagnostics
- reproducible intermediate artifacts
- a clear forward roadmap toward feature engineering, dataset assembly, modeling, and evaluation

This README reflects the *current, correct* state of Branch 2:

---

## Architecture Overview

Branch 2 implements a **four-stage ERA5 compiler pipeline**, where each stage produces a well‑defined intermediate representation (IR):

```code
IR₀ (GRIB diagnostic)
→ IR₁ (Parquet canonical)
→ IR₂ (Chunked Parquet)
→ IR₃ (Tensors)
→ (future) Features → Datasets → Models → Evaluation
```

### Stage 1 — Ingestion (WIP)

#### IR₀ input generation

- CDS API client
- Retry logic
- Directory validation
- Config‑driven execution
- Produces raw GRIB files for Stage 2
- Some tests expected to fail during active development

Stage 1 produces the raw meteorological archives consumed by Stage 2.

### Stage 2 — Preprocessing (Stable)

#### IR₀ → IR₁ compiler stage

Stage 2 transforms raw GRIB files into structured Parquet output and produces two metadata artifacts:

- `grib_metadata.json` — GRIB‑level diagnostic metadata (IR₀)
- `metadata.json` — Parquet‑only canonical hourly metadata (IR₁)

Core responsibilities:

- Optional ZIP extraction
- GRIB inspection (diagnostic-only)
- `.idx` generation for cfgrib
- GRIB → hourly/static Parquet conversion
- Instantaneous / static / flux classification
- Tail‑hour cleanup (e.g., CIN 2018‑12‑31 spillover)
- Deterministic, restart‑safe Parquet metadata builder

Canonical directory layout:

```code
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
```

Stage 2 produces the **canonical IR₁** consumed by Stage 3.

### Stage 3 — Chunked Core Processing (Stable)

#### IR₁ → IR₂ compiler stage

- Metadata-driven chunk planning (consumes IR₁ metadata.json)
- Deterministic transforms
- Parallel-safe worker isolation
- Schema-validated Parquet outputs
- Reproducible intermediate artifacts
- Produces **chunked Parquet IR₂**

Stage 3 is the temporal/spatial core of the compiler.

### Stage 4 — Spatiotemporal Tensor Builder (New, Stable)

#### IR₂ → IR₃ compiler stage

- Dense tensor construction
- Grid normalization
- Multi‑year tensor stitching
- Deterministic tensor shapes
- Tensor metadata + diagnostics
- Produces **tensors (IR₃)** ready for feature engineering

Stage 4 is the bridge between structured Parquet and ML‑ready tensors.

### Summary

Stages 1–4 form the **engineering foundation** of the ERA5 compiler pipeline:

- **Stage 1:** Raw GRIB ingestion
- **Stage 2:** GRIB → Parquet + canonical metadata
- **Stage 3:** Chunked Parquet
- **Stage 4:** Tensors

Everything downstream (features, datasets, models, evaluation) depends on the correctness and determinism of these four IR transitions.

---

## Design Principles

Branch 2 is built on explicit engineering principles:

- **Determinism** — every stage produces stable, reproducible outputs
- **Restart‑safety** — any stage can be re‑run without corrupting downstream artifacts
- **Separation of concerns** — each stage has a single responsibility
- **Compiler‑style IR evolution** — data becomes more structured at each stage
- **Diagnostics‑first design** — every stage emits structured logs and validation artifacts
- **Parallel‑safety** — workers operate independently without shared mutable state
- **Schema contracts** — every intermediate artifact is validated
- **Multi-year scalability** - directory layout and metadata support long-horizon ingestion

These principles guide all current and future stages.

---

## Directory Layout (Git-Safe)

```code
era5-pollution-risk/
├── Makefile
├── README.md
│
├── configs/
│   ├── config.yml
│   ├── era5.yml
│   ├── months.yml
│   ├── paths.yml
│   ├── region.yml
│   ├── variables.yml
│   └── years.yml
│
├── data/                    # empty, .gitkeep only
│   ├── raw/
│   │   └── era5/            # Stage 1 outputs (GRIB)
│   ├── intermediate/        # Stage 2 outputs (hourly Parquet)
│   ├── chunks/              # Stage 3 outputs (chunked Parquet)
│   ├── chunks_metadata/     # Chunk metadata
│   ├── spatiotemporal/      # Stage 4 outputs (dense spatiotemporal tensors)
│   ├── features/            # Stage 5 outputs (engineered features)
│   ├── datasets/            # Stage 6 outputs (ML-ready datasets)
│   ├── predictions/         # Stage 7 outputs (evaluation + inference)
│   ├── logs/                # structured logs for all stages
│   └── metadata/            # Parquet metadata
│
├── models/                  # Stage 6 outputs (trained models + metadata)
│
├── diagrams/
│   ├── pipeline.md
│   └── pipeline.txt
│
├── scripts/
│   └── diagnostics/         # stage-specific diagnostics (recommended)
│       ├── stage1/
│       ├── stage2/
│       ├── stage3/
│       └── stage4/
│
├── environment.yml
│
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data_check.py
│   │   ├── env_check.py
│   │   ├── logging.py
│   │   ├── metadata.py
│   │   ├── model_io.py
│   │   └── paths.py
│   │
│   ├── download_01/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── download_era5_monthly.py
│   │   ├── download_era5_single.py
│   │   └── paths.py
│   │
│   ├── preprocessing_02/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── run_preprocessing.py
│   │   ├── unzip_grib.py
│   │   ├── inspect_grib.py
│   │   ├── convert_grib_to_parquet.py
│   │   └── metadata_parquet.py
│   │
│   ├── core_03/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── chunk_orchestrator.py
│   │   ├── chunk_spec.py
│   │   ├── chunk_planner.py
│   │   ├── chunk_worker.py
│   │   ├── chunk_schema.py
│   │   └── chunk_merge.py
│   │
│   └── spatiotemporal_04/
│       ├── README.md
│       ├── __init__.py
│       ├── driver.py
│       ├── grid.py
│       ├── mask.py
│       ├── temporal_align.py
│       ├── temporal_interpolate.py
│       ├── tensor_builder.py
│       ├── qc.py
│       └── metadata.py
│
└── tests/
    ├── download_01/
    │   ├── test_download_monthly.py
    │   ├── test_download_single.py
    │   ├── test_environment_validation.py
    │   ├── test_metadata_logging.py
    │   └── test_retry_logic.py
    │
    ├── preprocessing_02/
    │   ├── test_preprocessing_smoke.py
    │   ├── test_preprocessing_unit.py
    │   ├── test_preprocessing_integration.py
    │   ├── test_preprocessing_acceptance.py
    │   ├── test_preprocessing_system.py
    │   └── test_preprocessing_regression.py
    │
    ├── core_03/
    │   ├── test_chunk_orchestrator.py
    │   ├── test_chunk_spec.py
    │   ├── test_chunk_planner.py
    │   ├── test_chunk_worker.py
    │   ├── test_chunk_schema.py
    │   └── test_chunk_merge.py
    │
    └── spatiotemporal_04/
        ├── test_spatiotemporal_smoke.py
        │
        ├── test_grid_unit.py
        ├── test_mask_unit.py
        ├── test_temporal_align_unit.py
        ├── test_temporal_interpolate_unit.py
        ├── test_tensor_builder_unit.py
        ├── test_qc_unit.py
        └── test_metadata_unit.py
        │
        ├── test_spatiotemporal_integration.py
        ├── test_spatiotemporal_acceptance.py
        ├── test_spatiotemporal_system.py
        └── test_spatiotemporal_regression.py
```

The layout is stable and production-aligned.

---

## Stage Architecture

### Stage 1 — Ingestion (WIP)

**Inputs:** CDS API configuration
**Outputs:** Monthly GRIB files

**Invariants:**

- Directory structure must match config
- All downloads logged with metadata

**Diagnostics:**

- Retry logs
- Directory validation logs

### Stage 2 — Preprocessing (Stable)

**Inputs:** GRIB files
**Outputs:**

- Hourly Parquet files
- Unified `metadata.json`

**Invariants:**

- Only instantaneous variables appear in metadata
- Flux/static variables are excluded
- No tail-hour timestamps
- All Parquets have normalized coordinates

**Diagnostics:**

- `.idx` generation logs
- Tail-hour warnings
- Parquet validation logs

### Stage 3 — Chunked Core Processing (Stable)

**Inputs:** Stage 2 metadata
**Outputs:** Chunked Parquet files

**Invariants:**

- Chunk boundaries deterministic
- No NaNs in merged chunks
- Schema-validated outputs

**Diagnostics:**

- Chunk planner logs
- Worker isolation logs
- Schema validation reports

### Stage 4 - Spatiotemporal Tensor Builder (Stable)

**Inputs:** Chunked Parquet files
**Outputs:** Dense spatiotemporal tensors

**Invariants:**

- Tensor shapes deterministic
- No sparsity
- Grid normalization applied consistently
- Multi-year stitching produces continuous temporal coverage

**Diagnostics:**

- Tensor shape logs
- Grid alignment checks
- Temporal continuity checks

---

## Intermediate Representation (IR) Evolution

Branch 2 uses a compiler-style IR evolution:

```code
GRIB (raw)
→ Parquet (normalized hourly)
→ Chunked Parquet (structured, schema‑validated)
→ Tensors (dense spatiotemporal arrays)
→ [Stage 5] Features (engineered domain features)
→ [Stage 6] Datasets (train/val/test windows)
→ [Stage 7] Models (baseline + deep learning)
→ [Stage 8] Evaluation (spatial + temporal metrics)
```

Each stage increases structure, determinism, and ML-readiness.

---

## Failure Modes & Diagnostics

Branch 2 explicitly handles:

- **Tail‑hour contamination** (CIN/CAPE, flux variables)
- **Flux variable contamination** (accumulated fields)
- **Stale Parquet poisoning** (pre‑fix artifacts)
- **Stale metadata poisoning**
- **Chunk misalignment**
- **Grid mismatch**
- **Timestamp drift**
- **Tensor sparsity**
- **Tensor shape mismatch**

Diagnostics are emitted at every stage to detect and prevent these issues.

---

## Future Roadmap (Concise, High-Signal)

Branch 2 establishes the engineering foundation.
Stages 5–8 introduce analytics, ML, and deployment.

### Stage 5 - Feature Engineering

- Temporal aggregations
- Spatial aggregations
- Pollution‑specific engineered features
- Feature schema versioning

### Stage 6 - ML Dataset Assembly

- Train/val/test splits
- Temporal windows
- Spatial windows
- Target construction
- Dataset versioning

### Stage 7 — Modeling

- Baseline models
- Deep learning models
- Hyperparameter search
- Model metadata
- Reproducibility contracts

### Stage 8 — Evaluation & Deployment

- Spatial/temporal evaluation
- Metrics
- Model cards
- Deployment artifacts
- Monitoring

This roadmap is intentionally concise but strategically complete.

---

## Testing Status

<table>
<thead>
<tr>
<th>Stage</th>
<th>Status</th>
<th>Notes</th>
</tr>
</thead>
<tbody>
<tr>
<td><a href="ca://s?q=Discuss_Stage_1_Ingestion">Stage 1</a></td>
<td>⚠️ WIP</td>
<td>Some tests failing (expected)</td>
</tr>
<tr>
<td><a href="ca://s?q=Discuss_Stage_2_Preprocessing">Stage 2</a></td>
<td>✅ Stable</td>
<td>Deterministic, restart‑safe</td>
</tr>
<tr>
<td><a href="ca://s?q=Discuss_Stage_3_Chunking">Stage 3</a></td>
<td>✅ Stable</td>
<td>Schema‑validated, parallel‑safe</td>
</tr>
<tr>
<td><a href="ca://s?q=Discuss_Stage_4_Tensor_Builder">Stage 4</a></td>
<td>✅ Stable</td>
<td>Dense tensors, deterministic shapes</td>
</tr>
</tbody>
</table>

---

## Running the Pipeline

### Stage 1

```bash
python -m src.download_01.download_era5_monthly --config configs/config.yml
```

### Stage 2

```bash
python -m src.preprocessing_02.run_preprocessing --config configs/config.yml
```

### Stage 3

```bash
python -m src.core_03 --config configs/config.yml
```

### Stage 4

```bash
python -m src.spatiotemporal_04.driver --config configs/config.yml
```

### Makefile

```makefile
download:
    python -m src.download_01.download_era5_monthly --config configs/config.yml

preprocess:
    python -m src.preprocessing_02.run_preprocessing --config configs/config.yml

core:
    python -m src.core_03 --config configs/config.yml

spatiotemporal:
    python -m src.spatiotemporal_04.driver --config configs/config.yml

all:
    make download
    make preprocess
    make core
    make spatiotemporal
```

---

## Branch Policy

- Stage 1 may fail during active development
- Stage 2 must remain deterministic
- Stage 3 must remain determinstic
- Stage 4 must produce dense tensors
- Main branch remains stable
- Branch 2 is safe to push

---

## Branch 1 → Branch 2 Snapshot

Branch 1 = MVP <br>
Branch 2 = production‑aligned pipeline <br>
Branch 3 = distributed parallelization (future)

Key Branch 2 upgrades:

- Multi‑stage architecture
- Config‑driven ingestion
- Structured metadata
- Deterministic preprocessing
- Parallel chunk processing
- Dense spatiotemporal tensors
- Unified logging
- Schema contracts

---

## 📬 Maintainer

**Brian Deng** <br>
Los Angeles, CA

**Focus:**

- Climate analytics
- Hazard‑risk modeling
- ERA5‑based pipelines
- Geospatial ML
- Pollution‑risk analytics
