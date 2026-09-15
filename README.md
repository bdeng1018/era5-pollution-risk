# ERA5 Compiler Pipeline — Branch 2

Branch 2 is the deterministic engineering foundation of the ERA5 compiler pipeline. It implements **multi‑variable ingestion**, **deterministic preprocessing**, **parallel‑safe chunking**, **dense spatiotemporal tensor construction**, and **completed feature engineering (IR₅)**. It replaces the Branch 1 MVP with a compiler‑style architecture designed for multi‑year, multi‑variable ERA5 analytics and downstream ML workflows.

Branch 2 establishes:

- deterministic, restart-safe multi-stage processing
- stable hourly metadata construction
- parallel-safe chunk planning and execution
- structured logging and diagnostics
- reproducible intermediate artifacts
- a clear forward roadmap toward datasets, models, evaluation, and deployment

---

## 🧭 Architecture Overview

The ERA5 pipeline is a **compiler‑style system** defined by its Intermediate Representations (IRs).
Each IR marks a **stable, deterministic boundary** between pipeline stages.

```text
IR₀ — Raw ERA5 GRIB
IR₁ — Hourly Parquet + metadata.json
IR₂ — Chunked Parquet Tiles
IR₃ — merged.nc + QC (Unified Dataset)
IR₄ — Spatiotemporal Tensor + Stage 4 Contracts
IR₅ — Feature Tensors
IR₆ — Model‑Ready Datasets
IR₇ — Predictions + Evaluation Artifacts
IR₈ — Deployment Artifacts
```

Branch 2 currently implements IR₀ → IR₅. IR₆ → IR₈ are planned for later release.

---

## 🏗️ Stage Overview

### Stage 1 — Ingestion

#### Produces: IR₀ — Raw ERA5 GRIB

Artifacts:

- Multi‑variable GRIB files
- Raw coordinate grids
- `.idx` index files (optional)
- ZIP extraction (backward‑compatible)

Directory:

```code
data/raw/
```

Diagnostics: retry logs, directory validation.

### Stage 2 — Preprocessing

#### Consumes: IR₀

#### Produces: IR₁ — Hourly Parquet + metadata.json

Artifacts:

- Hourly Parquet slices
- `metadata.json` (canonical IR₁)
- `grib_metadata.json` (diagnostic IR₀)

Directory:

```code
data/intermediate/
data/metadata/
```

### Import‑Time Purity

Stage 2 modules must remain lightweight:

- No heavy libraries (`cfgrib`, `eccodes`, `xarray`) at module load
- Heavy imports allowed **only during conversion** (lazy import pattern)

This ensures deterministic startup and test stability.

### Stage 3 — Chunk Engine

#### Consumes: IR₁

#### Produces: IR₂ — Chunked Parquet Tiles

#### Also produces: IR₃ — merged.nc + QC (Stage 03 Merge)

Artifacts:

- Chunk parquet tiles
- Chunk metadata
- Unified merged dataset (`merged.nc`)
- QC reports (`merged_qc.json`)

Directory:

```code
data/chunks/
data/chunks_metadata/
data/intermediate/merged.nc
```

Diagnostics: planner logs, worker isolation logs, QC reports.

### Stage 4 — Spatiotemporal Compiler

#### Consumes: IR₂ + IR₃

#### Produces: IR₄ — Spatiotemporal Tensor + Contracts

Artifacts:

- Canonical spatiotemporal tensor
- Grid, mask, temporal, QC, metadata contracts

Directory:

```code
data/spatiotemporal/
```

Diagnostics: tensor shape logs, grid alignment checks, temporal continuity checks.

### Stage 5 — Feature Engineering

#### Consumes: IR₄

#### Produces: IR₅ — Feature Tensors

Artifacts:

- Derived meteorological features
- Pollution‑risk composites
- Rolling windows, anomalies, gradients
- Feature registry + metadata

Directory:

```code
data/features/
```

IR₅ is **complete** in Branch 2.

Ongoing work focuses on registry expansion and composite pollution‑risk features.

---

## 🔁 Full IR Evolution (IR₀ → IR₈)

Branch 2 uses a compiler‑style IR evolution:

```text
IR₀ — Raw ERA5 GRIB
    ↓ Stage 02 (Preprocessing)
IR₁ — Hourly Parquet + metadata.json
    ↓ Stage 03 Worker
IR₂ — Chunked Parquet Tiles
    ↓ Stage 03 Merge
IR₃ — merged.nc + QC
    ↓ Stage 04 Compiler
IR₄ — Spatiotemporal Tensor + Contracts
    ↓ Stage 05 Features
IR₅ — Feature Tensors
    ↓ Stage 06 (Planned)
IR₆ — Model‑Ready Datasets
    ↓ Stage 07 (Planned)
IR₇ — Predictions + Evaluation Artifacts
    ↓ Stage 08 (Planned)
IR₈ — Deployment Artifacts
```

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

Diagnostics emitted at every stage.

---

## 🔮 Future Roadmap (IR₆ → IR₈)

### Stage 6 — IR₆ Model‑Ready Datasets

- Train/val/test splits
- Normalized datasets
- Model manifests
- Versioned artifacts

