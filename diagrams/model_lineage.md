# Model Lineage Diagram (Stages 06–08)

This diagram shows how datasets, features, models, evaluations, registry entries, and deployment artifacts connect across Stages 06–08.
It is the end‑to‑end lineage graph for the modeling + deployment pipeline.

```mermaid
flowchart TD

    F["📄 feature_tensors (IR5)
    - parquet
    - feature_metadata.json"]:::feat

    D["📁 model_ready_dataset (IR6)
    - train/val/test splits
    - normalization rules
    - dataset_manifest.json"]:::data

    M["🤖 trained_model (IR6)
    - weights
    - training_config.json
    - normalization.json"]:::model

    EVAL["📊 evaluation_reports (IR7)
    - metrics.json
    - residuals
    - plots"]:::eval

    PRED["📨 predictions (IR7)
    - prediction.parquet"]:::pred

    REG["🗂 model_registry_entry (IR8)
    - lineage
    - metadata
    - version"]:::reg

    DOCKER["📦 docker_image (IR8)
    - inference image
    - model + config"]:::dock

    API["🖥 fastapi_server (IR8)
    - /predict
    - /health
    - /metadata"]:::api

    DEPLOY["🚀 deployment (IR8)
    - staging
    - production"]:::deploy

    F --> D
    D --> M
    M --> EVAL
    M --> PRED
    M --> REG
    REG --> DOCKER
    DOCKER --> API
    API --> DEPLOY

    classDef feat fill:#cce5ff,stroke:#004c99,color:#000;
    classDef data fill:#ccffcc,stroke:#339933,color:#000;
    classDef model fill:#e0b3ff,stroke:#7a1fa2,color:#000;
    classDef eval fill:#f2ccff,stroke:#9933cc,color:#000;
    classDef pred fill:#d9f2ff,stroke:#3399cc,color:#000;
    classDef reg fill:#cce5ff,stroke:#004c99,color:#000;
    classDef dock fill:#fff2cc,stroke:#b38f00,color:#000;
    classDef api fill:#b3d9ff,stroke:#0066cc,color:#000;
    classDef deploy fill:#ccffcc,stroke:#339933,color:#000;
```

---

## Responsibilities

### Feature Tensors (IR₅)

- Provide all derived features, composites, and aggregations.
- Supply canonical feature metadata.
- Serve as the sole input to dataset assembly.

### Model‑Ready Dataset (IR₆)

- Build deterministic train/val/test splits.
- Apply normalization rules.
- Produce dataset manifest for reproducibility.

### Trained Model (IR₆)

- Store weights, training config, and normalization rules.
- Capture dataset lineage.
- Produce artifacts for evaluation and registry.

### Evaluation Reports (IR₇)

- Compute regression metrics (MAE, RMSE, R², MAPE).
- Generate residuals, plots, calibration curves.
- Provide model quality signals for promotion.

### Predictions (IR₇)

- Batch inference over full datasets.
- Produce prediction parquet files.

### Model Registry Entry (IR₈)

- Store lineage, metadata, version, and artifacts.
- Track promotion from staging → production.

### Docker Image (IR₈)

- Package model + normalization + inference config.
- Provide CPU/GPU variants.
- Serve as the deployable inference unit.

### FastAPI Server (IR₈)

- Load model and normalization rules.
- Expose `/predict`, `/health`, `/metadata`.
- Provide batch + streaming inference.

### Deployment (IR₈)

- Run staging and production environments.
- Autoscale inference.
- Serve predictions to downstream systems.

---

## Outputs

### Model‑Ready Dataset (IR₆)

```code
data/datasets/<dataset_name>.parquet
```

### Model Artifacts (IR₆)

```code
models/<model_id>/artifacts/
models/<model_id>/metadata.json
```

### Evaluation Reports (IR₇)

```code
evaluation_reports/<model_id>.json
plots/<model_id>_*.png
```

### Predictions (IR₇)

```code
data/predictions/<model_id>_<timestamp>.parquet
```

### Registry Entry (IR₈)

```code
mlflow/<model_id>/
```

### Docker Image (IR₈)

```code
docker/<model_id>/
```

### FastAPI Server (IR₈)

```code
api/
```

### Deployment (IR₈)

```code
deployment/
```

### IR Boundary

- Defines **IR₆**, **IR₇**, and **IR₈** lineage end‑to‑end
