# Stage 02 — Preprocessing (GRIB → Hourly Parquet)

Stage 02 converts raw ERA5 GRIB files into structured, hourly Parquet slices and produces the global metadata.json used by Stage 03.

```mermaid
flowchart TD

    Z["📦 Unzip GRIBs
    unzip_grib.py
    - Extract monthly ZIPs
    - Normalize filenames
    - Produce era5_year_month.grib"]:::z

    I["🔍 Inspect GRIB
    inspect_grib.py
    - Lightweight GRIB metadata extraction
    - Variables, dims, coords, units
    - File size and integrity checks"]:::i

    C["🧰 Convert GRIB to Parquet
    convert_grib_to_parquet.py
    - Multi-variable conversion
    - HOURLY Parquet slices
    - Parallel processing
    - Per-variable directories"]:::c

    M["🗂 Build Master Metadata
    run_preprocessing.py
    - Combine inspection and parquet paths
    - Global metadata.json
    - Stage 2 to Stage 3 contract"]:::m

    Z -->|normalized GRIB| I
    I -->|metadata| C
    C -->|hourly parquet| M

    classDef z fill:#e6f2ff,stroke:#004c99,color:#000;
    classDef i fill:#e8ffe8,stroke:#339933,color:#000;
    classDef c fill:#fff0e6,stroke:#cc5500,color:#000;
    classDef m fill:#f2e6ff,stroke:#7a1fa2,color:#000;
```

---

## Responsibilities

### 1. Unzip GRIBs

- Extract monthly ZIP archives from Stage 01.
- Normalize filenames to a consistent pattern:

```code
era5_<year>_<month>.grib
```

- Validate ZIP integrity and GRIB presence.

### 2. Inspect GRIB

- Extract variable list (shortName, long_name, units).
- Extract dimensions and coordinate grids.
- Validate GRIB structure before conversion.
- Produce lightweight inspection metadata.

### 3. Convert GRIB to Parquet

- Convert all variables in the GRIB file.
- Produce HOURLY Parquet slices:

```code
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
```

- Parallel conversion for speed.
- Normalize schema:
- `time`
- `lat`
- `lon`
- `<variable>`

### 4. Build Master Metadata

- Combine inspection metadata and parquet paths.
- Produce global `metadata.json`:

```json
{
  "variables": {
    "<shortName>": {
      "<timestamp>": "<parquet_path>"
    }
  },
  "timestamps": [...]
}
```

- Defines the Stage 2 → Stage 3 contract.

---

## Outputs

### Hourly Parquet Slices

```code
data/intermediate/<year>/<month>/<variable>/<variable>_<timestamp>.parquet
```

### Global Metadata

```code
data/metadata/metadata.json
```

### IR Boundary

- Defines **IR₁** (hourly Parquet + metadata.json)
