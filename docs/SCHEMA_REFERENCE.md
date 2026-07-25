# Schema Reference — ERA5 Pollution‑Risk Pipeline (Branch 1)

Branch 1 does **not** generate a JSON schema file.
However, it *does* produce deterministic tabular artifacts whose schemas are stable and should be documented.

This reference defines the canonical schemas for:

- Stage 02 — Intermediate Parquet
- Stage 03 — Features Parquet
- Stage 05 — Predictions Parquet

These schemas form the **data contract** for Branch 1.

---

## 1. Schema Structure

Branch 1 schemas are simple, flat tables.
Each artifact uses the following conceptual schema structure:

```text
<artifact>:
  - name: <column_name>
    type: <data_type>
    description: <human-readable description>
    required: <true|false>
```

All fields are required in Branch 1 because the pipeline is deterministic and single‑variable.

---

## 2. Stage 02 — Intermediate Parquet Schema

Flattened representation of ERA5 GRIB.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | float | true | Grid latitude |
| `longitude` | float | true | Grid longitude |
| `time` | datetime | true | Timestamp of reanalysis slice |
| `value` | float | true | ERA5 variable value (`t2m`) |
| `year` | int | true | Year extracted from `time` |
| `month` | int | true | Month extracted from `time` |

---

## 3. Stage 03 — Features Parquet Schema

Branch 1 applies an identity transformation.
The schema is identical to Stage 02.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | float | true | Same as intermediate |
| `longitude` | float | true | Same as intermediate |
| `time` | datetime | true | Same as intermediate |
| `value` | float | true | Same as intermediate |
| `year` | int | true | Same as intermediate |
| `month` | int | true | Same as intermediate |

No additional features are generated in Branch 1.

---

## 4. Stage 04 — Model Artifact Schema

The baseline model is a deterministic **MeanPredictor**.

| Artifact | Type | Description |
|----------|------|-------------|
| `model.pkl` | pickle | Stores the global mean of `value` |

There are no learned parameters beyond the mean.

---

## 5. Stage 05 — Predictions Parquet Schema

Final output of Branch 1.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | float | true | Grid latitude |
| `longitude` | float | true | Grid longitude |
| `time` | datetime | true | Timestamp |
| `value` | float | true | Actual ERA5 value |
| `prediction` | float | true | Global mean prediction |
| `error` | float | true | `value - prediction` |
| `mae` | float | true | Mean Absolute Error (constant per file) |
| `rmse` | float | true | Root Mean Square Error (constant per file) |

---

## 6. Data Type Definitions

| Type | Description |
|------|-------------|
| float | Decimal number |
| int | Whole number |
| datetime | ISO-8601 timestamp |
| pickle | Python serialized object |

---

## 7. Schema Evolution Rules (Branch 1 → Branch 2)

Branch 1 schemas are intentionally minimal.
Branch 2 will expand schemas significantly.

### Adding a field

- Add to Stage 02 conversion logic
- Add to Stage 03 feature registry
- Update predictions schema if needed
- Update this document

### Removing a field

- Remove from Stage 02 conversion
- Remove from Stage 03 features
- Update predictions schema
- Validate downstream dependencies

### Changing a field type

- Update GRIB → Parquet conversion
- Update feature engineering
- Update evaluation logic

Branch 1 does not include schema validation; Branch 2 will.

---

## 8. Relationship to Other Documentation

This file complements:

- `DATA_DICTIONARY.md` — semantic meaning of each field
- `PIPELINE_FLOW.md` — how artifacts move through stages
- `ARCHITECTURE.md` — high‑level pipeline design

Together, these documents define the full data contract for Branch 1.

---

## 9. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com>  <br>
GitHub: <https://github.com/bdeng1018>
