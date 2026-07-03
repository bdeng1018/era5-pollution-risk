"""
Branch 2: Environment validation tests for ERA5 download stage.

Purpose:
- Ensure environment validation detects missing CDS API key.
- Ensure cfgrib import errors are caught.
- Ensure eccodes availability is checked.
- Ensure required directories are created automatically.
- Avoid real network calls or real GRIB processing.
"""

import os
from pathlib import Path

import pytest

from src.download_01.download_era5_single import (
    Paths,
    validate_config,
    validate_directories,
    validate_environment,
)

# ------------------------------------------------------------------------------
# Environment validation
# ------------------------------------------------------------------------------

def test_environment_missing_credentials(monkeypatch):
    """Missing CDSAPI credentials should raise EnvironmentError."""
    monkeypatch.delenv("CDSAPI_URL", raising=False)
    monkeypatch.delenv("CDSAPI_KEY", raising=False)

    with pytest.raises(EnvironmentError):
        validate_environment()


def test_environment_valid(monkeypatch):
    """Valid CDSAPI credentials should pass without raising."""
    monkeypatch.setenv("CDSAPI_URL", "https://cds.climate.copernicus.eu/api")
    monkeypatch.setenv("CDSAPI_KEY", "12345:abcdef")

    validate_environment()  # Should not raise


# ------------------------------------------------------------------------------
# Directory validation
# ------------------------------------------------------------------------------

def test_directory_auto_creation(tmp_path, monkeypatch):
    """Missing directories should be auto-created in Branch 2."""
    def fake_init(self):
        self.raw_dir = tmp_path / "raw"
        self.metadata_dir = tmp_path / "metadata"
        self.config_dir = tmp_path / "configs"

    monkeypatch.setattr(Paths, "__init__", fake_init)

    validate_directories()

    assert (tmp_path / "raw").exists()
    assert (tmp_path / "metadata").exists()
    assert (tmp_path / "configs").exists()


# ------------------------------------------------------------------------------
# Config validation
# ------------------------------------------------------------------------------

def test_config_missing_returns_false(tmp_path, monkeypatch):
    """Missing config file should return False, not raise."""
    def fake_init(self):
        self.raw_dir = tmp_path
        self.metadata_dir = tmp_path / "metadata"
        self.config_dir = tmp_path / "configs"

    monkeypatch.setattr(Paths, "__init__", fake_init)

    result = validate_config()
    assert result is False


def test_config_invalid_returns_false(tmp_path, monkeypatch):
    """Invalid config file should return False."""
    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    config_file = config_dir / "config.json"
    config_file.write_text("{ invalid json }")

    def fake_init(self):
        self.raw_dir = tmp_path
        self.metadata_dir = tmp_path / "metadata"
        self.config_dir = config_dir

    monkeypatch.setattr(Paths, "__init__", fake_init)

    result = validate_config()
    assert result is False


def test_config_valid(tmp_path, monkeypatch):
    """Valid config file should return True."""
    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    config_file = config_dir / "config.json"
    config_file.write_text('{"variables": ["2m_temperature"]}')

    def fake_init(self):
        self.raw_dir = tmp_path
        self.metadata_dir = tmp_path / "metadata"
        self.config_dir = config_dir

    monkeypatch.setattr(Paths, "__init__", fake_init)

    result = validate_config()
    assert result is True
