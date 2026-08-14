"""
Branch 1 Smoke Tests — ERA5 Download Stage
==========================================

Purpose
-------
These tests provide *minimal, non‑networked* validation of the ERA5 download
modules. Their sole purpose is to confirm that:

- modules import correctly
- main download functions execute without raising exceptions
- logging works as expected
- mocked CDS API interactions behave consistently

What Branch 1 *Does Not* Test
-----------------------------
Branch 1 intentionally avoids all real ingestion behavior, including:

- real CDS API calls
- network-dependent behavior
- file existence assertions
- skip‑logic correctness
- schema validation
- metadata checks
- multi‑variable ingestion
- GRIB/ZIP/Parquet correctness

Why?
----
Branch 1 is designed to be fast, deterministic, and environment‑agnostic.
It should run cleanly on any machine without requiring:

- a valid ~/.cdsapirc
- network access
- pre-existing data files
- real GRIB or Parquet artifacts

Branch 2 Roadmap
----------------
Branch 2 will introduce full ingestion validation, including:

- pytest fixtures for synthetic GRIB/ZIP/Parquet files
- file existence checks and skip‑logic correctness
- schema validation and metadata extraction tests
- multi‑variable ingestion tests
- full CDS API mocking (retrieve + download + error paths)
- deterministic path resolution tests
"""

# ==============================================================================
# Branch 1 Constraints
# ==============================================================================
# These tests intentionally avoid executing real ingestion logic.
# They validate only:
# - module import stability
# - function execution with a mocked CDS API
# - logging behavior
#
# No real downloads, no skip-logic correctness, and no file assertions.
# ==============================================================================

import logging
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_cdsapi(monkeypatch):
    """
    Patch cdsapi.Client BEFORE any download modules import it.

    This ensures:
    - no real CDS API calls
    - no ~/.cdsapirc required
    - module import succeeds even if cdsapi is not installed
    """

    # Create a fake cdsapi module
    fake_cdsapi = MagicMock()

    # Mock Client() → returns a mock client
    mock_client = MagicMock()

    # Mock retrieve().download()
    mock_result = MagicMock()
    mock_result.download.return_value = None
    mock_client.retrieve.return_value = mock_result

    fake_cdsapi.Client = lambda: mock_client

    # Insert fake module into sys.modules BEFORE imports occur
    sys.modules["cdsapi"] = fake_cdsapi


def test_download_single_smoke():
    from src.download_01.download_era5_single import download_variable
    download_variable("2m_temperature", "2023", "09")


def test_download_monthly_smoke(caplog):
    from src.download_01.download_era5_monthly import main as download_monthly

    caplog.set_level(logging.INFO, logger="src.download_01.download_era5_monthly")
    download_monthly()

    assert "starting branch 1 era5 monthly downloads" in caplog.text.lower()


# ==============================================================================
# Branch 2 Roadmap
# ==============================================================================
# Future tests will add:
# - skip-logic correctness tests
# - synthetic GRIB/ZIP fixtures
# - schema validation tests
# - metadata extraction tests
# - multi-variable ingestion tests
# - full CDS API mock suite (retrieve + download + error paths)
# ==============================================================================
