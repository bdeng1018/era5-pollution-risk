# download_01 — Stage 1 ERA5 Data Retrieval (Branch 2)

`download_01` implements the ERA5 data ingestion layer. Stage 1 retrieves raw ERA5 **Single‑Level** reanalysis data from the Copernicus Data Store (CDS) and writes **GRIB** files into the `data/raw/era5/<year>/<month>/<variable>/` directory. Stage 1 is intentionally simple in Branch 1 and becomes production‑grade in Branch 2.

Stage 1 is the entrypoint of the entire pipeline.

---

## 🎯 Purpose

Stage 1 performs three core responsibilities:

1. **Build ERA5 API requests** for configured variables, years, and months
2. **Download raw GRIB files** into the structured raw directory
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

- Multi‑year ingestion across all configured years/months
- Retry logic with exponential backoff
- Structured logging
- Metadata tracking (timestamps, file sizes, run status)
- Environment validation (CDS credentials, directory structure)
- Config‑driven execution via YAML files
- Graceful error handling and recovery
- Long‑form ERA5 variable naming for consistency across CDSAPI, raw layout, metadata, and downstream stages

Branch 2 transforms Stage 1 into a reliable, reproducible ingestion layer.

---

## 📁 Folder Structure

```text
download_01/
│
├── __init__.py
├── download_era5_single.py     # single‑variable ingestion with retries and metadata
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

Branch 2 removes ZIP ingestion entirely because single‑variable GRIB downloads:

- simplify retry logic
- reduce failure surface area
- improve metadata granularity
- align with Stage 2 variable‑specific preprocessing

---

## 📦 Outputs

Stage 1 produces:

### Raw GRIB files

Stored under:

`data/raw/era5/<year>/<month>/<variable>/<variable>_<year>_<month>.grib`

Example:

`data/raw/era5/2023/01/10m_u_component_of_wind/10m_u_component_of_wind_2023_01.grib`

### Download metadata

Stored under:

`data/metadata/metadata_<variable>_<year>_<month>.json`

Branch 2 metadata includes:

- variable
- year
- month
- success flag
- config_valid flag
- outfile (absolute GRIB path)

Timestamps and file sizes are added in Stage 2 after GRIB inspection.

---

## 📐 Design Guarantees (Stage 1 Contract)

Stage 1 provides strict guarantees to downstream pipeline stages:

### 1. Deterministic Directory Layout

Every GRIB file is stored under:

`data/raw/era5/<year>/<month>/<variable>/<variable>_<year>_<month>.grib`

This layout is stable across Branch 1, Branch 2, and future branches.

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

No hard‑coded variables or dates exist in Stage 1.

### 6. No ZIP Ingestion

Branch 2 guarantees:

- GRIB‑only ingestion
- one variable per file
- consistent naming across CDSAPI, raw layout, metadata, and Stage 2

This simplifies downstream processing and retry logic.

---

## 🧪 Testing Strategy

### Branch 1

- Smoke tests for single‑variable downloads
- Validate GRIB file creation

### Branch 2

- Retry logic tests (exponential backoff + failure modes)
- Metadata logging tests (success/failure metadata correctness)
- Environment validation tests (credentials + directory + config)
- Multi‑year single-variable ingestion + multi-variable orchestration tests
- Error handling tests
- Monkeypatch tests for `Paths()` and `cdsapi.Client`

These tests ensure **100% functional coverage** of Stage 1 downloading.

---

## ➕ How to Add New Variables

To ingest additional ERA5 single‑level variables:

1. Open `configs/variables.yml`

2. Add the long‑form ERA5 variable name, e.g.:

```yaml
variables:
  - 2m_temperature
  - surface_pressure
  - total_precipitation
  - 10m_u_component_of_wind
```

1. Ensure the variable name matches CDSAPI’s long‑form naming

2. Run Stage 1 again:

```markdown
make download
```

Stage 1 will automatically ingest the new variable across all configured years and months.

---

## ▶️ Running Stage 1

From the project root:

```makefile
make download
```

Or directly:

```bash
python -m src.download_01.download_era5_monthly --config configs/config.yml
```

---

## 📌 Notes

Stage 1 is intentionally simple but foundational:

- Branch 1 provides minimal ingestion
- Branch 2 provides production‑grade ingestion
- Stage 2 preprocessing depends entirely on Stage 1 outputs

**Performance:** ERA5 single‑level GRIB downloads typically take **60–90 seconds per variable per month**. Larger variables (e.g., wind components) may take longer. Retry logic ensures robustness under CDS load.

A clean, reliable Stage 1 ensures the entire pipeline remains reproducible and scalable.

---

## 📝 Operational Notes

Stage 1 ingestion is **I/O‑bound** and interacts with the CDS queue. Typical performance characteristics:

- **60–90 seconds per variable per month** for single‑level ERA5 GRIB downloads
- Larger variables (e.g., wind components) may take longer
- Retry logic handles CDS queue delays and transient network failures
- Stage 1 is **safe to re‑run** — skip logic prevents overwriting existing GRIBs
- Metadata is **always written**, even on failure
- Stage 2 preprocessing depends entirely on Stage 1 outputs

These notes help set realistic expectations for long‑running ingestion jobs.

---

## 📊 Performance Benchmarks

Typical runtime characteristics for ERA5 single‑level ingestion:

| Variable Type           | Avg. GRIB Size | Download Time (CDS) | Notes                         |
|-------------------------|----------------|----------------------|-------------------------------|
| Temperature / Pressure  | 2–5 MB         | 45–75 sec            | Fastest variables             |
| Wind Components         | 5–12 MB        | 60–90 sec            | Larger GRIB payloads          |
| Precipitation           | 3–8 MB         | 60–90 sec            | Often queued longer           |
| Cloud / Radiation       | 5–15 MB        | 75–120 sec           | Heavier variables             |

These values vary with CDS queue load, network conditions, and retry cycles. Stage 1’s retry logic ensures ingestion remains robust even under heavy CDS traffic.

---

## ⚠️ Common Failure Modes

Stage 1 is robust, but several predictable issues can occur:

- **Missing CDS credentials**
`CDSAPI_URL` or `CDSAPI_KEY` not set → environment validation fails.

- **Invalid YAML config**
Malformed `config.yml` → `validate_config()` returns `False`.

- **CDS queue overload**
Long wait times or repeated retry cycles → ingestion slows down.

- **Network instability**
Temporary failures → retry logic handles up to 3 attempts.

- **Filesystem permission issues**
Raw or metadata directories not writable → ingestion fails early.

These failure modes are fully covered by Stage 1 tests.

---

## 🔍 How to Debug Ingestion

When ingestion fails, use the following workflow:

1. **Check logs**

Stage 1 logs every attempt, failure, and retry with `[stage1]` prefixes.

1. **Inspect metadata**

Metadata JSON files contain:

- success flag
- config validity
- GRIB path
- variable/year/month

1. **Verify directory structure**

Ensure:

```markdown
data/raw/era5/<year>/<month>/<variable>/
data/metadata/
data/config/
```

1. **Validate config.yml**

Run:

`python -m src.download_01.download_era5_single --validate-config`

1. **Test single-variable ingestion**

Narrow the failure:

`python -m src.download_01.download_era5_single 2m_temperature 2023 01`

This debugging flow mirrors real ingestion pipelines at ECMWF and NASA DAAC.
