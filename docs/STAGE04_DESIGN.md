# Stage 04 — Spatiotemporal Compiler (IR₄)

## Overview

Stage 04 compiles canonical IR₄ spatiotemporal tensors from Stage 03 chunk outputs.
It enforces deterministic grid alignment, mask logic, metadata consistency, and QC boundaries.

## Inputs

- Stage 03 chunk tensors
- Stage 03 chunk metadata
- Stage 03 QC

## Outputs

- `stage4_tensor.nc`
- `stage4_metadata.json`
- `stage4_qc.json`

## Responsibilities

- Align spatial grid (`lat`, `lon`)
- Align temporal index (`time`)
- Apply validity mask
- Merge chunked variables into canonical IR₄ tensor
- Produce metadata and QC artifacts

## IR₄ Components

### Coordinates

- `time`
- `lat`
- `lon`

### Variables

- 21 normalized ERA5 fields (blh, cape, cin, d2m, e, lsm, msl, slhf, sp, sshf, ssr, ssrd, ssrdc, str, t2m, tcc, tco3, tcwv, tp, u10, v10)

### Metadata

- Spatial metadata (lat/lon grid, region, chunk_id)
- Temporal metadata (timestamp, year, month, day, hour)
- Chunk provenance (source chunks, boundaries)
- QC summary (missing values, infinite values, range checks)

### QC

- Shape validation
- NaN validation
- Infinite value validation
- Alignment validation (IR₃ → IR₄)

## Determinism

IR₄ must be:

- grid‑stable
- mask‑stable
- reproducible
- hash‑stable under deterministic hashing rules

## Hashing Boundary

IR₄ hashing defines the boundary for:

- downstream IR₅ feature determinism
- versioned reproducibility of spatiotemporal tensors
