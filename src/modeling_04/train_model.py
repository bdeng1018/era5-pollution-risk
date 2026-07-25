"""
Minimal model training for Branch 1.

This module loads the features produced in features_03, fits a trivial baseline
model (MeanPredictor), and writes a model.pkl artifact to the top-level models/
directory. Branch 1 keeps modeling intentionally simple to maintain a runnable
end-to-end pipeline without introducing real ML complexity.

Branch 1 Scope
--------------
- Load features.parquet from data/features/
- Load minimal model configuration from model_config.yml
- Fit a trivial baseline model (mean predictor)
- Save a lightweight model artifact to models/model.pkl
- Provide a clean function signature for future expansion

Branch 2 Preview
----------------
Branch 2 will introduce:
- full model registry and dynamic model selection
- hyperparameter tuning and search strategies
- train/validation/test splits
- metrics, evaluation reports, and plots
- experiment tracking and model versioning
- integration with feature metadata and transformation graphs
"""

from pathlib import Path
import pickle
import pandas as pd

from src.utils.logging import get_logger
from src.utils.paths import Paths
from src.utils.config import load_model_config
from src.modeling_04.baseline_models import MeanPredictor


logger = get_logger(__name__)


def train_model() -> Path:
    """
    Train the Branch 1 baseline model and save the resulting artifact.

    Workflow
    --------
    1. Load model configuration
    2. Resolve feature and model artifact paths
    3. Load features.parquet
    4. Extract the target column
    5. Fit the MeanPredictor baseline model
    6. Serialize the model to models/model.pkl

    Returns
    -------
    Path
        Path to the saved model artifact.
    """

    logger.info("Starting Branch 1 model training...")

    # --------------------------------------------------------------------------
    # Load model configuration
    # --------------------------------------------------------------------------
    cfg = load_model_config()
    target_col = cfg["model"]["target"]

    # --------------------------------------------------------------------------
    # Resolve paths
    # --------------------------------------------------------------------------
    paths = Paths()
    features_file = paths.features_dir / "features.parquet"
    model_file = paths.model_artifact_dir / "model.pkl"

    logger.info(f"Resolved features file: {features_file}")
    logger.info(f"Resolved model artifact path: {model_file}")

    # --------------------------------------------------------------------------
    # Load features
    # --------------------------------------------------------------------------
    if not features_file.exists():
        raise FileNotFoundError(
            f"Features file not found: {features_file}. "
            "Ensure features_03 has been executed."
        )

    logger.info("Loading features...")
    df = pd.read_parquet(features_file)

    if target_col not in df.columns:
        raise ValueError(
            f"Target column '{target_col}' not found in features. "
            "Check model_config.yml and features_03 output."
        )

    y = df[target_col]
    logger.info(f"Loaded target column '{target_col}' with {len(y)} rows.")

    # --------------------------------------------------------------------------
    # Train baseline model
    # --------------------------------------------------------------------------
    logger.info("Fitting baseline mean predictor...")
    model = MeanPredictor()
    model.fit(y)

    logger.info(f"Baseline model fitted. Mean value = {model.mean_value:.4f}")

    # --------------------------------------------------------------------------
    # Save model artifact
    # --------------------------------------------------------------------------
    model_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving model artifact to: {model_file}")
    with open(model_file, "wb") as f:
        pickle.dump(model, f)

    logger.info("Model training complete.")
    logger.info(f"Saved model → {model_file}")

    return model_file


def main():
    train_model()


if __name__ == "__main__":
    main()
