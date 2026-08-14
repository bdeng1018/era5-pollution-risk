"""
Paths Utility (Branch 1)
------------------------
This version defines ONLY the directories actually used in Branch 1.

Branch 1 is intentionally minimal:
- Single-variable ingestion (t2m only)
- One Parquet output in data/intermediate/
- No multi-variable batching
- No grib_dir or parquet_dir inside intermediate
- No schema/metadata/cfg directories
- Model artifacts saved via utils.model_io into models/

Branch 2 will introduce:
- intermediate/parquet/<variable>/<year>/<month>/
- intermediate/grib/<variable>/
- metadata/cfg directories
- expanded model artifact structure
"""

from pathlib import Path

from src.utils.config import load_paths


class Paths:
    """
    Centralized path manager for the ERA5 pipeline.

    Loads directory paths from configs/paths.yml and exposes them as attributes.
    Ensures only the directories *actually used in Branch 1* are created.

    Branch 1 produces:
        - raw GRIBs in data/raw/era5/
        - one Parquet file in data/intermediate/
        - features in data/features/
        - model artifacts in models/ (saved via utils.model_io)
        - predictions in data/predictions/

    Branch 1 does NOT produce:
        - intermediate/grib/
        - intermediate/parquet/
        - metadata/cfg folders
    """

    def __init__(self):
        cfg = load_paths()

        # Base project root
        self.project_root = Path(cfg.get("project_root", "."))

        # RAW DATA — untouched ECMWF downloads + extracted GRIBs + cfgrib .idx files
        self.raw_dir = self.project_root / cfg["raw_dir"]

        # INTERMEDIATE — Branch 1 produces exactly ONE file here:
        #   2m_temperature_2023_09.parquet
        #
        # No subfolders like intermediate/grib or intermediate/parquet.
        self.intermediate_dir = self.project_root / cfg["intermediate_dir"]

        # LOGS — runtime logs
        self.logs_dir = self.project_root / cfg["logs_dir"]

        # FEATURES — ML-ready features (Branch 1+)
        self.features_dir = self.project_root / cfg["features_dir"]

        # MODEL ARTIFACTS — trained model files
        self.model_artifact_dir = self.project_root / cfg["model_artifact_dir"]

        # PREDICTIONS — model outputs
        self.predictions_dir = self.project_root / cfg["predictions_dir"]

        # Branch 1: ONLY create directories that are actually written to.
        for d in [
            self.raw_dir,
            self.intermediate_dir,
            self.logs_dir,
            self.features_dir,
            self.model_artifact_dir,
            self.predictions_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def __repr__(self):
        return (
            "Paths(\n"
            f"  raw_dir={self.raw_dir},\n"
            f"  intermediate_dir={self.intermediate_dir},\n"
            f"  logs_dir={self.logs_dir},\n"
            f"  features_dir={self.features_dir},\n"
            f"  model_artifact_dir={self.model_artifact_dir},\n"
            f"  predictions_dir={self.predictions_dir}\n"
            ")"
        )
