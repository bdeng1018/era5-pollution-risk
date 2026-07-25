"""
Branch 1 Smoke Tests — Evaluation Stage
=======================================

Purpose
-------
These tests verify that evaluation modules import correctly. Branch 1 does NOT
execute evaluation logic. This ensures:

- modules exist and import without errors
- no missing dependencies
- no circular imports
- metric utilities load correctly

What Branch 1 Does NOT Test
---------------------------
Branch 1 intentionally avoids:

- metric correctness
- prediction correctness
- model artifact loading
- residual analysis
- evaluation output correctness

Why?
----
Evaluation depends on trained model artifacts, deterministic predictions, and
metric validation — all of which belong in Branch 2.

Branch 2 Roadmap
----------------
Branch 2 will introduce:

- metric correctness tests
- prediction shape validation
- residual analysis tests
- artifact existence checks
- multi-variable evaluation tests
"""

# ----------------------------------------------------------------------
# Branch 1 Constraints
# ----------------------------------------------------------------------
# These tests intentionally avoid executing any evaluation logic.
# They validate only that evaluation modules import cleanly, ensuring:
# - no missing dependencies
# - no circular imports
# - no runtime errors during import
# ----------------------------------------------------------------------


def test_evaluation_import():
    """
    Smoke test: ensure evaluation modules import without crashing.

    Branch 1 keeps evaluation intentionally minimal. These imports confirm:
    - modules exist
    - no syntax errors
    - no missing dependencies
    - no circular imports

    No evaluation functions are executed in Branch 1 because real evaluation
    requires trained model artifacts, deterministic predictions, and metric
    validation — all of which belong in Branch 2.
    """
    # Import-only tests ensure that module-level code (logging setup,
    # metric registry loading, dependency imports) is stable and error-free.
    import src.evaluation_05.evaluate_model  # noqa: F401
    import src.evaluation_05.metrics  # noqa: F401


# ----------------------------------------------------------------------
# Branch 2 Roadmap
# ----------------------------------------------------------------------
# Future tests will add:
# - metric correctness tests
# - prediction shape validation
# - residual analysis tests
# - artifact existence checks
# - multi-variable evaluation tests
# ----------------------------------------------------------------------
