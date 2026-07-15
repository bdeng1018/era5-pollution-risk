# preprocessing_02 — Stage 2 ERA5 GRIB → Parquet Pipeline (Branch 2)

`preprocessing_02` implements the full **Stage 2** preprocessing pipeline for ERA5 data.
Stage 2 transforms raw ERA5 GRIB files into **hourly** and **static** column‑oriented
Parquet files ready for:

- Stage 3 chunk planning and merge‑readiness checks
- Stage 4 spatiotemporal alignment
- Stage 5 feature engineering

Stage 2 is the bridge between raw meteorological archives and structured ML‑ready data.

---

## 🎯 Purpose

Stage 2 performs four core operations:

1. **Unzip** ERA5 monthly ZIP bundles (optional, backward‑compatible)
2. **Inspect** GRIB files (diagnostic-only)
3. **Convert** GRIB → **HOURLY or STATIC Parquet**
4. **Emit two metadata files**:
   - `grib_metadata.json` (diagnostic IR₀)
   - `metadata.json` (canonical IR₁)

The Parquet dataset in `data/intermediate/` is consumed by Stage 3.

---

## 🧭 Branch Philosophy

### Branch 1 — MVP Pipeline

A minimal preprocessing workflow for early prototyping:

- Single‑variable GRIBs only
- No ZIP ingestion
- No metadata extraction
- No parallelization
- One GRIB → one Parquet

Useful for early feature engineering and model experimentation.

### Branch 2 — Full Production Pipeline

A robust, scalable preprocessing stage:

- Multi‑variable GRIB support
- GRIB metadata extraction
- `.idx` generation for fast cfgrib access
- Schema and dimension validation
- Filename → ERA5 shortName mapping
- Hourly slicing and Parquet generation
- Static variable handling
- Unified **hourly** `grib_metadata.json` (IR₀ diagnostic)
- Unified **hourly** `metadata.json` (IR₁ canonical Parquet metadata)
- Structured logging and error handling
- Parallel conversion
- Ready for Branch 3 parallelization

Branch 2 is the first branch where Stage 2 becomes a real pipeline, not a collection of utilities.

---

## 📁 Folder Structure

```markdown
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
│   Writes grib_metadata.json
│
├── convert_grib_to_parquet.py
│   GRIB → HOURLY or STATIC Parquet conversion
│
├── metadata_parquet.py
│   Canonical Parquet-only metadata.json builder (IR₁)
│
└── run_preprocessing.py
    Unified Stage 2 orchestrator:
    unzip → inspect → convert → grib_metadata.json → metadata.json
```

---

## 🔧 How Stage 2 Works (Branch 2 Flow)

```markdown
era5_YYYY_MM.zip (optional)
↓ unzip_grib.py
era5_YYYY_MM.grib
↓ inspect_grib.py
grib_metadata.json (diagnostic)
↓ convert_grib_to_parquet.py
<variable>_<timestamp>.parquet
↓ metadata_parquet.py
metadata.json (canonical)
↓
data/intermediate/
```

Single‑variable GRIBs follow the same flow but skip the ZIP step.

---

## 📦 Outputs

### Hourly Parquet Files (IR₁)

Directory layout:

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
  },
  ...
}
```

### ❗ Exclusions (intentional)

- **Flux/accumulated variables**
(`slhf`, `sshf`, `ssr`, `str`, `tp`, etc.)
→ different grid + accumulated semantics → **excluded**

- **Static variables**
(`lsm`)
→ no time dimension → **excluded**

These variables are written to Parquet but **not** included in metadata.json.

### ✔ Stage 3 uses metadata.json exclusively

GRIB metadata plays **no role** in Stage 3.

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
- Schema and dimension validation
- Multi‑variable conversion tests
- Hourly slicing tests
- Static variable handling tests
- Full pipeline orchestration tests
- `metadata.json` correctness tests
- Stage 3‑readiness diagnostics (timestamp + grid alignment)

---

## ▶️ Running Stage 2

From the project root:

```bash
python -m src.preprocessing_02.run_preprocessing
```

or via Makefile:

```bash
make preprocess
```

Pipeline flow:

```markdown
unzip → inspect → convert → grib_metadata.json → metadata.json
```

---

## 🔮 Future Enhancements (Branch 3+)

- Distributed GRIB → Parquet conversion (Ray/Dask)
- Chunk‑based parallelization
- Metadata lineage tracking
- Automatic variable filtering
- Spatial and temporal normalization
- Multi‑variable merging
- Pipeline run IDs and audit logs
- Environment validation (eccodes, cfgrib, xarray)

---

## 📌 Notes

Stage 2 is intentionally modular:

- Each operation is isolated (`unzip`, `inspect`, `convert`, `metadata`)
- The orchestrator (`run_preprocessing.py`) ties them together
- Branch 3 parallelization wraps the orchestrator, not the utilities

This keeps the pipeline clean, testable, and scalable.
