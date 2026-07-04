"""
Paths Utility (Branch 2)
------------------------

Branch 2 requirements:
- Directories come from configs/paths.yml
- No auto-creation inside __init__
- validate_directories() handles creation
- metadata_dir and config_dir must exist in YAML
- project_root is resolved automatically (not from YAML)
"""

from pathlib import Path

from src.utils.config import load_paths


class Paths:
    """
    Branch 2 path manager.
    All required directories come from configs/paths.yml.
    """

    def __init__(self):

        cfg = load_paths()

        # MUST BE STRING — required by Stage 1 + Stage 2 tests
        self.project_root = str(Path(__file__).resolve().parents[2])

        # Convert to Path ONLY for joining
        root = Path(self.project_root)

        # All attributes must be strings
        self.raw_dir = str(root / cfg["raw_dir"])
        self.metadata_dir = str(root / cfg["metadata_dir"])
        self.intermediate_dir = str(root / cfg["intermediate_dir"])
        self.logs_dir = str(root / cfg["logs_dir"])
        self.features_dir = str(root / cfg["features_dir"])
        self.model_artifact_dir = str(root / cfg["model_artifact_dir"])
        self.predictions_dir = str(root / cfg["predictions_dir"])
        self.config_dir = str(root / cfg["config_dir"])
        self.chunk_output_dir = str(root / cfg["chunk_output_dir"])
        self.chunk_metadata_dir = str(root / cfg["chunk_metadata_dir"])


    def __repr__(self):
        return (
            "Paths(\n"
            f"  raw_dir={self.raw_dir},\n"
            f"  metadata_dir={self.metadata_dir},\n"
            f"  intermediate_dir={self.intermediate_dir},\n"
            f"  logs_dir={self.logs_dir},\n"
            f"  features_dir={self.features_dir},\n"
            f"  model_artifact_dir={self.model_artifact_dir},\n"
            f"  predictions_dir={self.predictions_dir},\n"
            f"  config_dir={self.config_dir},\n"
            f"  chunk_output_dir={self.chunk_output_dir},\n"
            f"  chunk_metadata_dir={self.chunk_metadata_dir}\n"
            ")"
        )
