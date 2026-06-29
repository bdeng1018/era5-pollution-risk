# download_01 — ERA5 Data Retrieval

This stage retrieves raw ERA5 Single‑Level reanalysis data from the Copernicus Data Store (CDS).  
**Branch 1 (MVP)** provides two lightweight download modes that support the minimal ingestion pipeline.  
**Branch 2** expands this into a production‑grade ingestion system.

---

## 🎯 Purpose

- Build ERA5 API requests for selected variables, years, and months  
- Download raw GRIB or ZIP files into `data/raw/era5/`  
- Provide clean, modular entrypoints for preprocessing and conversion stages  

---

## 🧭 Branch 1 (MVP) Scope

Branch 1 includes **two download scripts**, each serving a distinct purpose.

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

## 🚀 Branch 2 (Full Pipeline) Scope

Branch 2 will expand this stage into a production‑grade ingestion system:

- Retry logic with exponential backoff  
- Parallel downloads  
- Metadata tracking (timestamps, hashes, run IDs)  
- Environment validation (Python, cfgrib, xarray, eccodes)  
- Multi‑year ingestion  
- Structured logging to file  
- Error handling and graceful recovery  

---

## 📁 Files in This Folder

```markdown
download_01/
│
├── __init__.py
├── download_era5_single.py     # minimal single-variable downloader
└── download_era5_monthly.py    # full monthly ingestion (Branch 1)
```

---

## 🔧 How It Works (Conceptual Flow)

```markdown
variables.yml + years.yml + months.yml
↓
build ERA5 API request
↓
CDS API client
↓
download GRIB or ZIP file
↓
save to data/raw/era5/
```

---

## 🧩 Dependencies

This stage relies on:

- `src/utils/config.py` — load YAML configs  
- `src/utils/paths.py` — resolve directories  
- `src/utils/logging.py` — lightweight logging  

---

## 🧪 Testing

Branch 1:

- Smoke tests for single‑variable downloads  
- Ensure ZIP/GRIB files are created  

Branch 2:

- Retry logic tests  
- Metadata tests  
- Environment validation tests  

---

## ▶️ Running This Stage

From the project root:

```bash
make download
```

This calls the `main()` function inside `download_era5_monthly.py`.

---

## 📌 Notes

Branch 1 is intentionally lightweight.  
Its primary goal is to produce raw ERA5 files so preprocessing can begin immediately.