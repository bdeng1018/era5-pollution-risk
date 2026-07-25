# ERA5 Pollution‑Risk Pipeline — Branch 1

## Pipeline Architecture (Stages 01–05)

```mermaid
flowchart TB
    %% ============================
    %% Stage 01 — Download ERA5
    %% ============================
    subgraph S01 ["Stage 01: Download ERA5"]
        direction LR
        D1["cdsapi monthly request"]
        D2["GRIB files (data/raw/era5/)"]
    end

    %% ============================
    %% Stage 02 — Preprocessing
    %% ============================
    subgraph S02 ["Stage 02: Preprocessing"]
        direction LR
        P1["Unzip GRIB archives"]
        P2["Inspect GRIB metadata"]
        P3["Convert GRIB → Parquet"]
    end

    %% ============================
    %% Stage 03 — Feature Engineering
    %% ============================
    subgraph S03 ["Stage 03: Feature Engineering"]
        direction LR
        F1["Load intermediate Parquet"]
        F2["Apply feature registry (identity)"]
        F3["Write features.parquet"]
    end

    %% ============================
    %% Stage 04 — Modeling
    %% ============================
    subgraph S04 ["Stage 04: Modeling"]
        direction LR
        M1["Load features.parquet"]
        M2["Train MeanPredictor"]
        M3["Save model.pkl"]
    end

    %% ============================
    %% Stage 05 — Evaluation
    %% ============================
    subgraph S05 ["Stage 05: Evaluation"]
        direction LR
        E1["Load model.pkl + features"]
        E2["Compute MAE + RMSE"]
        E3["Write predictions.parquet"]
    end

    %% ============================
    %% Connections (Top → Bottom)
    %% ============================
    D2 --> P1
    P3 --> F1
    F3 --> M1
    M3 --> E1
```

## Notes

- Branch 1 is **single‑variable** (2m_temperature) and fully deterministic.
- All stages use shared utilities (`src/utils/`) for logging, paths, config, and validation.
- Raw ERA5 data (`data/raw/era5/`) is never committed to the repository.
