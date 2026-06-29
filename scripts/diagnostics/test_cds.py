"""
CDS API Connectivity Test

This diagnostic script performs a minimal ERA5 data request to verify that the
local environment is correctly configured for Climate Data Store (CDS) API
access. It is not part of the pipeline and should be used only for debugging
environment or authentication issues.

It checks:
- Authentication via ~/.cdsapirc
- Network connectivity to the CDS API
- Functionality of the cdsapi Python client
- Ability to retrieve and download a small ERA5 file

Expected Output:
    A file named 'test.nc' in the working directory.

If this script succeeds, the full ERA5 monthly downloader will work.
"""

import cdsapi


def run_test_request():
    """
    Execute a minimal ERA5 Single-Level request to confirm that the CDS API is
    reachable and authentication is valid.

    Downloads:
        - Variable: 2m_temperature
        - Date: 2023-06-01 at 12:00 UTC
        - Region: Small LA Basin bounding box
        - Format: NetCDF

    Returns
    -------
    None
        Downloads 'test.nc' to the working directory.
    """
    client = cdsapi.Client()

    request = {
        "product_type": "reanalysis",
        "variable": "2m_temperature",
        "year": "2023",
        "month": "06",
        "day": "01",
        "time": "12:00",
        "data_format": "netcdf",
        "area": [35, -120, 33, -116],  # (North, West, South, East)
    }

    print("→ Submitting test request to CDS...")
    client.retrieve("reanalysis-era5-single-levels", request).download("test.nc")
    print("✓ Test file downloaded successfully: test.nc")


def main():
    """Entry point for the CDS connectivity test."""
    print("\nStarting CDS API connectivity test...\n")
    run_test_request()
    print("\nAll checks passed. CDS API is functioning correctly.\n")


if __name__ == "__main__":
    main()