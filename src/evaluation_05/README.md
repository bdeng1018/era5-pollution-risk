# evaluation_05 — Branch 1 Evaluation

Branch 1 provides a minimal placeholder workflow for model evaluation. The goal 
at this stage is not to compute meaningful metrics, but to validate that the 
pipeline runs end‑to‑end:

1. Features are generated correctly  
2. The baseline model is trained and saved  
3. The evaluation stage can load the model and produce predictions  
4. A predictions file is written to `data/predictions/`  

This ensures the pipeline is structurally complete before introducing real 
evaluation logic in Branch 2.

---

## 📌 Branch 1 Scope

Evaluation in Branch 1 is intentionally simple:

- Load `model.pkl` from `models/`
- Load `features.parquet` from `data/features/`
- Generate predictions using the baseline model
- Compute trivial metrics (MAE, RMSE)
- Save predictions to `data/predictions/predictions.parquet`
- Log all evaluation steps

The purpose is to confirm that the modeling stage produces a usable artifact and 
that the evaluation stage can consume it predictably.

---

## 📁 Files

```text
evaluation_05/
├── __init__.py          # Package initializer with Branch 1 documentation
├── metrics.py           # Minimal MAE/RMSE metric functions
└── evaluate_model.py    # Minimal Branch 1 evaluation script
```

---

## ⚙️ How It Works

The Branch 1 `evaluate_model.py` script performs:

1. Load pipeline configuration (`load_config`)
2. Resolve feature, model, and prediction paths via `Paths`
3. Load the trained baseline model (`models/model.pkl`)
4. Load the feature dataset (`data/features/features.parquet`)
5. Extract the target column
6. Generate predictions (constant mean value)
7. Compute trivial metrics (MAE, RMSE)
8. Save predictions to `data/predictions/predictions.parquet`
9. Log evaluation results

This validates the pipeline without requiring a real pollution‑risk model. 

---

## 🧠 Why Evaluation Exists in Branch 1

Branch 1 evaluation serves three structural purposes:

### 1. Pipeline validation
Ensures that model artifacts can be loaded and used without errors. 

### 2. Interface stabilization
Defines the expected inputs/outputs for future evaluation stages.

### 3. Pickle import‑path stability
Evaluation must import the baseline model class from: 

```markdown
src.modeling_04.baseline_models.MeanPredictor
```

so that pickle can resolve the model artifact correctly. 

---

## 🔜 Branch 2 Preview

Branch 2 will introduce:

- real evaluation metrics (MAE, RMSE, R²)
- train/validation/test splits
- residual analysis
- prediction vs target plots
- model comparison and selection
- experiment tracking
- evaluation reports and artifacts

None of these are included in Branch 1 to keep the MVP clean and focused. 

---

## 📦 Usage

Evaluation is triggered via the Makefile:

```markdown
make evaluate
```

Or directly:

```markdown
python src.evaluation_05.evaluate_model
```

---

## 📬 Notes

Branch 1 evaluation is a structural placeholder. Its purpose is to ensure the 
pipeline is complete, testable, and ready for more advanced modeling and 
evaluation workflows in Branch 2. 

Prediction outputs are written to the top‑level `data/predictions/` directory, 
consistent with the project’s directory contract. 

All `__pycache__/` directories should be ignored and removed; they are not part 
of the pipeline and should never be committed.