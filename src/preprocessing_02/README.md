# preprocessing_02 — ERA5 GRIB → Parquet Conversion

This stage converts ERA5 GRIB files into clean, analysis‑ready Parquet files for
downstream feature engineering and modeling.  
**Branch 1 (MVP)** processes *only the single‑variable GRIB file* produced by
`download_era5_single.py`.  
**Branch 2** expands this into a full multi‑variable preprocessing suite.

---

## 🎯 Purpose

- Load raw GRIB files produced in `download_01`
- Convert GRIB → xarray → pandas → Parquet
- Produce lightweight, column‑oriented data for fast feature engineering
- Maintain a clean, modular preprocessing stage that scales in Branch 2

---

## 🧭 Branch 1 (MVP) Scope

Branch 1 keeps preprocessing intentionally simple:

- Convert **only single‑variable GRIBs** (e.g., `2m_temperature_2023_09.grib`)
- Minimal logging (start/end of each conversion)
- No schema validation
- No metadata extraction
- No parallelization
- No multi‑variable ingestion
- No multi‑year orchestration

This is sufficient to support a minimal pollution‑risk model.

---

## 🚀 Branch 2 (Full Pipeline) Scope

Branch 2 expands preprocessing into a production‑grade stage:

- GRIB metadata inspection  
- Variable/dimension validation  
- Schema enforcement  
- Multi‑variable ingestion (monthly ZIPs)  
- Parallel GRIB → Parquet conversion  
- Metadata tracking (timestamps, hashes, run IDs)  
- Error handling + retries  
- Structured logging to file  

---

## 📁 Files in This Folder

```markdown
preprocessing_02/
│
├── __init__.py
├── convert_grib_to_parquet.py   # Branch 1: single-variable conversion
├── inspect_grib.py              # Branch 1: single-variable inspection
└── unzip_grib.py                # Branch 2: monthly ZIP ingestion
```

---

## 🔧 How It Works (Conceptual Flow)

```markdown
single-variable GRIB file
↓
open with cfgrib / xarray
↓
convert to pandas DataFrame
↓
write to Parquet
↓
data/intermediate/
```

---

## 🧩 Dependencies

This stage relies on:

- `src/utils/paths.py` — resolve directories  
- `src/utils/logging.py` — lightweight logging  
- `xarray` + `cfgrib` — GRIB ingestion  
- `pandas` — DataFrame + Parquet writing  

---

## 🧪 Testing

Branch 1:
- smoke tests for single-variable GRIB → Parquet  
- ensure Parquet files are created  

Branch 2:
- GRIB metadata validation tests  
- schema tests  
- multi-variable ingestion tests  
- parallel conversion tests  

---

## ▶️ Running This Stage

From the project root:

```bash
make preprocess
```

This calls the `main()` function inside `convert_grib_to_parquet.py`.

---

## 🔮 Future Enhancements (Branch 2)

- Parallel GRIB → Parquet conversion  
- Automatic variable filtering  
- Spatial/temporal normalization  
- Metadata JSON per file  
- Error handling + retries  
- Multi‑year ingestion  
- Multi‑variable ZIP extraction + conversion  

---

## 📌 Notes

Branch 1 is intentionally lightweight.  
Its primary goal is to produce clean Parquet files so feature engineering can begin immediately.