"""
Branch 1 smoke tests for the evaluation stage.

These tests verify only that the evaluation modules import correctly.
Branch 1 does NOT validate:
- metric correctness
- prediction correctness
- model artifact loading
- evaluation outputs

Branch 2 will introduce full evaluation tests including:
- pytest fixtures
- model artifact existence checks
- prediction shape validation
- metric correctness tests
- residual analysis tests
"""

def test_evaluation_import():
    """
    Smoke test: ensure evaluation modules import without crashing.

    Branch 1 keeps evaluation intentionally minimal. These imports confirm:
    - modules exist
    - no syntax errors
    - no missing dependencies
    - no circular imports

    No evaluation functions are executed in Branch 1.
    """
    import src.evaluation_05.evaluate_model    # noqa: F401
    import src.evaluation_05.metrics           # noqa: F401