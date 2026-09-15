# Stage 05 — Feature Engineering (IR₅)

Stage 05 transforms the canonical spatiotemporal tensor (IR₄) into ML‑ready
feature tensors (IR₅). This stage introduces temporal, spatial, and composite
meteorological features used by downstream modeling (Stage 06), evaluation
(Stage 07), and deployment (Stage 08).

## Overview

Stage 05 constructs three feature layers:

### 1. Temporal Features

Derived from rolling windows and temporal deltas:

- 6h / 24h rolling means
- 24h temporal deltas
- anomaly‑style transformations

### 2. Spatial Features

Computed using fixed spatial kernels:

- 3×3 mean filters
- Laplacian operators
- neighborhood‑based context features

### 3. Composite Features

Deterministic indices combining temporal + spatial signals:

- instability index
- moisture–temperature interaction index
- pressure‑context index
- wind‑shear index

Composite formulas are defined declaratively in `stage5.yml` and evaluated
deterministically.

## Outputs

Stage 05 produces the IR₅ boundary:

- **Feature tensor:** `stage5_features.nc`
- **Metadata:** `stage5_metadata.json`
- **Quality control report:** `stage5_qc.json`
- **Registry validation:** ensures all IR₅ features match the canonical registry

## Determinism

All IR₅ outputs are:

- reproducible
- hash‑stable
- aligned to the IR₄ grid
- versioned through `stage5.yml`

Stage 05 is the first stage where *features* are constructed rather than raw or
aligned tensors, forming the canonical input representation for all ML models.
