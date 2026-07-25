# API Flow Diagram (Inference Server Architecture)

This diagram shows how your FastAPI inference server loads IR₈ deployment artifacts, validates requests, runs inference, and returns structured predictions.

```mermaid
flowchart TD

    %% Client → API
    CLIENT[📄 client_request<br>- JSON payload]:::client

    API[🖥️ api_server<br>- FastAPI app]:::api

    VALIDATE[🗂️ request_validation<br>- schema + type checks]:::validate

    %% Model loading
    LOADER[🧰 model_loader<br>- weights + metadata + normalization]:::loader

    MODEL[🤖 model_instance<br>- warm-loaded model]:::model

    %% Inference pipeline
    PRE[📦 preprocessing<br>- normalization + tensor prep]:::pre

    INFER[⚙️ inference_engine<br>- forward pass]:::infer

    POST[📤 postprocessing<br>- denormalize + format]:::post

    %% Response
    RESP[📨 response_builder<br>- JSON output]:::resp

    %% Health + metadata endpoints
    HEALTH[❤️ health_endpoint<br>- latency + uptime]:::health

    META[🗄️ metadata_endpoint<br>- version + lineage]:::meta

    %% Main flow edges
    CLIENT --> API
    API --> VALIDATE
    VALIDATE --> PRE
    PRE --> INFER
    INFER --> POST
    POST --> RESP

    %% Auxiliary endpoints
    API --> HEALTH
    API --> META

    %% Model loading flow
    LOADER --> MODEL
    MODEL --> PRE

    %% Domain-coded colors (with pure black text)
    classDef client fill:#cce5ff,stroke:#004c99,color:#000,stroke-width:1px;
    classDef api fill:#b3d9ff,stroke:#0066cc,color:#000,stroke-width:1px;
    classDef validate fill:#ffe6cc,stroke:#cc7a00,color:#000,stroke-width:1px;
    classDef loader fill:#f2ccff,stroke:#9933cc,color:#000,stroke-width:1px;
    classDef model fill:#e0b3ff,stroke:#7a1fa2,color:#000,stroke-width:1px;
    classDef pre fill:#ccffcc,stroke:#339933,color:#000,stroke-width:1px;
    classDef infer fill:#b3ffb3,stroke:#2d862d,color:#000,stroke-width:1px;
    classDef post fill:#e6ffe6,stroke:#4d994d,color:#000,stroke-width:1px;
    classDef resp fill:#d9f2ff,stroke:#3399cc,color:#000,stroke-width:1px;
    classDef health fill:#fff2cc,stroke:#b38f00,color:#000,stroke-width:1px;
    classDef meta fill:#fff2cc,stroke:#b38f00,color:#000,stroke-width:1px;
```

---

## Responsibilities

### API Server

- Load model artifacts, normalization rules, and inference configuration.
- Expose `/predict`, `/health`, and `/metadata` endpoints.
- Manage request parsing, validation, and error handling.

### Request Validation

- Validate JSON payload structure.
- Enforce schema constraints for inputs.
- Reject malformed or incomplete requests.

### Model Loader

- Load model weights and metadata from IR₈ artifacts.
- Apply normalization rules and preprocessing steps.
- Maintain warm model instance for low‑latency inference.

### Inference Engine

- Run forward pass using normalized inputs.
- Apply post‑processing to predictions.
- Produce structured outputs for API response.

### Response Builder

- Format predictions into JSON response.
- Attach metadata, timestamps, and version info.
- Ensure consistent response schema across deployments.

### Health & Metadata Endpoints

- Report model version, registry lineage, and readiness.
- Provide latency, uptime, and environment diagnostics.

---

## Outputs

### API Endpoints

```code
/predict
/health
/metadata
```

### Inference Artifacts

```code
deployment/<model_id>/api/
```

### Logs

```code
data/logs/api/
```

### IR Boundary

- API consumes **IR₈** deployment artifacts and serves production inference.
