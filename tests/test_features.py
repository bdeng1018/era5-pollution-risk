"""
Branch 1 Smoke Tests — Feature Engineering Stage
================================================

Purpose
-------
These tests confirm that feature engineering modules import correctly. Branch 1
does NOT execute any feature-building logic. This ensures:

- modules exist and load without errors
- no missing dependencies
- no circular imports
- feature registry imports cleanly

What Branch 1 Does NOT Test
---------------------------
Branch 1 intentionally avoids:

- feature definitions correctness
- transformation logic
- schema correctness
- multi-variable feature generation
- deterministic feature shapes

Why?
----
Feature engineering requires real Parquet inputs and deterministic fixtures.
These belong in Branch 2.

Branch 2 Roadmap
----------------
Branch 2 will introduce:

- feature registry validation
- schema validation
- transformation correctness tests
- multi-variable feature tests
- deterministic feature shape tests
"""

# ----------------------------------------------------------------------
# Branch 1 Constraints
# ----------------------------------------------------------------------
# These tests intentionally avoid executing any feature-engineering logic.
# They validate only that modules import cleanly, ensuring:
# - no missing dependencies
# - no circular imports
# - no runtime errors during import
# ----------------------------------------------------------------------


def test_features_import():
    """
    Smoke test: ensure feature engineering modules import without crashing.

    Branch 1 keeps feature engineering intentionally minimal. These imports
    confirm:
    - modules exist
    - no syntax errors
    - no missing dependencies
    - no circular imports

    No feature functions are executed in Branch 1 because real feature
    engineering requires Parquet fixtures, schema validation, and deterministic
    test data — all of which belong in Branch 2.
    """
    # Import-only tests ensure that module-level code (logging setup,
    # feature registry loading, dependency imports) is stable and error-free.
    import src.features_03.build_features  # noqa: F401
    import src.features_03.feature_definitions  # noqa: F401


# ----------------------------------------------------------------------
# Branch 2 Roadmap
# ----------------------------------------------------------------------
# Future tests will add:
# - feature registry validation
# - schema validation for feature outputs
# - transformation correctness tests
# - multi-variable feature generation tests
# - deterministic feature shape tests
# ----------------------------------------------------------------------
