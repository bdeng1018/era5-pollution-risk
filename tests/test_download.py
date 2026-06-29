"""
Branch 1 smoke tests for the ERA5 download stage.

These tests verify only that:
- modules import correctly
- main download functions execute without raising exceptions
- skip logic runs cleanly when files already exist

Branch 1 intentionally avoids:
- file existence assertions
- schema validation
- metadata checks
- multi-variable testing
- network-dependent behavior

Branch 2 will add:
- pytest fixtures
- file existence checks
- schema validation
- metadata tests
- multi-variable tests
- full download mocking
"""

import logging
import pytest

from src.download_01.download_era5_single import download_variable
from src.download_01.download_era5_monthly import main as download_monthly


def test_download_single_smoke():
    """
    Smoke test: ensure download_variable runs without crashing.

    Branch 1 uses a minimal request:
    - one variable
    - one year
    - one month

    No actual download is required because skip logic handles existing files.
    """
    # If skip logic is correct, this should run instantly.
    download_variable("2m_temperature", "2023", "09")


def test_download_monthly_smoke(caplog):
    """
    Smoke test: ensure the monthly downloader runs without crashing.

    Branch 1 uses:
    - a single month (09)
    - a single year (2023)

    If the file already exists, skip logic should trigger cleanly and log
    a message indicating the file is being skipped.
    """
    caplog.set_level(logging.INFO, logger="src.download_01.download_era5_monthly")

    download_monthly()

    # Skip logic should produce a recognizable log message.
    log_text = caplog.text.lower()
    assert ("skipping" in log_text) or ("exists" in log_text), (
        "Skip logic did not produce expected log output."
    )