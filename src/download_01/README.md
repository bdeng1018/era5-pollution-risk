# download_01 — ERA5 Data Retrieval (Stage 1)

`download_01` implements the ERA5 data ingestion layer. Stage 1 retrieves raw ERA5 Single‑Level reanalysis data from the Copernicus Data Store (CDS) and writes GRIB files into the `raw/` directory. Stage 1 is intentionally simple in Branch 1 and becomes production‑grade in Branch 2.

Stage 1 is the entrypoint of the entire pipeline.

---

## 🎯 Purpose

Stage 1 performs three core responsibilities:

1. **Build ERA5 API requests** for selected variables, years, and months
2. **Download raw GRIB files** into `raw/`
3. **Emit metadata** describing download status, timestamps, and file paths

This provides the raw meteorological data consumed by Stage 2 preprocessing.

---

## 🧭 Branch Philosophy

### Branch 1 — MVP

A minimal ingestion layer designed for early prototyping:

- Single‑variable downloader
- Minimal request (one day, one hour)
- Simple monthly downloader
- No retries
- No metadata tracking
- No environment validation
- No parallelization

Branch 1 is sufficient for smoke tests and early model experimentation.

### Branch 2 — Full Ingestion Layer

A production‑grade ingestion system:

- Multi‑year ingestion
- Retry logic with exponential backoff
- Structured logging
- Metadata tracking (timestamps, file sizes, run status)
- Environment validation (CDS credentials, directory structure)
- Config‑driven execution
- Graceful error handling and recovery

Branch 2 transforms Stage 1 into a reliable, reproducible ingestion layer.

---

## 📁 Folder Structure

```text
download_01/
│
├── __init__.py
├── download_era5_single.py     # single‑variable ingestion with retries and metadata
└── download_era5_monthly.py    # monthly ingestion across variables, years, and months
└── paths.py                    # directory resolution for `raw/`, `metadata/`, and logs
```

---

## ⚙️ How Stage 1 Works (Branch 2 Flow)

```text
Variables, years, and months from `variables.yml`, `years.yml`, and `months.yml`
↓
Environment validation (CDS credentials, directory structure)
↓
Build ERA5 API request
↓
CDS API client with retry logic
↓
Download GRIB file
↓
Write metadata (timestamps, file size, run status)
↓
Save to `raw/`
```

Stage 1 downloads **GRIB files only**. ZIP ingestion is not part of Branch 2.

---

## 📦 Outputs

Stage 1 produces:

**Raw GRIB files**
`t2m_2023_01.grib`
`u10_2023_01.grib`

**Download metadata**
`metadata.json` containing variables, timestamps, file paths, and run status.

---

## 🧪 Testing Strategy

### Branch 1

- Smoke tests for single‑variable downloads
- Validate GRIB file creation

### Branch 2

- Retry logic tests
- Metadata tests
- Environment validation tests
- Multi‑year ingestion tests
- Error handling tests

---

## ▶️ Running Stage 1

From the project root:

```bash
make download
```

Or directly:

```bash
python -m src.download_01.download_era5_monthly
```

---

## 📌 Notes

Stage 1 is intentionally simple but foundational:

- Branch 1 provides minimal ingestion
- Branch 2 provides production‑grade ingestion
- Stage 2 preprocessing depends entirely on Stage 1 outputs

A clean, reliable Stage 1 ensures the entire pipeline remains reproducible and scalable.
