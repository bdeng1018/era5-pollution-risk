# ERA5 Pipeline — Branch 2 (Stages 1–3)

This diagram shows the current Branch 2 ERA5 pipeline, which expands Branch 1
from a single‑variable MVP into a multi‑variable, parallel, chunk‑ready ingestion
system.

Branch 2 introduces:

- Monthly ZIP + multi‑variable GRIB ingestion
- Unified GRIB inspection (single + multi)
- HOURLY Parquet conversion for all variables
- Parallel preprocessing
- Master metadata.json (Stage 2 → Stage 3 contract)
- Chunk‑planning and chunk‑execution engine (Stage 3)

```mermaid
flowchart TD

    A[download_01<br>download_era5_single.py<br>download_era5_monthly.py<br><br>Outputs:<br>• era5_YYYY_MM.zip<br>• era5_YYYY_MM.grib<br>• <var>_YYYY_MM.grib<br>• <var>_YYYY_MM.grib.&lt;hash&gt;.idx]

    B[preprocessing_02<br>unzip_grib.py<br>inspect_grib.py<br>convert_grib_to_parquet.py<br>run_preprocessing.py<br><br>Operates on:<br>• multi‑variable GRIBs<br>• single‑variable GRIBs<br><br>Outputs:<br>• HOURLLY Parquet slices<br>• metadata.json]

    C[core_03<br>chunk_planner.py<br>chunk_spec.py<br>chunk_schema.py<br>chunk_worker.py<br>chunk_orchestrator.py<br><br>Operates on:<br>• metadata.json<br>• HOURLY Parquet slices<br><br>Outputs:<br>• chunked Parquet tiles]

    A -->|raw GRIB files| B
    B -->|hourly parquet + metadata.json| C
```

## Stage Summaries

### Stage 1 — download_01

- Single‑variable GRIB (Branch 1 compatibility)
- Monthly ZIP + multi‑variable GRIB (Branch 2 ingestion)
- Output: raw GRIBs + IDX

### Stage 2 — preprocessing_02

- Unzip monthly ZIPs → normalized GRIBs
- Unified inspection (single + multi)
- HOURLY Parquet conversion
- Parallel preprocessing
- Output: `metadata.json` + hourly Parquet slices

### Stage 3 — core_03

- Chunk planning (temporal + spatial)
- Chunk schema definition
- Chunk worker execution (parallel)
- Output: chunked Parquet tiles

---

## Forward Plan — Stages 4–8 (Not Yet Implemented)

These stages are planned and shape the design of Stage 3. They appear here for
roadmap clarity but are not yet implemented.

### Stage 4 — Spatiotemporal Structuring

- Merge chunked tiles into unified spatiotemporal cubes
- Build multi‑variable tensors
- Output: `structured_04/`

### Stage 5 — Feature Engineering

- Derived features (gradients, anomalies, rolling windows)
- Spatial aggregations
- Output: `features_05/`

### Stage 6 — Dataset Assembly

- Train/val/test splits
- Normalization
- Output: `datasets_06/`

### Stage 7 — Modeling

- ML/AI models (regression, transformers, CNNs)
- Output: `modeling_07/`

### Stage 8 — Evaluation + Inference

- Metrics, plots, predictions
- Output: `predictions_08/`
