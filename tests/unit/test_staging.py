def test_staging_calculation():
    from oberth.mission import Stage

    # Test case: 1000 kg wet, 100 kg dry, Isp 300s
    # DV = 300 * 9.80665 * ln(10) ~ 2941.995 * 2.302585 ~ 6773.8
    stage = Stage(isp=300, wet_mass=1000, dry_mass=100)
    dv = stage.delta_v()

    assert dv > 6700
    assert dv < 6800
