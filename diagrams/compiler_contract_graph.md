# Compiler Contract Graph (Stage 04)

This diagram shows how each compiler pass in Stage 04 produces a **contract** that becomes the required input for the next pass.
It is the core of the spatiotemporal compiler architecture.

```mermaid
flowchart TD

    %% Grid contract (spatial domain → blue)
    G[📁 grid<br>- lat<br>- lon<br>- grid_shape<br>- crs]:::grid

    %% Mask contract (spatial filtering → green)
    M[🗂 mask<br>- mask<br>- mask_applied_variables]:::mask

    %% Temporal alignment (normalization → orange)
    TA[📄 temporal_align<br>- aligned_timestamps<br>- missing_timestamps]:::align

    %% Temporal interpolation (aux transform → yellow)
    TI[📦 temporal_interpolate<br>- interpolated_timestamps<br>- interpolation_fraction]:::interp

    %% QC (quality control → purple)
    QC[📊 qc<br>- qc_flags<br>- qc_summary]:::qc

    %% Metadata (provenance → deep purple)
    MD[🗂 metadata<br>- variable_metadata<br>- provenance]:::meta

    %% Tensor builder (final output → cyan)
    TB[🗄 tensor_builder<br>- spatiotemporal_tensor.nc<br>- stage4_metadata.pkl<br>- stage4_qc.pkl]:::output

    %% Flow
    G --> M --> TA --> TI --> QC --> MD --> TB

    %% Functional domain-coded colors (pure black text)
    classDef grid fill:#cce5ff,stroke:#004c99,color:#000,stroke-width:1px;      %% spatial domain
    classDef mask fill:#ccffcc,stroke:#339933,color:#000,stroke-width:1px;      %% spatial filtering
    classDef align fill:#ffe6cc,stroke:#cc7a00,color:#000,stroke-width:1px;     %% temporal normalization
    classDef interp fill:#fff2cc,stroke:#b38f00,color:#000,stroke-width:1px;    %% temporal interpolation
    classDef qc fill:#f2ccff,stroke:#9933cc,color:#000,stroke-width:1px;        %% QC
    classDef meta fill:#e0b3ff,stroke:#7a1fa2,color:#000,stroke-width:1px;      %% metadata
    classDef output fill:#d9f2ff,stroke:#3399cc,color:#000,stroke-width:1px;    %% final output
```

---

## Responsibilities

### grid

- Normalize latitude and longitude arrays.
- Validate CRS and grid spacing.
- Produce the **grid contract**:
  - `lat[]`
  - `lon[]`
  - `grid_shape`
  - `crs`

### mask

- Detect spatial holes.
- Build boolean mask array.
- Apply mask to variables.
- Produce the **mask contract**:
  - `mask[]`
  - `mask_applied_variables`

### temporal_align

- Build aligned timeline.
- Detect missing timestamps.
- Enforce hourly frequency.
- Produce the **alignment contract**:
  - `aligned_timestamps[]`
  - `missing_timestamps[]`

### temporal_interpolate

- Fill temporal gaps.
- Compute interpolation fractions.
- Produce the **interpolation contract**:
  - `interpolated_timestamps[]`
  - `interpolation_fraction[]`

### qc

- Physical range checks.
- NaN/inf detection.
- Temporal/spatial jump checks.
- Produce the **QC contract**:
  - `qc_flags`
  - `qc_summary`

### metadata

- Validate schema and units.
- Propagate provenance.
- Produce the **metadata contract**:
  - `variable_metadata`
  - `provenance`

### tensor_builder

- Apply all contracts (grid, mask, temporal, QC, metadata).
- Build canonical tensor.
- Write final artifacts:

```code
data/spatiotemporal/spatiotemporal_tensor.nc
data/spatiotemporal/stage4_metadata.pkl
data/spatiotemporal/stage4_qc.pkl
```

---

## Outputs

### Compiler Outputs (IR₄)

```code
data/spatiotemporal/spatiotemporal_tensor.nc
data/spatiotemporal/stage4_metadata.pkl
data/spatiotemporal/stage4_qc.pkl
```

### IR Boundary

- Defines **IR₄** (canonical spatiotemporal tensor)
