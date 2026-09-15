# Stage 05 — IR₅ Schema

## Overview

IR₅ defines the structured feature tensor produced by Stage 05.
It is derived from IR₄ canonical spatiotemporal tensors using registry‑driven temporal, spatial, and composite transforms.

## Coordinates

- `time`
- `lat`
- `lon`

## Base Variables (from IR₄)

Stage 05 uses the following IR₄ meteorological variables:

- t2m, d2m, u10, v10, msl

## Feature Variables

IR₅ contains three feature groups:

- **Temporal features** (rolling means + deltas)
- **Spatial features** (3×3 kernels + Laplacians)
- **Composite features** (deterministic formulas combining temporal + spatial transforms)

## Shape

All IR₅ variables must have shape:

```code
(time=9128, lat=9, lon=17)
```

## Metadata

IR₅ metadata includes:

- `dimensions` — tensor shape
- `missing_values` — count per feature
- `infinite_values` — count per feature
- `registry` — canonical list of temporal, spatial, composite features
- `provenance` — IR₄ source tensor + version

## QC Requirements

Strict QC:

- Shape validation
- NaN validation
- Range validation
- Alignment validation

## Deterministic Hashing

IR₅ hashing rules ensure:

- reproducibility
- version stability
- registry‑driven determinism
