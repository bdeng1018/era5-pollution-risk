"""
Configuration loading utilities for the ERA5 pipeline.

This module provides:
- a safe YAML loader with clear error messages
- dedicated loaders for paths, years, months, variables, and model configs
- a unified `load_config()` function used by notebooks and Branch 1 scripts

Branch 1 only requires:
- paths (directory structure)
- model configuration (target column)

All other YAML files remain available for earlier pipeline stages but are
not included in the unified config to keep Branch 1 lightweight.
"""

from pathlib import Path
import yaml


def load_yaml(path: str | Path) -> dict:
    """Load a YAML file and return its contents as a dictionary."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_paths() -> dict:
    """Load `paths.yml` from the configs directory."""
    return load_yaml(Path("configs/paths.yml"))


def load_years() -> dict:
    """Load `years.yml` from the configs directory."""
    return load_yaml(Path("configs/years.yml"))


def load_months() -> dict:
    """Load `months.yml` from the configs directory."""
    return load_yaml(Path("configs/months.yml"))


def load_variables() -> dict:
    """Load `variables.yml` from the configs directory."""
    return load_yaml(Path("configs/variables.yml"))


def load_model_config() -> dict:
    """Load `config.yml` (model configuration) from the configs directory."""
    return load_yaml(Path("configs/config.yml"))


def load_config() -> dict:
    """
    Unified configuration loader for notebooks and Branch 1 pipeline scripts.

    Returns:
        {
            "paths": <directory configuration>,
            "model": <model target column>,
        }
    """
    return {
        "paths": load_paths(),
        "model": load_model_config()["model"],
    }


if __name__ == "__main__":
    print(load_config())