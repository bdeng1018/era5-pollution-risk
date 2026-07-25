"""
Minimal evaluation metrics for Branch 1.

Branch 1 uses a trivial baseline model (MeanPredictor), so evaluation metrics
are intentionally simple. This module provides lightweight functions for
computing basic metrics such as MAE and RMSE. These metrics are sufficient for
validating the end-to-end pipeline without introducing real evaluation
complexity.

Branch 2 Preview
----------------
Branch 2 will expand this module to include:
- R² and additional regression metrics
- residual analysis and diagnostic plots
- error distributions and summary statistics
- model comparison utilities
- integration with evaluation reports and visualization tools

Notes
-----
These functions are intentionally dependency-light and avoid external libraries
such as scikit-learn. They operate directly on NumPy arrays for maximum
simplicity and portability in Branch 1.
"""

import numpy as np


def mae(y_true, y_pred):
    """
    Compute Mean Absolute Error (MAE).

    MAE measures the average magnitude of errors between predictions and
    ground-truth values, without considering direction. It is a simple,
    interpretable metric suitable for baseline evaluation.

    Parameters
    ----------
    y_true : array-like
        Ground truth target values.
    y_pred : array-like
        Predicted values.

    Returns
    -------
    float
        Mean absolute error.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    """
    Compute Root Mean Squared Error (RMSE).

    RMSE penalizes larger errors more heavily than MAE and is useful for
    understanding the variance of prediction errors. In Branch 1, RMSE serves
    as a simple complementary metric to MAE.

    Parameters
    ----------
    y_true : array-like
        Ground truth target values.
    y_pred : array-like
        Predicted values.

    Returns
    -------
    float
        Root mean squared error.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
