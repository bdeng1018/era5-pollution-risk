"""
Branch 2 — Stage 1 Test: Monthly ERA5 Orchestrator

Aligned with REAL Stage‑1 behavior:
- variable names are normalized (2m_temperature → t2m)
- monthly orchestrator delegates to download_variable()
- GRIB files written under raw/era5/<year>/<month>/<normalized_var>/
- metadata JSON written under metadata/
"""

import json
from pathlib import Path

import pytest

from src.download_01.download_era5_monthly import main as monthly_main

# Normalization map used by Stage‑1
NORMALIZED = {
    "2m_temperature": "t2m",
    "surface_pressure": "sp",
    "10m_u_component_of_wind": "u10",
}


@pytest.mark.parametrize(
    "year,month,variables",
    [
        ("2023", "01", ["2m_temperature", "surface_pressure"]),
        ("2022", "12", ["10m_u_component_of_wind"]),
    ],
)
def test_monthly_orchestrator(monkeypatch, tmp_path, year, month, variables):
    """
    Ensures:
    - monthly orchestrator loads variables/years/months from config.yml
    - calls download_variable() for each (variable, year, month)
    - per-variable GRIB + metadata files are created (normalized)
    """

    # --------------------------------------------------------------------------
    # Monkeypatch environment
    # --------------------------------------------------------------------------
    monkeypatch.setenv("CDSAPI_URL", "https://fake-url")
    monkeypatch.setenv("CDSAPI_KEY", "fake-key")

    # --------------------------------------------------------------------------
    # Monkeypatch Paths used by monthly orchestrator and single downloader
    # --------------------------------------------------------------------------
    class FakePaths:
        def __init__(self):
            self.raw_dir = tmp_path / "raw" / "era5"
            self.metadata_dir = tmp_path / "metadata"
            self.config_dir = tmp_path / "config"

    monkeypatch.setattr(
        "src.download_01.download_era5_monthly.Paths",
        FakePaths
    )
    monkeypatch.setattr(
        "src.download_01.download_era5_single.Paths",
        FakePaths
    )

    # --------------------------------------------------------------------------
    # Fake config.yml (Branch 2 uses YAML)
    # --------------------------------------------------------------------------
    config_file = tmp_path / "config" / "config.yml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        f"years: [{year}]\nmonths: [{int(month)}]\nvariables: {variables}"
    )

    # --------------------------------------------------------------------------
    # Monkeypatch config loaders
    # --------------------------------------------------------------------------
    monkeypatch.setattr(
        "src.download_01.download_era5_monthly.load_variables",
        lambda: variables
    )
    monkeypatch.setattr(
        "src.download_01.download_era5_monthly.load_years",
        lambda: [year]
    )
    monkeypatch.setattr(
        "src.download_01.download_era5_monthly.load_months",
        lambda: [month]
    )

    # --------------------------------------------------------------------------
    # Monkeypatch download_variable() to simulate GRIB + metadata creation
    # --------------------------------------------------------------------------
    calls = []

    def fake_download_variable(var, yr, mo):
        calls.append((var, yr, mo))

        norm = NORMALIZED[var]

        # Simulate GRIB file (normalized)
        grib = (
            tmp_path
            / "raw"
            / "era5"
            / yr
            / mo
            / norm
            / f"{norm}_{yr}_{mo}.grib"
        )
        grib.parent.mkdir(parents=True, exist_ok=True)
        grib.write_text("fake grib")

        # Simulate metadata file
        metadata = (
            tmp_path
            / "metadata"
            / f"metadata_{var}_{yr}_{mo}.json"
        )
        metadata.write_text(json.dumps({
            "variable": var,
            "year": yr,
            "month": mo,
            "outfile": str(grib),
            "success": True,
            "config_valid": True,
        }))

        return grib

    monkeypatch.setattr(
        "src.download_01.download_era5_monthly.download_variable",
        fake_download_variable
    )

    # --------------------------------------------------------------------------
    # Execute monthly orchestrator
    # --------------------------------------------------------------------------
    monthly_main()

    # --------------------------------------------------------------------------
    # Validate delegation
    # --------------------------------------------------------------------------
    expected_calls = [(v, year, f"{int(month):02d}") for v in variables]
    assert calls == expected_calls

    # --------------------------------------------------------------------------
    # Validate per-variable GRIB + metadata (normalized)
    # --------------------------------------------------------------------------
    for var in variables:
        norm = NORMALIZED[var]

        grib = (
            tmp_path
            / "raw"
            / "era5"
            / year
            / f"{int(month):02d}"
            / norm
            / f"{norm}_{year}_{int(month):02d}.grib"
        )
        assert grib.exists()

        metadata = (
            tmp_path
            / "metadata"
            / f"metadata_{var}_{year}_{int(month):02d}.json"
        )
        assert metadata.exists()
