from oberth.mission import Stage

def test_two_stage_to_orbit():
    """
    E2E Test: Can this 2-stage configuration reach Low Earth Orbit (LEO)?
    Target Delta-V: ~9400 m/s
    """
    stage1 = Stage(isp=300, wet_mass=100000, dry_mass=8000)
    stage2 = Stage(isp=350, wet_mass=20000, dry_mass=2000)

    total_dv = stage1.delta_v() + stage2.delta_v()
    assert total_dv > 9400
