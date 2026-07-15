"""
Stage 4 Smoke Test
Purpose:
    Verify that all spatiotemporal_04 modules import cleanly.
    This test does NOT execute any logic or load data.
    It ensures the Stage 4 subsystem is structurally intact.

Test Type:
    Smoke Test — import-only, zero side effects.
"""

def test_stage4_imports():
    # Core invariants
    # Orchestration layer
    import src.spatiotemporal_04.driver as driver
    import src.spatiotemporal_04.grid as grid
    import src.spatiotemporal_04.mask as mask
    import src.spatiotemporal_04.metadata as metadata
    import src.spatiotemporal_04.qc as qc
    import src.spatiotemporal_04.temporal_align as temporal_align
    import src.spatiotemporal_04.temporal_interpolate as temporal_interpolate

    # Tensor + metadata invariants
    import src.spatiotemporal_04.tensor_builder as tensor_builder

    # If all imports succeed, the smoke test passes
    assert True
