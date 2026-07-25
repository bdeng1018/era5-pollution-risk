# ERA5 Compiler Pipeline — Branch 2 (Deterministic Ingestion → Preprocessing → Chunking → Spatiotemporal Structuring)

Branch 2 is the deterministic engineering foundation of the ERA5 compiler pipeline. It implements **single‑variable ingestion**, **deterministic preprocessing**, **parallel‑safe chunking**, and **dense spatiotemporal tensor construction**. It replaces the Branch 1 MVP with a compiler‑style architecture designed for multi‑year, multi‑variable ERA5 analytics and downstream ML workflows.

Branch 2 establishes:

- deterministic, restart-safe multi-stage processing
- stable hourly metadata construction
- parallel-safe chunk planning and execution
- structured logging and diagnostics
- reproducible intermediate artifacts
- a clear forward roadmap toward feature engineering, dataset assembly, modeling, and evaluation

---

## 🧭 Architecture Overview

Branch 2 implements a **four-stage ERA5 compiler pipeline**, where each stage produces a well‑defined intermediate representation (IR):

```code
IR₀ (GRIB diagnostic)
→ IR₁ (Parquet canonical)
→ IR₂ (Chunked Parquet)
→ IR₃ (Dense spatiotemporal tensors)
→ [future] Features → Datasets → Models → Evaluation
```

---

## 🏗️ Stage Overview

### Stage 1 — Ingestion (WIP)

#### IR₀ input generation

- CDS API client
- Retry logic
- Directory validation
- Config‑driven execution
- Produces raw GRIB files for Stage 2
- Some tests expected to fail during active development

#### Invariants

- Directory structure must match config
- All downloads logged with metadata

#### Diagnostics

- Retry logs
- Directory validation logs

---

### Stage 2 — Preprocessing (Stable)

#### IR₀ → IR₁ compiler stage

Outputs:

- `grib_metadata.json` — GRIB‑level diagnostic metadata (IR₀)
- `metadata.json` — canonical hourly Parquet metadata (IR₁)

#### Invariants

- Only instantaneous variables appear in metadata
- Flux/static variables excluded
- No tail‑hour timestamps
- All Parquets have normalized coordinates

#### Diagnostics

- `.idx` generation logs
- Tail‑hour warnings
- Parquet validation logs

Canonical layout:

```code
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
```

---

### Stage 3 — Chunked Core Processing (Stable)

#### IR₁ → IR₂ compiler stage

- Metadata‑driven chunk planning
- Deterministic transforms
- Parallel‑safe worker isolation
- Schema‑validated Parquet outputs
- Produces **chunked Parquet IR₂**

#### Invariants

- Chunk boundaries deterministic
- No NaNs in merged chunks
- Schema‑validated outputs

#### Diagnostics

- Chunk planner logs
- Worker isolation logs
- Schema validation reports

---

### Stage 4 — Spatiotemporal Tensor Builder (Stable)

#### IR₂ → IR₃ compiler stage

- Dense tensor construction
- Grid normalization
- Multi‑year tensor stitching
- Deterministic tensor shapes
- Tensor metadata + diagnostics
- Produces **tensors (IR₃)** ready for feature engineering

#### Invariants

- Tensor shapes deterministic
- No sparsity
- Grid normalization applied consistently
- Multi‑year stitching produces continuous temporal coverage

#### Diagnostics

- Tensor shape logs
- Grid alignment checks
- Temporal continuity checks

---

## 🔁 Intermediate Representation (IR) Evolution

Branch 2 uses a compiler‑style IR evolution:

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

Each stage increases structure, determinism, and ML‑readiness.

---

## ⚠️ Failure Modes & Diagnostics

Branch 2 explicitly handles:

- tail‑hour contamination (CIN/CAPE, flux variables)
- flux variable contamination (accumulated fields)
- stale Parquet poisoning
- stale metadata poisoning
- chunk misalignment
- grid mismatch
- timestamp drift
- tensor sparsity
- tensor shape mismatch

Diagnostics are emitted at every stage to detect and prevent these issues.

---

## 🔮 Future Roadmap (Concise, High-Signal)

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

---

## 🧪 Testing Status

| Stage | Status | Notes |
|-------|--------|-------|
| Stage 1 | ⚠️ WIP | Some tests failing (expected) |
| Stage 2 | ✅ Stable | Deterministic, restart-safe |
| Stage 3 | ✅ Stable | Schema-validated, parallel-safe |
| Stage 4 | ✅ Stable | Dense tensors, deterministic shapes |

---

## ▶️ Running the Pipeline

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

## 🏛️ Branch Policy

- Stage 1 may fail during active development
- Stage 2 must remain deterministic
- Stage 3 must remain deterministic
- Stage 4 must produce dense tensors
- `main` branch remains stable
- Branch 2 is safe to push

---

## 📈 Branch 1 → Branch 2 Snapshot

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
