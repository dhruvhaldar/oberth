def test_full_engine_design_cycle():
    """
    Simulates a full design loop:
    1. Select Propellants -> Get Isp and Combustion properties
    2. Size Throat for Thrust (not implemented but can mock)
    3. Design Nozzle Contour
    4. Calculate Cooling Requirements
    """
    from oberth.chemistry import RocketPerformance
    from oberth.nozzle import MethodOfCharacteristics
    from oberth.cooling import bartz_equation

    # 1. Performance
    pc = 100e5
    pe = 1e5
    engine = RocketPerformance(pc=pc, pe=pe)
    engine.scan_mixture_ratio(['LOX', 'RP-1'], [2.0, 2.6])

    # Check we got results
    assert len(engine.results['isp']) > 0
    max_isp = max(engine.results['isp'])
    assert max_isp > 250

    # 2. Nozzle Design
    expansion_ratio = 25.0

    moc = MethodOfCharacteristics(gamma=1.2)
    contour = moc.solve(expansion_ratio=expansion_ratio)
    assert len(contour) > 0

    # 3. Cooling Check at Throat
    dt = 0.1
    hg = bartz_equation(
        diameter=dt,
        mach=1.0,
        prop_data={'viscosity': 8e-5, 'cp': 2500, 'prandtl': 0.8},
        pc=pc,
        c_star=1700, # Approx for RP-1
        diameter_throat=dt,
        radius_curvature=dt/2
    )

    # Heat transfer coefficient should be positive
    assert hg > 0
