"""
Baseline models for Branch 1.

This module contains the minimal baseline model classes used in Branch 1 of the
pipeline. The purpose of these models is not to provide meaningful predictive
performance, but to supply a stable, import‑safe model interface that downstream
stages (training, evaluation, and later Branch 2 components) can rely on.

Branch 1 Scope
--------------
- Provide a trivial baseline model (MeanPredictor)
- Support a minimal fit/predict API
- Ensure the model class lives in a dedicated module so pickle can correctly
  resolve its import path during model loading in Stage 5 evaluation
- Avoid any real ML complexity: no hyperparameters, no model families, no
  training loops, no metrics, no validation

Why This Module Exists
----------------------
Python's pickle requires that model classes be importable from a stable module
path. If the model class were defined inside train_model.py, pickle would embed
that path and Stage 5 evaluation would fail to load the artifact. Placing
MeanPredictor here ensures:

- A stable import path: src.modeling_04.baseline_models.MeanPredictor
- Cross‑stage compatibility (training → evaluation)
- Clean separation between model definitions and training logic

Branch 2 Preview
----------------
In Branch 2, this module will expand to include:
- Multiple model families (linear models, tree models, neural nets)
- A model registry for dynamic model selection
- Config‑driven model construction
- Hyperparameter tuning
- Metadata and provenance tracking
- Integration with feature metadata and transformation graphs

Classes
-------
MeanPredictor
    A trivial baseline model that stores the mean of the target variable and
    returns it for all predictions. Used only to keep the pipeline runnable in
    Branch 1.

Notes
-----
This module intentionally keeps modeling extremely simple. Its purpose is to
provide a predictable interface and a stable serialization path, not to perform
real machine learning. Full modeling functionality arrives in Branch 2.
"""

import pandas as pd


class MeanPredictor:
    """
    A trivial baseline model used in Branch 1.

    The MeanPredictor stores the mean of the target variable during `fit` and
    returns that same value for all predictions. This model is intentionally
    simple and exists only to keep the pipeline runnable end‑to‑end in Branch 1.

    Purpose (Branch 1)
    ------------------
    - Provide a minimal, import‑safe model class for serialization.
    - Support a clean `fit` / `predict` API compatible with later model classes.
    - Enable Stage 4 (training) and Stage 5 (evaluation) to operate without
      introducing real ML complexity.
    - Ensure pickle can resolve the class path:
          src.modeling_04.baseline_models.MeanPredictor

    Why This Model Exists
    ----------------------
    Branch 1 focuses on pipeline structure, not predictive performance. A simple
    mean predictor:
    - avoids hyperparameters,
    - avoids dependencies on sklearn/xgboost/lightgbm,
    - avoids train/validation/test splits,
    - avoids metrics and evaluation logic,
    - guarantees deterministic behavior.

    Branch 2 Preview
    ----------------
    In Branch 2, this module will expand to include:
    - multiple model families (linear, tree‑based, neural),
    - config‑driven model construction,
    - hyperparameter tuning,
    - metadata and provenance tracking,
    - a full model registry.

    Attributes
    ----------
    mean_value : float or None
        The stored mean of the target variable. Set during `fit`.

    Methods
    -------
    fit(y)
        Computes and stores the mean of the target variable.

    predict(n)
        Returns a pandas Series of length `n` filled with the stored mean value.
    """

    def __init__(self):
        self.mean_value = None

    def fit(self, y: pd.Series):
        """
        Compute and store the mean of the target variable.

        Parameters
        ----------
        y : pd.Series
            Target values.
        """
        self.mean_value = float(y.mean())

    def predict(self, n: int) -> pd.Series:
        """
        Predict the stored mean value for n observations.

        Parameters
        ----------
        n : int
            Number of predictions to generate.

        Returns
        -------
        pd.Series
            Series of length n filled with the stored mean value.
        """
        return pd.Series([self.mean_value] * n)
