# Stage 05 — Feature Engineering (IR₅)

## Overview

Stage 05 constructs deterministic IR₅ feature tensors from IR₄ canonical spatiotemporal tensors.
All features are defined through the Stage 05 registry and include temporal, spatial, and composite transforms.

## Inputs

- `stage4_tensor.nc`
- `stage4_metadata.json`
- `stage4_qc.json`

## Outputs

- `stage5_features.nc`
- `stage5_metadata.json`
- `stage5_qc.json`
- `registry.json`

## Responsibilities

- Apply temporal transforms (rolling means, deltas)
- Apply spatial transforms (3×3 kernels, Laplacians)
- Compute composite indices
- Produce metadata and QC artifacts
- Enforce deterministic hashing boundary

## IR₅ Components

### Coordinates

- `time`
- `lat`
- `lon`

### Base Variables (from IR₄)

- `t2m`
- `d2m`
- `u10`
- `v10`
- `msl`

### Feature Groups

- **Temporal features** (rolling means + deltas)
- **Spatial features** (3×3 kernels + Laplacians)
- **Composite features** (deterministic formulas combining temporal + spatial transforms)

### Metadata

- Dimensions (`time`, `lat`, `lon`)
- Missing value counts
- Infinite value counts
- Canonical feature registry
- IR₄ provenance and version

### QC

- Shape validation
- NaN validation
- Infinite value validation
- Alignment validation (IR₄ → IR₅)

## Determinism

IR₅ must be:

- registry‑driven
- reproducible
- hash‑stable
- aligned with IR₄ grid

## Hashing Boundary

IR₅ hashing defines the boundary for:

- deterministic IR₆ dataset generation
- versioned reproducibility of feature tensors
