from src.core_03.chunk_schema import ChunkSchema


def test_schema_basic_validation():
    schema = ChunkSchema({
        "schema": {
            "columns": ["time", "t2m"],
            "dtypes": {"time": "string", "t2m": "float64"},
            "version": "1.0",
        }
    })

    # Column validation
    assert schema.validate_columns(["time", "t2m"])
    assert not schema.validate_columns(["t2m", "time"])  # wrong order

    # Dtype validation
    df_dtypes = {"time": "string", "t2m": "float64"}
    assert schema.validate_dtypes(df_dtypes)

    df_bad = {"time": "string", "t2m": "int64"}
    assert not schema.validate_dtypes(df_bad)


def test_schema_description():
    schema = ChunkSchema({
        "schema": {
            "columns": ["time", "t2m"],
            "dtypes": {"time": "string", "t2m": "float64"},
            "version": "1.0",
        }
    })

    desc = schema.describe()
    assert "ChunkSchema" in desc
    assert "time" in desc
