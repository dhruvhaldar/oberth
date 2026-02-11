def test_area_mach_relation():
    """Verifies the Area-Mach number relation A/A* for isentropic flow."""
    from oberth.nozzle import isentropic_area_ratio
    # For Gamma=1.4, M=2.0, A/A* should be ~1.6875 (Anderson Table A.1)
    area_ratio = isentropic_area_ratio(mach=2.0, gamma=1.4)
    assert abs(area_ratio - 1.6875) < 1e-4
