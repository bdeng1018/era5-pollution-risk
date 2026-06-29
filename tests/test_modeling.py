"""
Branch 1 smoke tests for the modeling stage.

These tests verify only that the modeling module imports correctly.
Branch 1 does NOT validate:
- training logic
- model artifacts
- predictions
- configuration handling
- feature loading

Branch 2 will introduce full modeling tests including:
- pytest fixtures
- model artifact existence checks
- schema validation
- deterministic training behavior
- multi-model testing
"""

def test_model_import():
    """
    Smoke test: ensure modeling modules import without crashing.

    Branch 1 keeps modeling intentionally minimal. These imports confirm:
    - modules exist
    - no syntax errors
    - no missing dependencies
    - no circular imports

    No training functions are executed in Branch 1.
    """
    import src.modeling_04.train_model    # noqa: F401