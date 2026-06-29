"""
Minimal evaluation script for Branch 1.

This script loads the baseline model trained in modeling_04, loads the feature
dataset, generates predictions, computes trivial metrics (MAE, RMSE), and writes
predictions to the top-level predictions/ directory.

Branch 1 keeps evaluation intentionally simple. Full evaluation workflows—
including real metrics, train/validation/test splits, residual analysis, plots,
diagnostics, and model comparison—will be introduced in Branch 2.

Notes
-----
Evaluation in Branch 1 exists primarily to validate the pipeline end-to-end.
The baseline model (MeanPredictor) returns a constant prediction, so metrics
serve only as sanity checks rather than meaningful performance indicators.
"""

from pathlib import Path
import pandas as pd

from src.utils.logging import get_logger
from src.utils.paths import Paths
from src.utils.config import load_config
from src.utils.model_io import load_model
from src.modeling_04.baseline_models import MeanPredictor  # ensures pickle resolution

from src.evaluation_05.metrics import mae, rmse

logger = get_logger(__name__)


def evaluate_model() -> Path:
    """
    Evaluate the Branch 1 baseline model.

    Workflow
    --------
    1. Load model configuration
    2. Resolve feature, model, and prediction paths
    3. Load features.parquet
    4. Extract target column
    5. Generate predictions using the baseline model
    6. Compute trivial metrics (MAE, RMSE)
    7. Save predictions to predictions/predictions.parquet

    Returns
    -------
    Path
        Path to the saved predictions file.
    """

    logger.info("Starting Branch 1 evaluation...")

    # --------------------------------------------------------------------------
    # Load configuration and resolve paths
    # --------------------------------------------------------------------------
    cfg = load_config()
    paths = Paths()

    features_path = paths.features_dir / "features.parquet"
    model_path = paths.model_artifact_dir / "model.pkl"
    predictions_path = paths.predictions_dir / "predictions.parquet"

    logger.info(f"Resolved features file: {features_path}")
    logger.info(f"Resolved model artifact: {model_path}")
    logger.info(f"Resolved predictions output: {predictions_path}")

    # --------------------------------------------------------------------------
    # Load model
    # --------------------------------------------------------------------------
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {model_path}. "
            "Ensure modeling_04.train_model has been executed."
        )

    logger.info("Loading baseline model...")
    model = load_model(model_path)

    # --------------------------------------------------------------------------
    # Load features
    # --------------------------------------------------------------------------
    if not features_path.exists():
        raise FileNotFoundError(
            f"Features file not found: {features_path}. "
            "Ensure features_03 has been executed."
        )

    logger.info("Loading features...")
    df = pd.read_parquet(features_path)

    target_col = cfg["model"]["target"]
    if target_col not in df.columns:
        raise ValueError(
            f"Target column '{target_col}' not found in features. "
            "Check model_config.yml and features_03 output."
        )

    y_true = df[target_col].to_numpy()
    logger.info(f"Loaded target column '{target_col}' with {len(y_true)} rows.")

    # --------------------------------------------------------------------------
    # Generate predictions
    # --------------------------------------------------------------------------
    logger.info("Generating predictions using baseline model...")
    y_pred = model.predict(len(df)).to_numpy()

    # --------------------------------------------------------------------------
    # Compute trivial metrics
    # --------------------------------------------------------------------------
    mae_value = mae(y_true, y_pred)
    rmse_value = rmse(y_true, y_pred)

    logger.info(f"MAE  (Branch 1): {mae_value:.4f}")
    logger.info(f"RMSE (Branch 1): {rmse_value:.4f}")

    # --------------------------------------------------------------------------
    # Save predictions
    # --------------------------------------------------------------------------
    predictions_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving predictions to: {predictions_path}")
    pred_df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    pred_df.to_parquet(predictions_path)

    logger.info("Branch 1 evaluation complete.")
    logger.info(f"Saved predictions → {predictions_path}")

    return predictions_path


def main():
    evaluate_model()


if __name__ == "__main__":
    main()