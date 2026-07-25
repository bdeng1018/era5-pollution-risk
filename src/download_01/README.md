# download_01 — Stage 1 ERA5 Data Retrieval (Branch 2)

`download_01` implements the ERA5 data ingestion layer. Stage 1 retrieves raw ERA5 **Single‑Level** reanalysis data from the Copernicus Data Store (CDS) and writes **GRIB** files into the deterministic directory layout:

```code
data/raw/era5/<year>/<month>/<variable>/
```

Stage 1 is the entrypoint of the entire pipeline and provides the raw meterological data consumed by Stage 2 preprocessing.

---

## 🎯 Purpose

Stage 1 performs three core responsibilities:

1. **Build ERA5 API requests** for configured variables, years, and months
2. **Download raw GRIB files** into the structured raw directory
3. **Emit metadata** describing download status, timestamps, and file paths

This forms the foundation for deterministic ingestion across Branch 2.

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

Useful for smoke tests and early experimentation.

### Branch 2 — Production‑Grade Ingestion

A robust ingestion system designed for reproducibility:

- Multi‑year, multi‑variable ingestion
- Retry logic with exponential backoff
- Structured logging
- Metadata tracking (timestamps, file sizes, run status)
- Environment validation (CDS credentials, directory structure)
- Config‑driven execution via YAML
- Graceful error handling and recovery
- Long‑form ERA5 variable naming for consistency across CDSAPI, raw layout, metadata, and downstream stages

Branch 2 transforms Stage 1 into a reliable ingestion layer for large-scale ERA5 pipelines.

### Branch 3 — AI/LLM/RAG Enhancements (Future)

Stage 1 remains deterministic, but Branch 3 may introduce:

- LLM‑assisted ingestion diagnostics
- RAG‑based metadata search
- Natural‑language ingestion summaries
- Agentic troubleshooting (“why did this variable fail?”)

These tools will live in separate modules and will not modify deterministic Stage 1 behavior.

---

## 📁 Folder Structure

```text
download_01/
│
├── __init__.py
├── download_era5_single.py     # single‑variable ingestion with retries + metadata
├── download_era5_monthly.py    # multi‑variable monthly ingestion
└── paths.py                    # directory resolution for raw/, metadata/, configs/, logs
```

---

## ⚙️ How Stage 1 Works (Branch 2 Flow)

```text
variables.yml, years.yml, months.yml
↓
Environment validation (CDS credentials, directory structure)
↓
Build ERA5 API request (long‑form variable names)
↓
CDS API client with retry logic
↓
Download GRIB file
↓
Write metadata (timestamps, file size, run status)
↓
Save to raw/era5/<year>/<month>/<variable>/
```

Stage 1 downloads **GRIB files only**.

Branch 2 removes ZIP ingestion entirely because GRIB-only ingestion:

- simplifies retry logic
- reduces failure surface area
- improves metadata granularity
- aligns with Stage 2 variable‑specific preprocessing

---

## 📦 Outputs

### Raw GRIB files

Stored under:

`data/raw/era5/<year>/<month>/<variable>/<variable>_<year>_<month>.grib`

Example:

`data/raw/era5/2023/01/10m_u_component_of_wind/10m_u_component_of_wind_2023_01.grib`

### Download metadata

Stored under:

`data/metadata/metadata_<variable>_<year>_<month>.json`

Metadata includes:

- variable
- year
- month
- success flag
- config_valid flag
- outfile (absolute GRIB path)

Timestamps and file sizes are added in Stage 2 after GRIB inspection.

---

## 📐 Design Guarantees (Stage 1 Contract)

### 1. Deterministic Directory Layout

Every GRIB file is stored under:

`data/raw/era5/<year>/<month>/<variable>/<variable>_<year>_<month>.grib`

Stable across Branch 1, Branch 2, and Branch 3.

### 2. Metadata Always Exists

For every attempted download (success or failure), Stage 1 writes:

`data/metadata/metadata_<variable>_<year>_<month>.json`

Metadata is guaranteed to contain:

- variable
- year
- month
- success flag
- config_valid flag
- outfile (absolute GRIB path)

### 3. No Partial Files

If a download fails, Stage 1 ensures:

- no corrupted GRIB files remain
- metadata marks the attempt as failed
- Stage 2 will never ingest partial data

### 4. Idempotent Execution

Re‑running Stage 1:

- never overwrites existing GRIB files
- never deletes existing metadata
- only downloads missing data
- is safe for long‑running ingestion jobs

### 5. Config‑Driven Behavior

All ingestion behavior is determined by:

- `variables.yml`
- `years.yml`
- `months.yml`

### 6. GRIB‑Only Ingestion

One variable per file → simpler, safer, more consistent.
This simplifies downstream processing and retry logic.

---

## 🧪 Testing Strategy

### Branch 1

- Smoke tests
- Validate GRIB creation

### Branch 2

- Retry logic tests (exponential backoff + failure modes)
- Metadata logging tests (success/failure metadata correctness)
- Environment validation tests (credentials + directory + config)
- Multi‑year + multi-variable ingestion tests
- Error handling tests
- Monkeypatch tests for `Paths()` and `cdsapi.Client`

These tests ensure **full functional coverage** of Stage 1.

---

## ➕ Adding New Variables

Add long‑form ERA5 variable names to `configs/variables.yml`:

```yaml
variables:
  - 2m_temperature
  - surface_pressure
  - total_precipitation
  - 10m_u_component_of_wind
```

Run Stage 1:

```bash
make download
```

Stage 1 automatically ingests the new variable across all configured years/months.

---

## ▶️ Running Stage 1

From the project root:

```bash
make download
```

Or directly:

```bash
python -m src.download_01.download_era5_monthly --config configs/config.yml
```

---

## 📌 Operational Notes

Stage 1 ingestion is **I/O-bound** and interacts with the CDS queue:

- 60–90 seconds per variable per month
- Larger variables take longer
- Retry logic handles CDS queue delays
- Skip logic prevents overwriting existing GRIBs
- Metadata is always written

---

## 📊 Performance Benchmarks

| Variable Type | Avg. GRIB Size | Download Time | Notes |
|---------------|----------------|---------------|-------|
| Temperature / Pressure | 2-5 MB | 45-75 sec | Fastest variables |
| Wind Components | 5-12 MB | 60-90 sec | Larger payloads |
| Precipitation | 3-8 MB | 60-90 sec | Often queued longer |
| Cloud / Radiation | 5-15 MB | 75-120 sec | Heavier variables |

Times vary with CDS load and retry cycles.

---

## ⚠️ Common Failure Modes

- Missing CDS credentials
- Invalid YAML config
- CDS queue overload
- Network instability
- Filesystem permission issues

All covered by Stage 1 tests.

---

## 🔍 Debugging Workflow

1. **Check logs**
2. **Inspect metadata**
3. **Verify directory structure**
4. **Validate `config.yml`**
5. **Test single-variable ingestion**

This mirrors ingestion pipelines at ECMWF and NASA DAAC.
