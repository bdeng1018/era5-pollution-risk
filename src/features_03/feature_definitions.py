"""
Feature definitions (Branch 1).

This module provides the minimal placeholder structure for defining features
in the Branch 1 pipeline. Feature engineering is intentionally lightweight:
only a single identity transformation is included so the pipeline remains
runnable without real feature logic.

Branch 1 scope:
    - minimal feature registry
    - lightweight transformation functions
    - no metadata, no dependencies, no validation
    - supports only the single-variable Parquet produced in preprocessing_02

Branch 2 will introduce:
    - a full feature registry with rich transformations
    - metadata for each feature (units, description, provenance)
    - dependency graphs between features
    - validation rules and schema enforcement
    - spatial/temporal aggregations and multi-file feature generation
"""

from typing import Callable, Dict
import pandas as pd


def identity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Branch 1 placeholder feature: return the DataFrame unchanged.
    Useful for keeping the pipeline runnable without real transformations.
    """
    return df


# Minimal Branch 1 feature registry
FEATURES: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "identity": identity,
}


if __name__ == "__main__":
    # Running this module directly should do nothing in Branch 1.
    # This avoids Python's -m double-import warning.
    pass