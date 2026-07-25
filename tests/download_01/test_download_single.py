"""
Branch 2 — Stage 1 Test: Single-Variable ERA5 Downloader

Aligned with REAL Branch‑2 behavior:
    - variable names are normalized (2m_temperature → t2m)
    - GRIB files written under raw/era5/<year>/<month>/<normalized_var>/
    - metadata JSON written under metadata/ on SUCCESS ONLY
"""

import json
from pathlib import Path

import pytest

from src.download_01.download_era5_single import download_variable

# Mapping from long variable names → normalized ERA5 codes
NORMALIZED = {
    "2m_temperature": "t2m",
    "surface_pressure": "sp",
    "10m_u_component_of_wind": "u10",
}


@pytest.mark.parametrize(
    "variable,year,month",
    [
        ("2m_temperature", "2023", "01"),
        ("surface_pressure", "2022", "12"),
        ("10m_u_component_of_wind", "2020", "07"),
    ],
)
def test_download_single_variable(monkeypatch, tmp_path, variable, year, month):
    """
    Ensures:
    - fake CDSAPI retrieve is called
    - GRIB file is created in the correct normalized Branch‑2 directory
    - metadata JSON is created on SUCCESS and contains correct fields
    """

    # ----------------------------------------------------------------------
    # Monkeypatch environment
    # ----------------------------------------------------------------------
    monkeypatch.setenv("CDSAPI_URL", "https://fake-url")
    monkeypatch.setenv("CDSAPI_KEY", "fake-key")

    # ----------------------------------------------------------------------
    # Monkeypatch cdsapi retrieve
    # ----------------------------------------------------------------------
    def fake_retrieve(dataset, request, outfile):
        Path(outfile).parent.mkdir(parents=True, exist_ok=True)
        Path(outfile).write_text("fake grib")

    monkeypatch.setattr(
        "src.download_01.download_era5_single.client.retrieve", fake_retrieve
    )

    # ----------------------------------------------------------------------
    # Monkeypatch the Paths class
    # ----------------------------------------------------------------------
    class FakePaths:
        def __init__(self):
            self.raw_dir = tmp_path / "raw" / "era5"
            self.metadata_dir = tmp_path / "metadata"
            self.config_dir = tmp_path / "config"

    monkeypatch.setattr("src.download_01.download_era5_single.Paths", FakePaths)

    # ----------------------------------------------------------------------
    # Fake config.yml
    # ----------------------------------------------------------------------
    config_file = tmp_path / "config" / "config.yml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        f"years: [{year}]\nmonths: [{int(month)}]\nvariables: ['{variable}']"
    )

    # ----------------------------------------------------------------------
    # Execute download
    # ----------------------------------------------------------------------
    result = download_variable(variable, year, month)

    # ----------------------------------------------------------------------
    # Validate GRIB output (normalized path)
    # ----------------------------------------------------------------------
    norm = NORMALIZED[variable]

    expected_grib = (
        tmp_path / "raw" / "era5" / year / month / norm / f"{norm}_{year}_{month}.grib"
    )

    assert result is not None
    assert expected_grib.exists()

    # ----------------------------------------------------------------------
    # Validate metadata output (SUCCESS ONLY)
    # ----------------------------------------------------------------------
    metadata_file = tmp_path / "metadata" / f"metadata_{variable}_{year}_{month}.json"
    assert metadata_file.exists()

    metadata = json.loads(metadata_file.read_text())
    assert metadata["variable"] == variable
    assert metadata["year"] == year
    assert metadata["month"] == month
    assert metadata["success"] is True
    assert metadata["config_valid"] is True
    assert metadata["outfile"] == str(expected_grib)
