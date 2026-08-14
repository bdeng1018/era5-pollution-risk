"""
Minimal feature engineering for Branch 1.

This script loads the single-variable Parquet file produced in preprocess_02,
applies lightweight placeholder transformations, and writes a features.parquet
file to the features directory. Branch 1 keeps feature engineering intentionally
simple so the pipeline remains runnable without real transformations.

Branch 1 scope:
    - load one Parquet file from intermediate/
    - apply minimal placeholder features
    - no metadata, no validation, no dependency graphs
    - supports only the single-variable ERA5 ingestion pipeline

Branch 2 will introduce:
    - full feature registry with real transformations
    - metadata per feature (units, description, provenance)
    - dependency graphs between features
    - spatial/temporal aggregations
    - lagged features and rolling windows
    - validation and schema checks
"""

from pathlib import Path

import pandas as pd

from src.features_03.feature_definitions import FEATURES
from src.utils.logging import get_logger
from src.utils.paths import Paths

logger = get_logger(__name__)


def build_features() -> Path:
    """
    Load Parquet → apply placeholder features → save features.parquet.

    Returns
    -------
    Path
        Path to the saved features.parquet file
    """

    logger.info("Starting Branch 1 feature engineering...")

    # Resolve paths
    paths = Paths()
    intermediate_dir = paths.intermediate_dir

    # Branch 1 assumption: exactly one Parquet file exists
    parquet_files = list(intermediate_dir.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError("No Parquet files found in intermediate_dir.")

    input_path = parquet_files[0]
    logger.info(f"Loading Parquet file: {input_path}")

    df = pd.read_parquet(input_path)

    # Apply Branch 1 placeholder features
    for name, func in FEATURES.items():
        logger.info(f"Applying feature: {name}")
        df = func(df)

    # Output file
    output_path = paths.features_dir / "features.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    logger.info(f"Saved features → {output_path}")
    logger.info(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    return output_path


def main():
    build_features()


if __name__ == "__main__":
    main()
