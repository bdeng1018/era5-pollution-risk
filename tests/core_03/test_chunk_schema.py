"""
Tests for the Branch‑2 ChunkSchema class used in Stage 3.

Your current ChunkSchema API (as implemented in src/core_03/chunk_schema.py)
has the following behavior:

    - validate_columns(columns: list[str]) -> bool
        Ensures the provided column list matches the schema exactly
        in both content AND order.

    - validate_dtypes(dtypes: dict[str, str]) -> bool
        Ensures the provided dtype mapping matches the schema exactly.

    - describe() -> str
        Returns a human‑readable summary containing the schema version
        and column names.

This test suite reflects the correct, modern API.
"""

from src.core_03.chunk_schema import ChunkSchema


def test_schema_basic_validation():
    """
    Basic validation test for the simplified Branch‑2 ChunkSchema.

    Ensures:
    - column order must match exactly
    - dtype mapping must match exactly
    """

    schema = ChunkSchema(
        {
            "schema": {
                # Your real Stage 3 schema ALWAYS includes lat/lon
                "columns": ["time", "lat", "lon", "t2m"],
                "dtypes": {
                    "time": "string",
                    "lat": "float64",
                    "lon": "float64",
                    "t2m": "float64",
                },
                "version": "1.0",
            }
        }
    )

    # Column validation — correct order
    assert schema.validate_columns(["time", "lat", "lon", "t2m"])

    # Column validation — wrong order should fail
    assert not schema.validate_columns(["t2m", "time", "lat", "lon"])

    # Dtype validation — correct mapping
    df_dtypes = {
        "time": "string",
        "lat": "float64",
        "lon": "float64",
        "t2m": "float64",
    }
    assert schema.validate_dtypes(df_dtypes)

    # Dtype validation — incorrect dtype should fail
    df_bad = {
        "time": "string",
        "lat": "float64",
        "lon": "float64",
        "t2m": "int64",
    }
    assert not schema.validate_dtypes(df_bad)


def test_schema_description():
    """
    The describe() method should return a human‑readable summary
    containing the schema version and column names.
    """

    schema = ChunkSchema(
        {
            "schema": {
                # Description test can use a minimal schema
                "columns": ["time", "t2m"],
                "dtypes": {"time": "string", "t2m": "float64"},
                "version": "1.0",
            }
        }
    )

    desc = schema.describe()

    assert "ChunkSchema" in desc
    assert "time" in desc
    assert "t2m" in desc
    assert "1.0" in desc
