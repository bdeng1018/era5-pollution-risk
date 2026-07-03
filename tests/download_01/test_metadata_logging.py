"""
Stage 1: Metadata logging tests for ERA5 download stage.

Purpose:
- Verify Stage 1 ALWAYS writes metadata (success, failure).
- Verify correct fields: status, timestamp, size_mb (success only).
- Ensure no real network calls or real sleep delays.
"""

import importlib
import json
import logging
from pathlib import Path

import pytest

from src.download_01.download_era5_single import download_variable


class FakeCDSClient:
    """
    Fake CDS API client:
    - fail_times: number of failures before success
    """

    def __init__(self, fail_times):
        self.fail_times = fail_times
        self.calls = 0

    def retrieve(self, dataset, request):
        class FakeResult:
            def __init__(self, outer):
                self.outer = outer

            def download(self, target):
                self.outer.calls += 1

                # Fail first N attempts
                if self.outer.calls <= self.outer.fail_times:
                    raise Exception("Simulated CDS API failure")

                # Success: write dummy GRIB file
                Path(target).write_text("dummy grib data")

        return FakeResult(self)


def read_metadata(path):
    with open(path, "r") as f:
        return json.load(f)


def test_metadata_success(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO)

    # Disable real sleep (retry backoff)
    monkeypatch.setattr("time.sleep", lambda _: None)

    # Patch environment
    monkeypatch.setenv("CDSAPI_URL", "https://cds.climate.copernicus.eu/api")
    monkeypatch.setenv("CDSAPI_KEY", "dummy")

    # Patch cfgrib/eccodes
    orig_import = importlib.import_module
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: object() if name in ("cfgrib", "eccodes") else orig_import(name)
    )

    # Patch CDS client: fail once, then succeed
    fake_client = FakeCDSClient(fail_times=1)
    monkeypatch.setattr(
        "src.download_01.download_era5_single.cdsapi.Client",
        lambda: fake_client
    )

    # Patch Paths
    def fake_init(self):
        self.raw_dir = tmp_path
        self.metadata_dir = tmp_path / "metadata"

    monkeypatch.setattr(
        "src.download_01.download_era5_single.Paths.__init__",
        fake_init
    )

    (tmp_path / "metadata").mkdir(parents=True, exist_ok=True)

    # Run Stage 1 download
    outfile = download_variable("2m_temperature", "2023", "09")

    # Metadata existence check (Stage 1 requirement)
    metadata_path = tmp_path / "metadata" / "2m_temperature_2023_09.json"
    assert metadata_path.exists()

    metadata = read_metadata(metadata_path)

    # Field correctness
    assert metadata["status"] == "success"
    assert metadata["variable"] == "2m_temperature"
    assert metadata["year"] == "2023"
    assert metadata["month"] == "09"
    assert metadata["size_mb"] > 0
    assert "timestamp" in metadata


def test_metadata_failure(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO)

    # Disable real sleep
    monkeypatch.setattr("time.sleep", lambda _: None)

    # Patch environment
    monkeypatch.setenv("CDSAPI_URL", "https://cds.climate.copernicus.eu/api")
    monkeypatch.setenv("CDSAPI_KEY", "dummy")

    # Patch cfgrib/eccodes
    orig_import = importlib.import_module
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: object() if name in ("cfgrib", "eccodes") else orig_import(name)
    )

    # Patch CDS client to always fail
    fake_client = FakeCDSClient(fail_times=10)
    monkeypatch.setattr(
        "src.download_01.download_era5_single.cdsapi.Client",
        lambda: fake_client
    )

    # Patch Paths
    def fake_init(self):
        self.raw_dir = tmp_path
        self.metadata_dir = tmp_path / "metadata"

    monkeypatch.setattr(
        "src.download_01.download_era5_single.Paths.__init__",
        fake_init
    )

    (tmp_path / "metadata").mkdir(parents=True, exist_ok=True)

    # Run Stage 1 download (returns None on failure)
    outfile = download_variable("2m_temperature", "2023", "09")
    assert outfile is None

    # Metadata existence check (Stage 1 requirement)
    metadata_path = tmp_path / "metadata" / "2m_temperature_2023_09.json"
    assert metadata_path.exists()

    metadata = read_metadata(metadata_path)

    # Field correctness
    assert metadata["status"] == "failed"
    assert metadata["variable"] == "2m_temperature"
    assert metadata["year"] == "2023"
    assert metadata["month"] == "09"
    assert "timestamp" in metadata