### Stage 7 — IR₇ Predictions + Evaluation

- Predictions
- Regression metrics
- Residuals
- Diagnostic plots

### Stage 8 — IR₈ Deployment

- Docker images
- FastAPI inference server
- CI/CD manifests
- Batch + online inference endpoints

---

## 🧪 Testing Status

| Stage | Status | Notes |
| ------- | -------- | ------- |
| Stage 1 | ⚠️ WIP | Some tests failing (expected) |
| Stage 2 | ✅ Stable | Deterministic, restart-safe, import‑time purity enforced |
| Stage 3 | ✅ Stable | Schema-validated, parallel-safe |
| Stage 4 | ✅ Stable | Dense tensors, deterministic shapes |
| Stage 5 | ✅ Stable | Feature tensors complete |

---

## Operational Metrics (v2.0.0)

### Preprocessing Latency

- GRIB → Parquet conversion: **0.39 sec/file** (1512 files in 9 min 50 sec)
- Metadata extraction: **0.00095 sec/entry** (618,864 entries in 9 min 46 sec)
- GRIB inspection throughput: **292 files/sec** (1512 files in 5.18 sec)

### Chunk Engine Performance

- Chunk merge time: **0.45 sec/chunk (median)**
- Worker parallelism: **6 workers**
- Deterministic chunk boundaries: 100%
- NaN footprint (pre‑QC): **55,080 instantaneous**, **1.38M flux**
- Post‑QC NaNs: **0**

### Spatiotemporal Compiler

- Tensor build time: **7 sec/tensor (median)**
- Memory footprint: **128 MB**
- Tensor shape: **(9128, 9, 17, 12)**

### Tensor Diagnostics (Stage 4)

- Temporal coverage: **2019‑01‑01 → 2024‑12‑31 18:00**
- Variables stitched: **12** (t2m, d2m, u10, v10, msl, sp, tcc, blh, cape, cin, tco3, tcwv)
- Grid resolution: **9 × 17 (0.25° lat/lon)**
- NaNs: **0** (post‑QC)
- Infs: **0**
- Min/Max sanity: **validated via Stage‑3 QC**
- Coordinate consistency: **validated (monotonic time/lat/lon)**
- Tensor completeness: **9128 timestamps × 12 variables × 9 × 17 grid**

### Artifact Footprint

- Stage 1 raw: **0.43 GB**
- Stage 2 parquet: **5.0 GB**
- Stage 3 chunked: **128 MB**
- Stage 4 tensor: **128 MB**

### Determinism

- Reproducibility: 100%
- Artifact digests: SHA256 validated

### Boundary Hashing (C++ Module)

Artifact digests are computed using a deterministic C++ SHA‑256 module
(`src/cpp/deterministic_sha256.cpp`) exposed to Python via pybind11.
This ensures reproducible, verifiable digests across all pipeline stages.

## Performance Summary (v2.0.0)

| Metric | Value | Notes |
| -------- | -------- | ------- |
| GRIB → Parquet conversion | 0.39 sec/file | Deterministic, restart‑safe |
| Metadata extraction | 0.00095 sec/entry | 618,864 entries processed |
| GRIB inspection throughput | 292 files/sec | Parallel CF‑GRIB inspection |
| Chunk merge time | 0.45 sec/chunk (median) | 6‑worker parallelism |
| Worker parallelism | 6 workers | Config‑driven orchestrator |
| NaN footprint (pre‑QC) | 55,080 instantaneous; 1.38M flux | All removed post‑QC |
| Post‑QC NaNs | 0 | Deterministic merge guarantee |
| Tensor build time | 7 sec/tensor (median) | Dense IR₃ construction |
| Tensor shape | (9128, 9, 17, 12) | Multi‑year, multi‑variable |
| Stage 1 raw footprint | 0.43 GB | GRIB files (2019–2024) |
| Stage 2 parquet footprint | 5.0 GB | Hourly + variable‑split parquet |
| Stage 3 chunked footprint | 128 MB | Merged IR₂ artifact |
| Stage 4 tensor footprint | 128 MB | Final IR₃ tensor |
| Reproducibility | 100% | SHA256‑validated artifacts |

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

### Stage 5

```bash
python -m src.features_05 --config configs/stage5.yml
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

features:
    python -m src.features_05 --config configs/stage5.yml

all:
    make download
    make preprocess
    make core
    make spatiotemporal
    make features
```

---

## 🏛️ Branch Policy

- Stage 1 may fail during active development
- Stage 2 must remain deterministic and import‑time lightweight
- GRIB decoding occurs via runtime‑only lazy imports
- Stage 3 must remain deterministic
- Stage 4 must produce dense tensors
- `main` branch remains stable
- Stage 5 must produce deterministic IR₅ features
- `main` branch remains stable
- Branch 2 is safe to push

---

## 📈 Branch 1 → Branch 2 Snapshot

Branch 1 = MVP  <br>
Branch 2 = production‑aligned pipeline  <br>
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

**Brian Deng**  <br>
Los Angeles, CA

**Focus:**

- Climate analytics
- Hazard‑risk modeling
- ERA5‑based pipelines
- Geospatial ML
- Pollution‑risk analytics
