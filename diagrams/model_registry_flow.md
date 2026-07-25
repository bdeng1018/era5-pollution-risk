# Model Registry Flow Diagram (MLflow Lineage + Promotion)

```mermaid
flowchart TD

    %% Inputs
    TRAINED["🤖 trained_model
    weights + config + normalization"]:::model

    METRICS["📊 evaluation_reports
    MAE • RMSE • R² • residuals"]:::eval

    DATASET["📁 model_ready_dataset
    train/val/test splits"]:::data

    %% Registry
    REG["🗂 model_registry
    versioned entries
    lineage + metadata"]:::reg

    STAGE["🧪 staging_version
    'Staging'"]:::stage

    PROD["🚀 production_version
    'Production'"]:::prod

    %% Promotion
    PROMOTE["📈 promotion_gate
    thresholds + approvals"]:::promote

    %% Edges
    TRAINED --> REG
    METRICS --> REG
    DATASET --> REG

    REG --> STAGE
    STAGE --> PROMOTE
    PROMOTE --> PROD

    %% Color scheme (functional, black text)
    classDef model fill:#e8d7ff,stroke:#7a1fa2,color:#000,stroke-width:1px;
    classDef eval fill:#ffd6f5,stroke:#b30086,color:#000,stroke-width:1px;
    classDef data fill:#d9ffd9,stroke:#339933,color:#000,stroke-width:1px;
    classDef reg fill:#d6e8ff,stroke:#004c99,color:#000,stroke-width:1px;
    classDef stage fill:#fff4c2,stroke:#b38f00,color:#000,stroke-width:1px;
    classDef prod fill:#c9f7c9,stroke:#2e8b57,color:#000,stroke-width:1px;
    classDef promote fill:#ffe0cc,stroke:#cc5500,color:#000,stroke-width:1px;
```

---

## Responsibilities

### Model Registry

- Store versioned model entries.
- Capture lineage: dataset hash, feature set, training config.
- Store evaluation summary and metadata.
- Provide artifacts for staging and production.

### Staging Version

- Holds the candidate model for promotion.
- Used for smoke tests, latency checks, correctness validation.
- Allows rollback to previous staging versions.

### Promotion Gate

- Enforces thresholds for accuracy, latency, stability.
- Requires human approval or automated checks.
- Moves model from staging → production.

### Production Version

- Serves live inference.
- Autoscaled and monitored.
- Supports rollback and version pinning.

---

## Outputs

### Registry Entries

```code
mlflow/<model_id>/version-<n>/
```

### Staging Version

```code
mlflow/<model_id>/staging/
```

### Production Version

```code
mlflow/<model_id>/production/
```

### IR Boundary

- Registry manages **IR₈** promotion artifacts end‑to‑end.
