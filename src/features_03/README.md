# features_03 — Branch 1 Feature Engineering

Branch 1 includes a minimal placeholder for feature engineering. The goal at 
this stage is not to build a full transformation pipeline, but to establish a 
clean module structure that downstream stages (modeling and evaluation) can 
import without breaking.

This directory will expand significantly in Branch 2, where full feature
definitions, metadata tracking, and transformation graphs will be introduced.

---

## 📌 Branch 1 Scope

Branch 1 feature engineering is intentionally lightweight:

- Load the **single‑variable Parquet file** produced in `preprocessing_02`
- Apply minimal placeholder transformations (e.g., identity feature)
- Save a small `features.parquet` file for the modeling placeholder
- Provide a clean function signature for future expansion
- Avoid complexity: no metadata, no dependency graphs, no validation

The goal is to keep the pipeline runnable end‑to‑end without introducing
complexity prematurely.

---

## 📁 Files

```markdown
features_03/
├── __init__.py              # Package initializer
├── feature_definitions.py   # Minimal Branch 1 feature registry
└── build_features.py        # Branch 1 feature engineering entrypoint
```

Branch 1 contains **only these two modules**. 
Additional modules (e.g., `feature_utils.py`, `validate_features.py`) will 
appear in Branch 2.

---

## ⚙️ How It Works

The Branch 1 `build_features.py` script:

1. Loads the single Parquet file from `data/intermediate/`
2. Applies placeholder features from `feature_definitions.py`
3. Writes `features.parquet` to `data/features/`
4. Logs the action using the shared logging utilities

This keeps the pipeline functional while leaving room for Branch 2 expansion.

---

## 🔜 Branch 2 Preview

Branch 2 will introduce:

- A full feature registry
- Transformation dependency graphs
- Variable‑level metadata
- Multi‑variable feature generation
- Spatial + temporal aggregations
- Rolling windows and lagged features
- Feature validation and schema checks

None of these are included in Branch 1 to maintain a clean MVP.

---

## 📦 Usage

Feature engineering is triggered via the Makefile:

```markdown
make features
```

Or directly:

```markdown
python -m src.features_03.build_features
```

---

## 📬 Notes

Branch 1 keeps this stage intentionally simple. The purpose is to maintain a
clean pipeline structure and ensure downstream modules have predictable inputs,
without committing to a full feature‑engineering framework yet.