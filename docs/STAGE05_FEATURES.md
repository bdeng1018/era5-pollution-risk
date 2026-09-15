# Stage 05 — Feature Engineering (IR₅)

## Overview

Stage 05 constructs ML‑ready **registry‑driven** features from Stage 04 (IR₄) tensors.
This includes deterministic temporal, spatial, and composite meteorological features used by downstream modeling (IR₆), evaluation (IR₇), and deployment (IR₈).

## Inputs

- Stage 04 tensor (`stage4_tensor.nc`)
- Stage 04 metadata
- Stage 04 QC

## Outputs

- `stage5_features.nc`
- `stage5_metadata.json`
- `stage5_qc.json`
- `registry.json` (canonical feature registry)

## Feature Groups

- **Temporal features** (rolling means + deltas)
- **Spatial features** (3×3 kernels + Laplacians)
- **Composite indices** (deterministic formulas combining temporal + spatial transforms)

## Determinism

All IR₅ outputs must be:

- reproducible
- hash‑stable
- aligned to the IR₄ grid
- defined through the canonical Stage 05 registry (`stage5.yml`)

## Registry‑Driven Definitions

Stage 05 uses a declarative registry to define:

- temporal feature transforms
- spatial kernel transforms
- composite formulas
- feature provenance
- deterministic hashing boundaries

The registry ensures that IR₅ features are stable, reproducible, and version‑controlled.
