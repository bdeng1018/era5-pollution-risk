# preprocessing_02 — ERA5 GRIB Preprocessing Pipeline (Stage 2)

`preprocessing_02` implements the full Stage 2 preprocessing pipeline for ERA5 data. Stage 2 transforms raw ERA5 GRIB files into **hourly**, column‑oriented Parquet files ready for Stage 3 chunk planning, Stage 4 spatiotemporal alignment, and Stage 5 feature engineering.

Stage 2 is the bridge between raw meteorological data and structured ML‑ready data.

---

## 🎯 Purpose

Stage 2 performs three core operations:

1. **Inspect** all GRIB files to validate structure and generate `.idx` indexes
2. **Convert** GRIB → **HOURLY Parquet** (single‑variable and multi‑variable)
3. **Emit unified metadata** describing variables, timestamps, and file paths

This produces a complete intermediate dataset in `intermediate/` consumed by Stage 3.

---

## 🧭 Branch Philosophy

### Branch 1 — MVP

A minimal preprocessing pipeline designed for early prototyping:

- Handles only single‑variable GRIBs
- No ZIP ingestion
- No metadata extraction
- No schema validation
- No parallelization
- Converts one GRIB → one Parquet
- Supports early feature engineering and model experimentation

### Branch 2 — Full Pipeline

A production‑grade preprocessing stage.

- Multi‑variable GRIB support
- GRIB metadata extraction
- `.idx` generation for fast cfgrib access
- Schema and dimension validation
- Filename → ERA5 shortName mapping
- Hourly slicing and Parquet generation
- Unified `metadata.json`
- Structured logging
- Error handling
- Ready for Branch 3 parallelization

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
│   Convert GRIB → HOURLY Parquet.
│   Branch 1: filename→shortName mapping + hourly conversion
│   Branch 2: multi-variable conversion + unified metadata
│
└── run_preprocessing.py
    Unified Stage 2 orchestrator.
    Runs: unzip → inspect → convert → metadata.
    Required for Branch 3 parallelization.
```

## 🔧 How Stage 2 Works (Branch 2 Flow)

```markdown
era5_YYYY_MM.zip
↓ unzip_grib.py
era5_YYYY_MM.grib
↓ inspect_grib.py
era5_YYYY_MM.grib.<hash>.idx
↓ convert_grib_to_parquet.py
<shortName>_<timestamp>.parquet
↓
data/intermediate/
```

Single‑variable GRIBs follow the same flow but skip the ZIP step.

---

## 📦 Outputs

Stage 2 produces:

- Hourly Parquet files

```markdown
t2m_2023_01_2023-01-01T00:00.parquet
u10_2023_01_2023-01-01T01:00.parquet
...
```

- cfgrib index files

`*.grib.<hash>.idx`

- Unified hourly metadata

`metadata.json`

Structure:

```markdown
{
  "variables": {
    "t2m": {
      "2023-01-01T00:00": "/path/to/parquet",
      ...
    },
    "u10": { ... },
    ...
  },
  "timestamps": [
    "2023-01-01T00:00",
    ...
  ]
}
```

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
- Full pipeline orchestration tests
- `metadata.json` structure tests

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
unzip → inspect → convert → metadata
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

- Each operation is isolated (`unzip`, `inspect`, `convert`)
- The orchestrator (`run_preprocessing.py`) ties them together
- Branch 3 parallelization wraps the orchestrator, not the utilities

This keeps the pipeline clean, testable, and scalable.
