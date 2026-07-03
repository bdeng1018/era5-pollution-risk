"""
Branch 2: Retry logic tests for ERA5 download stage.

Purpose:
- Verify that download_variable() retries on failure.
- Verify that retry loop stops on success.
- Verify metadata is written for both success and failure.
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


def test_retry_success_after_failures(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO)

    # Disable real sleep (backoff)
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

    # Patch CDS client
    fake_client = FakeCDSClient(fail_times=2)
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

    # Run download
    outfile = download_variable("2m_temperature", "2023", "09")

    # Fake client should be called 3 times
    assert fake_client.calls == 3

    # Metadata
    metadata_path = tmp_path / "metadata" / "2m_temperature_2023_09.json"
    assert metadata_path.exists()

    metadata = read_metadata(metadata_path)
    assert metadata["status"] == "success"
    assert metadata["size_mb"] > 0
    assert "timestamp" in metadata


def test_retry_exhaustion(monkeypatch, tmp_path, caplog):
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

    # Run download (returns None on failure)
    outfile = download_variable("2m_temperature", "2023", "09")
    assert outfile is None

    # Fake client should be called max_retries = 3
    assert fake_client.calls == 3

    # Metadata
    metadata_path = tmp_path / "metadata" / "2m_temperature_2023_09.json"
    assert metadata_path.exists()

    metadata = read_metadata(metadata_path)
    assert metadata["status"] == "failed"
    assert "timestamp" in metadata
