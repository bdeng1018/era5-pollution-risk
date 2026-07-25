# spatiotemporal_04 — Stage 4 Spatiotemporal Compiler (Branch 2)

Stage 4 consumes the fully merged ERA5 dataset produced in Stage 3 and transforms it into **analysis‑ready spatiotemporal tensors**, **compiler‑validated invariants**, and **domain‑agnostic meteorological composites**.

Stage 4 is intentionally designed as a **pure library layer**: deterministic, import‑safe, and free of side effects. It is the **compiler** of the pipeline — converting raw geophysical fields into structured, validated, reproducible tensors suitable for downstream modeling, risk scoring, and visualization.

---

## 🎯 Objectives

Stage 4 provides a stable interface for:

- **Loading Stage 3 outputs** (`merged.nc`, metadata, QC)
- **Constructing spatiotemporal tensors** (`time × lat × lon × variables`)
- **Applying domain‑agnostic transforms** (grid normalization, alignment, interpolation)
- **Propagating QC + metadata contracts**
- **Producing analysis‑ready artifacts** for Stage 5 modeling or external tools

All transformations are **pure**, **deterministic**, and **reproducible**.

---

## 📥 Inputs

Stage 4 expects the following Stage 3 outputs:

- `merged.nc`
Fully merged ERA5 dataset (xarray).

- `merged_metadata.json`
Dimensions, coordinate ranges, variable list.

- `merged_qc.json`
QC summary (min, max, NaN counts per variable).

Paths are defined in:

- `config.yml → paths.stage3_merged`
- `config.yml → paths.stage3_metadata`
- `config.yml → paths.stage3_qc`

---

## 📤 Outputs

Stage 4 produces:

- **Spatiotemporal tensors**
Structured arrays with shape:
`time × lat × lon × variables`

- **Aligned + interpolated temporal sequences**

- **Grid‑normalized datasets**
(consistent lat/lon ordering, masks, metadata)

- **Stage 4 diagnostic reports**
Saved under:
`data/spatiotemporal/stage4_<diagnostic>.json`

Stage 4 does **not** compute domain‑specific risk indices.
Those belong in **Stage 5+**, where modeling logic and domain semantics live.

---

## 📁 Directory Structure

```text
src/
└── spatiotemporal_04/
    ├── __init__.py
    ├── driver.py
    ├── grid.py
    ├── mask.py
    ├── temporal_align.py
    ├── temporal_interpolate.py
    ├── qc.py
    ├── metadata.py
    └── tensor_builder.py
```

Each module is **pure**, **import‑safe**, and **side‑effect‑free**.

---

## 🧩 Core Concepts

### Spatiotemporal Tensor

Stage 4 constructs tensors with strict IR₄ invariants:

- sorted time dimension
- normalized lat/lon coordinates
- consistent variable ordering
- stable dtypes
- no missing coordinates
- no duplicate indices

These invariants ensure Stage 5 modeling can rely on a stable, predictable API.

### Temporal Alignment & Interpolation

Stage 4 provides utilities for:

- aligning timestamps across variables
- filling missing hours
- interpolating short gaps
- ensuring monotonic time sequences

These operations live in:

- `temporal_align.py`
- `temporal_interpolate.py`

### Grid Normalization & Masking

Stage 4 ensures:

- consistent lat/lon ordering
- grid masks for land/sea or custom domains
- coordinate normalization

These operations live in:

- `grid.py`
- `mask.py`

### Metadata & QC Propagation

Stage 4 validates:

- dimension consistency
- variable presence
- coordinate ranges
- QC propagation from Stage 3

These operations live in:

- `metadata.py`
- `qc.py`

---

## ▶️ Usage Example

```python
from src.spatiotemporal_04 import load_stage3_outputs
from src.spatiotemporal_04.grid import process_grid
from src.spatiotemporal_04.mask import process_spatial_consistency
from src.spatiotemporal_04.temporal_align import process_temporal_alignment
from src.spatiotemporal_04.temporal_interpolate import process_interpolation
from src.spatiotemporal_04.qc import process_qc
from src.spatiotemporal_04.tensor_builder import process_spatiotemporal_merge

# Load Stage 3 merged dataset
ds = load_stage3_outputs(config)

# Stage 4 invariant pipeline
ds, grid_contract = process_grid(ds)
ds, mask_contract = process_spatial_consistency(ds)
ds, temporal_contract = process_temporal_alignment(ds)
ds, interp_contract = process_interpolation(ds)
ds, qc_contract = process_qc(ds, fields=config["fields"])

# Build canonical spatiotemporal tensor
tensor = process_spatiotemporal_merge(
    ds,
    grid_contract=grid_contract,
    mask_contract=mask_contract,
    temporal_contract=temporal_contract,
    interp_contract=interp_contract,
    qc_contract=qc_contract,
)
```

This is the canonical Stage 4 workflow.

---

## 🧭 Design Principles

- **Pure library modules**
No `main()`, no CLI, no side effects.

- **Compiler‑style invariants**
Stable API, deterministic outputs, strict tensor contracts.

- **Reproducibility**
Every transformation is documented and deterministic.

- **Interoperability**
Outputs compatible with NumPy, PyTorch, TensorFlow, and xarray.

- **Safety**
No mutation of global state; no implicit I/O.

---

## 📦 Dependencies

Stage 4 relies on:

- `xarray`
- `numpy`
- `scipy`
- `netcdf4`
- Stage 3 outputs

No external services are required.

---

## 🔮 Extensibility

Stage 4 can be extended with:

- additional risk indices
- custom tensor formats
- more aggregation pipelines
- domain‑specific modeling features
- integration with Stage 5 ML pipelines
