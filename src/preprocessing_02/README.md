# preprocessing_02 — ERA5 GRIB Preprocessing Pipeline (Stage 2)

`preprocessing_02` implements the full Stage 2 preprocessing pipeline for ERA5 data.
Stage 2 transforms raw ERA5 monthly ZIP archives and GRIB files into clean,
column‑oriented Parquet files ready for feature engineering, merging, and modeling.

Stage 2 is the bridge between raw meteorological data and structured ML‑ready data.

---

## 🎯 Purpose

Stage 2 performs three core operations:

1. Unzip monthly ERA5 ZIP archives → multi‑variable GRIBs
2. Inspect all GRIB files → generate `.idx` indexes + metadata
3. Convert GRIB → Parquet (single‑variable + multi‑variable)

This produces a complete intermediate dataset in:

```markdown
data/intermediate/
```

which Stage 3 parallelization and Stage 4 merging will consume.

---

## 🧭 Branch Philosophy

### Branch 1 — MVP

A minimal preprocessing pipeline designed for early prototyping.

- Handles only single‑variable GRIBs
- No ZIP ingestion
- No metadata extraction
- No schema validation
- No parallelization
- Converts one GRIB → one Parquet
- Supports early feature engineering and model experimentation

### Branch 2 — Full Pipeline

A production‑grade preprocessing stage.

- Full monthly ZIP ingestion
- Multi‑variable GRIB support
- GRIB metadata extraction
- `.idx` generation for fast cfgrib access
- Schema + dimension validation
- Unified pipeline orchestration
- Structured logging
- Error handling + retries
- Ready for Branch 3 parallelization

Branch 2 is the first branch where Stage 2 becomes a real pipeline, not a collection of utilities.

---

## 📁 Folder Structure

```markdown
preprocessing_02/
│
├── __init__.py
│
├── unzip_grib.py
│   Extract monthly ZIP archives into GRIB files.
│   Branch 1: placeholder
│   Branch 2: full ZIP ingestion
│
├── inspect_grib.py
│   Inspect GRIB structure, variables, dimensions.
│   Generates cfgrib index (.idx) files.
│   Branch 1: single-variable only
│   Branch 2: multi-variable support
│
├── convert_grib_to_parquet.py
│   Convert GRIB → Parquet.
│   Branch 1: single-variable conversion
│   Branch 2: multi-variable conversion + metadata
│
└── run_preprocessing.py
    Unified Stage 2 orchestrator.
    Runs: unzip → inspect → convert.
    Required for Branch 3 parallelization.
```

## 🔧 How Stage 2 Works (Full Branch 2 Flow)

```markdown
era5_YYYY_MM.zip
↓ unzip_grib.py
era5_YYYY_MM.grib
↓ inspect_grib.py
era5_YYYY_MM.grib.<hash>.idx
↓ convert_grib_to_parquet.py
era5_YYYY_MM.parquet
↓
data/intermediate/
```

Single‑variable GRIBs follow the same flow but skip the ZIP step.

---

## 📦 Outputs

Stage 2 produces:

- Single‑variable Parquet files
`2m_temperature_YYYY_MM.parquet`

- Multi‑variable Parquet files
`era5_YYYY_MM.parquet`

- cfgrib index files
`*.grib.<hash>.idx`

- (Branch 3+) metadata JSON
`stage2_metadata.json`

---

## 🧪 Testing Strategy

### Branch 1

- GRIB → Parquet smoke tests
- Validate Parquet schema
- Validate directory creation

### Branch 2

- Multi‑variable GRIB inspection tests
- `.idx` generation tests
- Schema + dimension validation
- Multi‑variable conversion tests
- Full pipeline orchestration tests
- Error handling + retry tests

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

This runs the full pipeline:

```markdown
unzip → inspect → convert
```

---

## 🔮 Future Enhancements (Branch 3+)

- Parallel GRIB → Parquet conversion
- Distributed ingestion (Ray/Dask)
- Metadata lineage tracking
- Automatic variable filtering
- Spatial/temporal normalization
- Multi‑variable merging
- Pipeline run IDs + audit logs
- Environment validation (eccodes, cfgrib, xarray)

---

## 📌 Notes

Stage 2 is intentionally modular:

- Each operation is isolated (`unzip`, `inspect`, `convert`)
- The orchestrator (`run_preprocessing.py`) ties them together
- Branch 3 parallelization wraps the orchestrator, not the utilities

This keeps the pipeline clean, testable, and scalable.
