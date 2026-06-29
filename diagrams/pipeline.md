# ERA5 Pipeline — Branch 1 (MVP)

This diagram shows the complete Branch 1 ERA5 pipeline.
Although Branch 1 downloads both the **all‑variables ZIP/GRIB** and the
**single‑variable GRIB**, **Stages 2–5 operate exclusively on the
single‑variable GRIB file** (e.g., `2m_temperature_2023_09.grib`).

The pipeline performs minimal preprocessing, lightweight feature engineering,
a baseline model fit, and basic evaluation.

```mermaid
flowchart TD

    A[download_01<br>download_era5_single.py<br>download_era5_monthly.py<br><br>Outputs:<br>• all‑variables ZIP<br>• all‑variables GRIB<br>• single‑variable GRIB<br>• single‑variable IDX (with &lt;hash&gt; suffix)]

    B[preprocessing_02<br>unzip_grib.py<br>inspect_grib.py<br>convert_grib_to_parquet.py<br><br>Operates ONLY on:<br>• single‑variable GRIB<br><br>Outputs:<br>• 2m_temperature_2023_09.parquet]

    C[features_03<br>minimal feature engineering<br><br>Operates ONLY on:<br>• 2m_temperature_2023_09.parquet<br><br>Outputs:<br>• features.parquet]

    D[modeling_04<br>baseline pollution‑risk model<br><br>Operates ONLY on:<br>• features.parquet<br><br>Outputs:<br>• model.pkl]

    E[evaluation_05<br>basic metrics + plots<br><br>Operates ONLY on:<br>• model.pkl<br>• features.parquet<br><br>Outputs:<br>• predictions.parquet]

    A -->|raw GRIB files| B
    B -->|single‑variable parquet| C
    C -->|features.parquet| D
    D -->|model.pkl| E
```

## Notes

- Branch 1 intentionally uses **one year** and **one month**  
  - Recommended: **September 2023**
- Stage 1 downloads **four raw files**:
  - all‑variables ZIP  
  - all‑variables GRIB  
  - single‑variable GRIB  
  - single‑variable IDX (with `<hash>` suffix)
- Stages **2–5 operate exclusively on the single‑variable GRIB**.
- Preprocessing includes:
  - `unzip_grib.py` (extracts multi‑variable GRIB from ZIP; optional in Branch 1)  
  - `inspect_grib.py` (schema + cfgrib metadata check)  
  - `convert_grib_to_parquet.py` (single‑variable only)
- Feature engineering is intentionally minimal (Branch 1).
- Modeling produces a single artifact: **model.pkl**.
- Evaluation produces **predictions.parquet** and basic plots.