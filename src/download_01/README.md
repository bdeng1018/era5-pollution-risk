# download_01 — ERA5 Data Retrieval (Branch 2)

This stage retrieves raw ERA5 Single‑Level reanalysis data from the Copernicus Data Store (CDS).
**Branch 1 (MVP)** provides minimal ingestion logic.
**Branch 2** upgrades this into a robust, reproducible, multi‑year ingestion system suitable for research, industry, and government workflows.

---

## 🎯 Purpose

- Build ERA5 API requests for selected variables, years, and months
- Download raw GRIB or ZIP files into `data/raw/era5/`
- Provide clean, modular entrypoints for preprocessing and conversion stages
- Ensure reproducibility through structured logging, environment validation, and config‑driven execution

---

## 🧭 Branch 1 (MVP) Scope

Branch 1 includes **two lightweight download scripts**, each serving a distinct purpose.

### 1. Minimal single‑variable downloader

`download_era5_single.py`

- Downloads **one variable**
- For **one year + one month**
- Minimal request (1 day, 1 hour)
- Fast and notebook‑friendly
- Ideal for smoke tests, debugging, and verifying CDS connectivity

### 2. Monthly ZIP downloader

`download_era5_monthly.py`

- Downloads **all variables** listed in `variables.yml`
- For **all years + months** in `years.yml` and `months.yml`
- Full hourly resolution
- Saves each month as a **ZIP of GRIB files**
- Produces the complete dataset required for Branch‑1 modeling

Branch 1 intentionally excludes:

- retries
- parallelization
- metadata tracking
- environment validation
- multi‑year orchestration beyond simple loops

This is sufficient for a minimal pollution‑risk model.

---

## 🚀 Branch 2 (Production‑Grade Ingestion)

Branch 2 expands this stage into a robust, reproducible ingestion system:

- Retry logic with exponential backoff
- Metadata tracking (timestamps, file sizes, run status)
- Environment validation (CDS credentials, directory structure)
- Multi‑year ingestion across all configured years/months
- Structured logging to console and file
- Config‑driven execution via YAML files
- Graceful error handling and recovery

### Intentional Branch 2 scope limits

Branch 2 does **not** include:

- parallelization (added in Branch 3)
- global ingestion (scope defined in configs)
- heavy MLOps stack (MLflow/Docker optional in later stages)
- multi‑variable orchestration beyond monthly ingestion

This keeps Branch 2 clean, believable, and production‑aligned.

---

## 📁 Files in This Folder

```text
download_01/
│
├── __init__.py
├── download_era5_single.py     # Branch 2 single-variable ingestion with retries + metadata
└── download_era5_monthly.py    # Branch 1 monthly ingestion (to be upgraded in Branch 2)
```

---

## 🔧 How It Works (Conceptual Flow)

```text
variables.yml + years.yml + months.yml
↓
environment validation (CDS credentials, directories)
↓
build ERA5 API request (full-month/full-day in Branch 2)
↓
CDS API client with retry logic
↓
download GRIB or ZIP file
↓
metadata logging (timestamps, file size)
↓
save to data/raw/era5/
```

---

## 🧩 Dependencies

This stage relies on:

- `src/utils/config.py` — load YAML configs
- `src/utils/paths.py` — resolve directories
- `src/utils/logging.py` — structured logging

Branch 2 also uses:

- `os` — environment validation
- `time` — retry backoff
- `pathlib.Path` — metadata inspection

---

## 🧪 Testing

### Branch 1 tests

- Smoke tests for single‑variable downloads
- Ensure ZIP/GRIB files are created

### Branch 2 tests

- Retry logic tests
- Metadata tests
- Environment validation tests
- Multi‑year ingestion tests

---

## ▶️ Running This Stage

From the project root:

```bash
make download
```

This calls the `main()` function inside `download_era5_monthly.py` (Branch 1) or
the upgraded Branch 2 version once implemented.

---

## 📌 Notes

Branch 2 transforms Stage 1 from a minimal downloader into a **reliable,
reproducible ingestion system**.
It remains intentionally scoped to avoid premature complexity while supporting
downstream preprocessing, feature engineering, and modeling stages.
