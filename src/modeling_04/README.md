# modeling_04 — Branch 1 Modeling

Branch 1 provides a minimal placeholder workflow for model training. The goal at
this stage is to maintain a clean pipeline structure and ensure that the feature
engineering stage produces an output that can be consumed by a basic model
script. No real machine learning is performed in Branch 1.

This directory will expand significantly in Branch 2, where full modeling,
hyperparameter tuning, and evaluation workflows will be introduced.

---

## 📌 Branch 1 Scope

Branch 1 modeling is intentionally lightweight:

- Load `features.parquet` from `data/features/`
- Fit a trivial baseline model (`MeanPredictor`)
- Save a minimal `model.pkl` artifact to `models/model.pkl`
- Provide a clean function signature for future expansion
- Keep the pipeline runnable end‑to‑end without introducing ML complexity

The purpose is structural: ensure downstream stages (evaluation, notebooks,
later modeling branches) have predictable inputs and interfaces.

---

## 📁 Files

```text
modeling_04/
├── __init__.py          # Package initializer with Branch 1 documentation
├── baseline_models.py   # Minimal baseline model classes (MeanPredictor)
├── model_config.yml     # Branch 1 model configuration
└── train_model.py       # Minimal Branch 1 model training script
```

---

## ⚙️ How It Works

The Branch 1 `train_model.py` script:

1. Loads model configuration from `model_config.yml`
2. Loads `features.parquet` from `data/features/` 
3. Extracts the target column specified in the config
4. Fits the `MeanPredictor` baseline model
 - Stores the mean of the target variable
 - Returns the mean for all predictions
5. Saves `model.pkl` to the top‑level `models/` directory
6. Logs all actions using the shared logging utilities

This keeps the pipeline functional while leaving room for Branch 2 expansion.

---

## 🧠 Why a Baseline Model?

Branch 1 uses a trivial baseline model for three reasons:

### 1. Pipeline validation

Ensures the pipeline runs end‑to‑end without requiring real ML logic.

### 2. Deterministic behavior

A mean predictor has no hyperparameters, no randomness, and no dependencies.

### 3. Pickle import‑path stability

Model classes must live in a dedicated module (`baseline_models.py`) so that 
pickle can resolve:

```markdown
src.modeling_04.baseline_models.MeanPredictor
```

This guarantees Stage 5 evaluation can load the model artifact reliably.

---

## 🔜 Branch 2 Preview

Branch 2 will introduce:

- full model registry  
- hyperparameter tuning  
- train/validation/test splits  
- cross‑validation  
- model metadata and provenance
- experiment tracking  
- multiple model families (linear, tree‑based, neural)  
- model comparison and selection 
- config-driven model construction 

None of these are included in Branch 1 to maintain a clean MVP.

---

## 📦 Usage

Model training is triggered via the Makefile:

```markdown
make train
```

Or directly:

```markdown
python src.modeling_04.train_model
```

---

## 📬 Notes

Branch 1 keeps this stage intentionally simple. The purpose is to maintain a 
clean pipeline structure and ensure downstream modules have predictable inputs, 
without committing to a full modeling framework yet.

Model artifacts are written to the top‑level `models/` directory (not `data/`), 
consistent with the project’s directory contract.