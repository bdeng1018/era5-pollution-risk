"""
Branch 2 Configuration Loader
-----------------------------

Branch 2 requires:
- clean YAML loading
- explicit validation of required keys
- correct loading of paths.yml (including config_dir)
- correct loading of variables, years, months
- non-fatal config validation for ingestion

This module replaces the Branch 1 loader.
"""

from pathlib import Path

import yaml


# ------------------------------------------------------------------------------
# Generic YAML loader
# ------------------------------------------------------------------------------
def load_yaml(path: str | Path) -> dict:
    """Load a YAML file and return its contents as a dictionary."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ------------------------------------------------------------------------------
# Branch 2: Load paths.yml
# ------------------------------------------------------------------------------
def load_paths() -> dict:
    """
    Load configs/paths.yml relative to project root.
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "configs" / "paths.yml"
    cfg = load_yaml(path)

    required = [
        "raw_dir",
        "metadata_dir",
        "intermediate_dir",
        "logs_dir",
        "features_dir",
        "model_artifact_dir",
        "predictions_dir",
        "config_dir",
    ]

    missing = [k for k in required if k not in cfg]
    if missing:
        raise KeyError(f"Missing keys in paths.yml: {missing}")

    return cfg


# ------------------------------------------------------------------------------
# Branch 2: Load ingestion configs
# ------------------------------------------------------------------------------
def load_years() -> list[str]:
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "configs" / "years.yml"

    data = load_yaml(path)
    if not isinstance(data, list):
        raise TypeError(f"years.yml must be a list, got {type(data)}")

    return data

def load_months() -> list[str]:
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "configs" / "months.yml"

    data = load_yaml(path)
    if not isinstance(data, list):
        raise TypeError(f"months.yml must be a list, got {type(data)}")

    return data

def load_variables() -> list[str]:
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "configs" / "variables.yml"

    data = load_yaml(path)
    if not isinstance(data, list):
        raise TypeError(f"variables.yml must be a list, got {type(data)}")

    return data


def load_region() -> dict:
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "configs" / "region.yml"

    data = load_yaml(path)
    if not isinstance(data, dict):
        raise TypeError(f"region.yml must be a dict, got {type(data)}")

    return data


# ------------------------------------------------------------------------------
# Branch 2: Load master config (optional)
# ------------------------------------------------------------------------------
def load_master_config() -> dict:
    """
    Load configs/config.yml relative to project root.
    Branch 2 ingestion does not require this file, but notebooks do.
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "configs" / "config.yml"

    data = load_yaml(path)
    if not isinstance(data, dict):
        raise TypeError(f"config.yml must be a dict, got {type(data)}")

    return data


# ------------------------------------------------------------------------------
# Branch 2 unified loader (used by notebooks)
# ------------------------------------------------------------------------------
def load_config() -> dict:
    """
    Unified configuration loader for notebooks and later pipeline stages.
    Branch 2 ingestion does NOT require this.
    """
    master = load_master_config()

    return {
        "paths": load_paths(),
        "era5": master.get("era5", {}),
        "model": master.get("model", {}),
    }


if __name__ == "__main__":
    print(load_config())
