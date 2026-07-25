"""
Branch 2 — Retry Logic Tests for Single-Variable ERA5 Downloader

Aligned with REAL Stage‑1 behavior:
- variable names are normalized (2m_temperature → t2m)
- GRIB files written under raw/era5/<year>/<month>/<normalized_var>/
- metadata JSON written only on success
- retry loop retries on failure and stops on success
"""

import json
from pathlib import Path

import src.download_01.download_era5_single as single_mod

# Normalization map used by Stage‑1
NORMALIZED = {
    "2m_temperature": "t2m",
    "surface_pressure": "sp",
    "10m_u_component_of_wind": "u10",
}


class FakeCDSClient:
    """Simulates CDSAPI retrieve() with controlled failures."""

    def __init__(self, fail_times):
        self.fail_times = fail_times
        self.calls = 0

    def retrieve(self, dataset, request, target):
        self.calls += 1

        if self.calls <= self.fail_times:
            raise Exception("Simulated CDS API failure")

        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_text("fake grib")


def read_metadata(path: Path):
    return json.loads(path.read_text())


# ----------------------------------------------------------------------
# SUCCESS AFTER FAILURES
# ----------------------------------------------------------------------
def test_retry_success_after_failures(monkeypatch, tmp_path):
    monkeypatch.setattr("time.sleep", lambda _: None)

    monkeypatch.setenv("CDSAPI_URL", "https://fake-url")
    monkeypatch.setenv("CDSAPI_KEY", "fake-key")

    class FakePaths(single_mod.Paths):
        def __init__(self):
            self.raw_dir = tmp_path / "raw" / "era5"
            self.metadata_dir = tmp_path / "metadata"
            self.config_dir = tmp_path / "config"

    monkeypatch.setattr("src.download_01.download_era5_single.Paths", FakePaths)

    cfg = tmp_path / "config" / "config.yml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("years: [2023]\nmonths: [9]\nvariables: ['2m_temperature']")

    fake_client = FakeCDSClient(fail_times=2)
    monkeypatch.setattr("src.download_01.download_era5_single.client", fake_client)

    result = single_mod.download_variable("2m_temperature", "2023", "09")

    # Should succeed on 3rd attempt
    assert fake_client.calls == 3
    assert result is not None

    norm = NORMALIZED["2m_temperature"]

    expected_grib = (
        tmp_path / "raw" / "era5" / "2023" / "09" / norm / f"{norm}_2023_09.grib"
    )
    assert expected_grib.exists()

    metadata_file = tmp_path / "metadata" / "metadata_2m_temperature_2023_09.json"
    assert metadata_file.exists()

    metadata = read_metadata(metadata_file)
    assert metadata["variable"] == "2m_temperature"
    assert metadata["year"] == "2023"
    assert metadata["month"] == "09"
    assert metadata["success"] is True
    assert metadata["config_valid"] is True
    assert metadata["outfile"] == str(expected_grib)


# ----------------------------------------------------------------------
# EXHAUSTION (all retries fail)
# ----------------------------------------------------------------------
def test_retry_exhaustion(monkeypatch, tmp_path):
    monkeypatch.setattr("time.sleep", lambda _: None)

    monkeypatch.setenv("CDSAPI_URL", "https://fake-url")
    monkeypatch.setenv("CDSAPI_KEY", "fake-key")

    class FakePaths(single_mod.Paths):
        def __init__(self):
            self.raw_dir = tmp_path / "raw" / "era5"
            self.metadata_dir = tmp_path / "metadata"
            self.config_dir = tmp_path / "config"

    monkeypatch.setattr("src.download_01.download_era5_single.Paths", FakePaths)

    cfg = tmp_path / "config" / "config.yml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("years: [2023]\nmonths: [9]\nvariables: ['2m_temperature']")

    fake_client = FakeCDSClient(fail_times=10)
    monkeypatch.setattr("src.download_01.download_era5_single.client", fake_client)

    result = single_mod.download_variable("2m_temperature", "2023", "09")

    # Should fail after 3 attempts
    assert fake_client.calls == 3
    assert result is None

    # REAL behavior: no metadata written on failure
    metadata_file = tmp_path / "metadata" / "metadata_2m_temperature_2023_09.json"
    assert not metadata_file.exists()
