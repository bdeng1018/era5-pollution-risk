"""
Branch 2 — Environment & Config Validation Tests
Matches actual Branch 2 signatures:

    validate_environment(paths)
    validate_directories(paths)
    validate_config(paths)

Uses YAML config.yml and correct Paths class.
"""

import pytest

import src.download_01.download_era5_single as single_mod


# ------------------------------------------------------------------------------
# Fake Paths that satisfies Pyright (inherits from real Paths)
# ------------------------------------------------------------------------------
class FakePaths(single_mod.Paths):
    def __init__(self, tmp_path):
        # Override directories for tmp_path isolation
        self.raw_dir = tmp_path / "raw" / "era5"
        self.metadata_dir = tmp_path / "metadata"
        self.config_dir = tmp_path / "config"


# ------------------------------------------------------------------------------
# Environment validation
# ------------------------------------------------------------------------------
def test_environment_missing_credentials(monkeypatch, tmp_path):
    """Missing CDSAPI credentials should raise EnvironmentError."""
    monkeypatch.delenv("CDSAPI_URL", raising=False)
    monkeypatch.delenv("CDSAPI_KEY", raising=False)

    paths = FakePaths(tmp_path)

    with pytest.raises(EnvironmentError):
        single_mod.validate_environment(paths)


def test_environment_valid(monkeypatch, tmp_path):
    """Valid CDSAPI credentials should pass without raising."""
    monkeypatch.setenv("CDSAPI_URL", "https://fake-url")
    monkeypatch.setenv("CDSAPI_KEY", "fake-key")

    paths = FakePaths(tmp_path)

    # Should not raise
    single_mod.validate_environment(paths)


# ------------------------------------------------------------------------------
# Directory validation
# ------------------------------------------------------------------------------
def test_directory_auto_creation(tmp_path):
    """Missing directories should be auto-created in Branch 2."""
    paths = FakePaths(tmp_path)

    single_mod.validate_directories(paths)

    assert paths.raw_dir.exists()
    assert paths.metadata_dir.exists()
    assert paths.config_dir.exists()


# ------------------------------------------------------------------------------
# Config validation
# ------------------------------------------------------------------------------
def test_config_missing_returns_false(tmp_path):
    """Missing config.yml should return False."""
    paths = FakePaths(tmp_path)

    result = single_mod.validate_config(paths)
    assert result is False


def test_config_invalid_returns_false(tmp_path):
    """Invalid YAML config should return False."""
    paths = FakePaths(tmp_path)

    paths.config_dir.mkdir(parents=True, exist_ok=True)
    bad_cfg = paths.config_dir / "config.yml"
    bad_cfg.write_text("not: valid: yaml: :::")

    result = single_mod.validate_config(paths)
    assert result is False


def test_config_valid(tmp_path):
    """Valid YAML config should return True."""
    paths = FakePaths(tmp_path)

    paths.config_dir.mkdir(parents=True, exist_ok=True)
    good_cfg = paths.config_dir / "config.yml"
    good_cfg.write_text("years: [2023]\nmonths: [1]\nvariables: ['2m_temperature']")

    result = single_mod.validate_config(paths)
    assert result is True
