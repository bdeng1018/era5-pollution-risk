# Deployment Promotion Flow (Stage 08)

This diagram shows how a model moves from **training → registry → staging → smoke tests → production**, completing the IR₈ deployment lifecycle.

```mermaid
flowchart TD

    %% Inputs
    M[📄 trained_model IR6<br>- weights<br>- config<br>- normalization]:::model

    EVAL[📊 evaluation_reports IR7<br>- metrics<br>- residuals<br>- plots]:::eval

    %% Registry
    REG[🗂 model_registry<br>- version<br>- lineage<br>- metadata]:::reg

    %% CI/CD
    CI[🧰 ci_cd_pipeline<br>- build<br>- test<br>- scan]:::cicd

    %% Docker
    DOCKER[📦 docker_image<br>- inference image<br>- model + config]:::dock

    %% Staging
    STAGE[🧪 staging_env<br>- smoke tests<br>- latency checks<br>- correctness checks]:::stage

    %% Promotion
    PROMOTE[🗳 promotion_gate<br>- thresholds<br>- approvals]:::promote

    %% Production
    PROD[🗄 production_env<br>- autoscaling<br>- monitoring<br>- alerts]:::prod

    %% Edges
    M --> REG
    EVAL --> REG
    REG --> CI
    CI --> DOCKER
    DOCKER --> STAGE
    STAGE --> PROMOTE
    PROMOTE --> PROD

    %% model artifact (purple)
    classDef model fill:#e0b3ff,stroke:#7a1fa2,color:#000,stroke-width:1px;

    %% evaluation diagnostics (pink/purple)
    classDef eval fill:#f2ccff,stroke:#9933cc,color:#000,stroke-width:1px;

    %% registry metadata (blue)
    classDef reg fill:#cce5ff,stroke:#004c99,color:#000,stroke-width:1px;

    %% CI/CD automation (orange)
    classDef cicd fill:#ffe6cc,stroke:#cc7a00,color:#000,stroke-width:1px;

    %% docker packaging (yellow)
    classDef dock fill:#fff2cc,stroke:#b38f00,color:#000,stroke-width:1px;

    %% staging checks (green)
    classDef stage fill:#ccffcc,stroke:#339933,color:#000,stroke-width:1px;

    %% promotion gate (gold)
    classDef promote fill:#ffd966,stroke:#b38600,color:#000,stroke-width:1px;

    %% production runtime (cyan)
    classDef prod fill:#d9f2ff,stroke:#3399cc,color:#000,stroke-width:1px;
```

---

## Responsibilities

### Model Registry

- Store model version, lineage, metadata, and evaluation summary.
- Provide promotion‑ready artifacts for CI/CD.

### CI/CD Pipeline

- Build inference image.
- Run unit tests and integration tests.
- Perform security scans.
- Push image to container registry.

### Docker Image

- Package model + normalization + inference config.
- Provide CPU/GPU variants.
- Serve as deployable inference unit.

### Staging Environment

- Run smoke tests:
  - latency checks
  - correctness checks
  - schema validation
- Validate inference endpoints.

### Promotion Gate

- Enforce thresholds:
  - accuracy
  - latency
  - stability
- Require approvals for production promotion.

### Production Environment

- Autoscale inference.
- Monitor latency, throughput, and error rates.
- Emit alerts and logs for observability.

---

## Outputs

### Staging Deployment (IR₈)

```code
deployment/staging/
```

### Production Deployment (IR₈)

```code
deployment/production/
```

### Docker Images (IR₈)

```code
docker/<model_id>/
```

### Registry Entries (IR₈)

```code
mlflow/<model_id>/
```

### IR Boundary

- Defines **IR₈** (production‑ready deployment artifacts)
