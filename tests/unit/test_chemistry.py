
import numpy as np
from oberth.chemistry import RocketPerformance

def test_rocket_performance_initialization():
    engine = RocketPerformance(pc=100e5, pe=1e5)
    assert engine.pc == 100e5
    assert engine.pe == 1e5
    assert engine.results == {}

def test_scan_mixture_ratio_results():
    engine = RocketPerformance()
    propellants = ['LOX', 'RP-1']
    of_range = [2.0, 3.0]

    engine.scan_mixture_ratio(propellants, of_range)

    results = engine.results
    assert 'of' in results
    assert 'isp' in results
    assert 'propellants' in results
    assert results['propellants'] == propellants
    assert len(results['of']) == 50
    assert len(results['isp']) == 50

    # Check that Isp values are reasonable
    # For LOX/RP-1, peak is around 2.3, max Isp ~300-320
    assert max(results['isp']) > 250
    assert max(results['isp']) <= 320

def test_scan_mixture_ratio_peak_location():
    # Test that peak Isp occurs near expected O/F for RP-1
    engine = RocketPerformance()
    engine.scan_mixture_ratio(['LOX', 'RP-1'], [1.0, 4.0])

    max_isp_idx = np.argmax(engine.results['isp'])
    peak_of = engine.results['of'][max_isp_idx]

    # RP-1 peak is around 2.3
    assert 2.0 < peak_of < 2.6

def test_scan_mixture_ratio_hydrogen():
    # Test that peak Isp occurs near expected O/F for LH2
    engine = RocketPerformance()
    engine.scan_mixture_ratio(['LOX', 'LH2'], [3.0, 7.0])

    max_isp_idx = np.argmax(engine.results['isp'])
    peak_of = engine.results['of'][max_isp_idx]

    # LH2 peak is around 5.0 (in this simplified model)
    assert 4.5 < peak_of < 5.5
    assert max(engine.results['isp']) > 400
