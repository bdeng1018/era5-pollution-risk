# Feature Registry DAG (Stage 05)

This diagram shows how Stage 05’s feature engineering system builds **derived features**, **composites**, and **aggregations**, and how each of them flows into the final feature tensor set (IR₅).
It is the core DAG for the feature registry.

```mermaid
flowchart TD

    %% Derived Features
    G[📄 gradients<br>- spatial<br>- temporal]:::derived
    A[📄 anomalies<br>- rolling_mean<br>- climatology]:::derived
    RW[📄 rolling_windows<br>- 3h<br>- 6h<br>- 12h<br>- 24h]:::derived
    TD[📄 temporal_deltas<br>- hour_over_hour]:::derived
    SD[📄 spatial_derivatives<br>- d_lat<br>- d_lon]:::derived

    %% Composites
    C1[🗂 humidity_temperature_interaction]:::composite
    C2[🗂 wind_dispersion_proxy]:::composite
    C3[🗂 instability_index<br>- pressure_plus_temperature]:::composite

    %% Aggregations
    S1[📦 spatial_means]:::agg
    S2[📦 regional_masks]:::agg
    S3[📦 lat_lon_bands]:::agg
    T1[📦 temporal_rolling_mean]:::agg
    T2[📦 temporal_rolling_std]:::agg

    %% Final Feature Tensor
    FT[🗄 feature_tensor<br>- parquet_outputs<br>- feature_metadata_json]:::output

    %% Edges
    G --> C1
    A --> C1
    RW --> C1

    TD --> C2
    SD --> C2

    A --> C3
    SD --> C3

    G --> S1
    A --> S1
    RW --> S1

    S1 --> FT
    S2 --> FT
    S3 --> FT
    T1 --> FT
    T2 --> FT

    C1 --> FT
    C2 --> FT
    C3 --> FT

    %% Color scheme (functional, text black)
    classDef derived fill:#cce5ff,stroke:#004c99,color:#000,stroke-width:1px;
    classDef composite fill:#ccffcc,stroke:#339933,color:#000,stroke-width:1px;
    classDef agg fill:#ffe6cc,stroke:#cc7a00,color:#000,stroke-width:1px;
    classDef output fill:#d9f2ff,stroke:#3399cc,color:#000,stroke-width:1px;
```

---

## Responsibilities

### Derived Features

- Compute variable‑specific transformations:
  - gradients (spatial + temporal)
  - anomalies (rolling mean or climatology)
  - rolling windows (3h, 6h, 12h, 24h)
  - temporal deltas (hour‑over‑hour)
  - spatial derivatives (∂/∂lat, ∂/∂lon)
- Normalize units and ensure consistent dtype.
- Register each derived feature with:
  - name
  - description
  - units
  - dependencies

### Composites

- Build multi‑variable composites:
  - humidity × temperature interactions
  - wind × pollutant dispersion proxies
  - pressure + temperature instability indices
- Ensure composite definitions are versioned and reproducible.
- Register composite features with full provenance.

### Aggregations

- Spatial aggregations:
  - grid‑cell means
  - regional masks
  - lat/lon band summaries
- Temporal aggregations:
  - rolling mean
  - rolling std
- Register aggregated features with dependency graphs.

### Feature Tensor Builder

- Combine derived features, composites, and aggregations.
- Align all features to the canonical spatiotemporal grid.
- Write feature tensors and metadata:

```code
data/features/<feature_name>_<timestamp>.parquet
feature_metadata.json
```

---

## Outputs

### Feature Tensors (IR₅)

```code
data/features/<feature_name>_<timestamp>.parquet
```

### Feature Metadata

```code
feature_metadata.json
```

### IR Boundary

- Defines **IR₅** (feature tensors)
