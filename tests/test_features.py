"""
Branch 1 smoke tests for the feature engineering stage.

These tests verify only that the feature engineering modules import correctly.
Branch 1 does NOT validate:
- feature definitions
- transformations
- schema correctness
- data content or shape

Branch 2 will introduce full validation tests including:
- pytest fixtures
- feature registry checks
- schema validation
- transformation correctness
- multi-variable feature tests
"""

def test_features_import():
    """
    Smoke test: ensure feature engineering modules import without crashing.

    Branch 1 keeps feature engineering intentionally minimal. These imports
    confirm:
    - modules exist
    - no syntax errors
    - no missing dependencies
    - no circular imports

    No feature functions are executed in Branch 1.
    """
    import src.features_03.build_features          # noqa: F401
    import src.features_03.feature_definitions     # noqa: F401