# preprocessing_02 — Stage 2 ERA5 GRIB → Parquet Pipeline (Branch 2)

`preprocessing_02` implements the full **Stage 2** preprocessing pipeline for ERA5 data.
Stage 2 transforms raw ERA5 GRIB files into **hourly** and **static** column‑oriented Parquet files ready for:

- Stage 3 chunk planning
- Stage 4 spatiotemporal alignment
- Stage 5 feature engineering

Stage 2 is the bridge between raw meteorological archives and structured ML‑ready data.

---

## 🎯 Purpose

Stage 2 performs four core operations:

1. **Inspect** GRIB files (diagnostic-only, IR₀)
2. **Convert** GRIB → **HOURLY or STATIC Parquet**
3. **Emit two metadata files**:
   - `grib_metadata.json` (diagnostic IR₀)
   - `metadata.json` (canonical IR₁)
4. **Prepare intermediate directory layout** for Stage 3

ZIP ingestion is supported only for backward compatibility; Branch 2 uses GRIB‑only ingestion.

---

## 🧭 Branch Philosophy

### Branch 1 — MVP Pipeline

A minimal preprocessing workflow:

- Single‑variable GRIBs
- No metadata extraction
- No parallelization
- One GRIB → one Parquet

Useful for early experimentation.

### Branch 2 — Production‑Grade Preprocessing

A robust, scalable Stage 2 pipeline:

- Multi‑variable GRIB support
- GRIB metadata extraction (IR₀)
- `.idx` generation for fast cfgrib access
- Schema + dimension validation
- Filename → ERA5 shortName mapping
- Hourly slicing + Parquet generation
- Static variable handling
- Canonical Parquet metadata (IR₁)
- Structured logging + error handling
- Parallel conversion
- Deterministic directory layout

Branch 2 is the first branch where Stage 2 becomes a real pipeline.

### Branch 3 - AI/LLM/RAG Enhancements (Future)

Stage 2 remains deterministic, but Branch 3 may introduce:

- LLM‑assisted GRIB diagnostics
- RAG‑based metadata search
- Natural‑language summaries of IR₀/IR₁
- Agentic troubleshooting (“why did this GRIB fail conversion?”)

These tools will live in separate modules and will not modify deterministic Stage 2 behavior.

---

## 📁 Folder Structure

```text
preprocessing_02/
│
├── __init__.py
│   Package documentation (no public API)
│
├── unzip_grib.py
│   Optional ZIP → GRIB extraction (backward-compatible)
│
├── inspect_grib.py
│   GRIB-level inspection (diagnostic-only)
│   Writes grib_metadata.json (IR₀)
│
├── convert_grib_to_parquet.py
│   GRIB → HOURLY or STATIC Parquet conversion
│
├── metadata_parquet.py
│   Canonical Parquet metadata.json builder (IR₁)
│
└── run_preprocessing.py
    Unified Stage 2 orchestrator:
    unzip → inspect → convert → grib_metadata.json → metadata.json
```

---

## 🔧 How Stage 2 Works (Branch 2 Flow)

```text
GRIB file
↓ inspect_grib.py
grib_metadata.json (IR₀ diagnostic)
↓ convert_grib_to_parquet.py
<variable>_<timestamp>.parquet
↓ metadata_parquet.py
metadata.json (IR₁ canonical)
↓
data/intermediate/
```

ZIP ingestion is optional and used only for backward compatibility.

---

## 📦 Outputs

### Hourly Parquet Files (IR₁)

```code
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
```

Example:

```code
data/intermediate/2023/01/t2m/t2m_2023-01-01T00:00.parquet
data/intermediate/2023/01/u10/u10_2023-01-01T01:00.parquet
```

### Static Parquet Files

```code
data/intermediate/2023/01/lsm/lsm_static.parquet
```

### GRIB Diagnostic Metadata (IR₀)

```code
metadata/grib_metadata.json
```

Contains raw GRIB-level inspection results.

### Canonical Parquet Metadata (IR₁)

```code
metadata/metadata.json
```

Contains normalized hourly timestamps and Parquet paths.

### cfgrib Index Files

`*.grib.<hash>.idx`

---

## 🗂 Canonical Hourly Metadata (`metadata.json`)

Stage 2 produces a **Parquet-only** metadata.json containing **only instantaneous hourly variables:**

```json
{
  "2023-01-01T00:00": {
    "variable": "t2m",
    "path": "/path/to/parquet",
    "year": 2023,
    "month": 1,
    "dtype": "float32",
    "shape": [721, 1440]
  }
}
```

### ❗ Exclusions (intentional)

- **Flux/accumulated variables**
(`slhf`, `sshf`, `ssr`, `str`, `tp`, etc.)
→ accumulated semantics → excluded from IR₁

- **Static variables**
(`lsm`)
→ no time dimension → excluded from IR₁

These variables are written to Parquet but **not** included in metadata.json.

### ✔ Stage 3 uses metadata.json exclusively

GRIB metadata (IR₀) plays **no role** in Stage 3.

This is the Stage 2 → Stage 3 contract.

---

## 🧪 Testing Strategy

### Branch 1

- GRIB → Parquet smoke tests
- Validate hourly timestamps
- Validate Parquet schema
- Validate directory creation

### Branch 2

- Multi‑variable GRIB inspection tests
- `.idx` generation tests
- Schema + dimension validation
- Multi‑variable conversion tests
- Hourly slicing tests
- Static variable handling tests
- Full pipeline orchestration tests
- `metadata.json` correctness tests
- Stage 3‑readiness diagnostics

---

## ▶️ Running Stage 2

From the project root:

```bash
python -m src.preprocessing_02.run_preprocessing
```

Or via Makefile:

```bash
make preprocess
```

Pipeline flow:

```code
inspect → convert → grib_metadata.json → metadata.json
```

ZIP extraction is optional.

---

## 🔮 Future Enhancements (Branch 3+)

- Distributed GRIB → Parquet conversion (Ray/Dask)
- Chunk‑based parallelization
- Metadata lineage tracking
- Automatic variable filtering
- Spatial + temporal normalization
- Multi‑variable merging
- Pipeline run IDs + audit logs
- Environment validation (eccodes, cfgrib, xarray)
- LLM-assisted diagnostics + summaries

---

## 📌 Notes

Stage 2 is intentionally modular:

- Each operation is isolated (`inspect`, `convert`, `metadata`)
- The orchestrator (`run_preprocessing.py`) ties them together
- Branch 3 parallelization wraps the orchestrator, not the utilities

This keeps the pipeline clean, testable, and scalable.
