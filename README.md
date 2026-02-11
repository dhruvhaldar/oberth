# Oberth

Oberth is a comprehensive computational propulsion library designed for MJ2246 Rocket Propulsion. It automates the complex thermochemical and gas-dynamic calculations required to design liquid rocket engines.

The project bridges the gap between textbook theory (Hill & Peterson, Sutton) and real-world preliminary design, offering a "glass-box" alternative to industry tools like NASA CEA or RPA.

## 📚 Syllabus Mapping (MJ2246)

This project strictly adheres to the course learning outcomes:

| Module | Syllabus Topic | Implemented Features |
| :--- | :--- | :--- |
| **Nozzle Flow** | Calculation of rocket nozzle flow field | Method of Characteristics (MOC) solver for supersonic bell nozzle contour generation. |
| **Performance** | Equilibrium chemistry | $I_{sp}$, $C^*$, and $C_F$ calculator for Frozen vs. Shifting Equilibrium flows. |
| **Thermodynamics** | Combustion chamber design | Adiabatic Flame Temperature calculation using enthalpy balance. |
| **Heat Transfer** | Wall cooling | Bartz Equation implementation for convective heat flux ($h_g$) estimation. |
| **Mission** | Orbital mechanics | Multistage Delta-V calculator and Hohmann Transfer budgeter. |

## 🚀 Deployment (Vercel)

Oberth is designed to run as a serverless API.

1.  Fork this repository.
2.  Deploy to Vercel (the `api/` folder is automatically detected as a Python Function).
3.  Access the Nozzle Design Tool at `https://your-oberth.vercel.app`.

## 📊 Artifacts & Engine Analysis

### 1. Nozzle Contour Design (Method of Characteristics)

Generates the optimal supersonic bell shape to minimize divergence losses.

**Code:**

```python
from oberth.nozzle import MethodOfCharacteristics

# Design a nozzle for Mach 5 exit
moc = MethodOfCharacteristics(gamma=1.2, lines=20)
contour = moc.solve(expansion_ratio=25)

moc.plot_mesh()
```

**Artifact Output:**

*Figure 1: The Characteristic Net. The plot shows the expansion waves (Mach lines) originating from the throat (x=0). The "wall" streamline defines the physical nozzle contour required to straighten the flow at the exit.*

### 2. Performance Optimization ($I_{sp}$ vs O/F Ratio)

Determines the optimal Oxidizer-to-Fuel ratio for maximum specific impulse.

**Code:**

```python
from oberth.chemistry import RocketPerformance

# Compare LOX/LH2 vs LOX/RP-1
engine = RocketPerformance(pc=100e5, pe=1e5) # 100 bar chamber
results = engine.scan_mixture_ratio(
    propellants=['LOX', 'RP-1'],
    of_range=[1.5, 4.0]
)

results.plot_isp()
```

**Artifact Output:**

*Figure 2: $I_{sp}$ Optimization. The curve peaks around O/F = 2.3 for LOX/RP-1. The rapid drop-off at high O/F ratios illustrates the effect of increased molecular weight ($M_{wg}$) counteracting high temperature.*

### 3. Regenerative Cooling Analysis

Estimates the heat flux along the nozzle wall using the Bartz correlation.

**Artifact Output:**

*Figure 3: Heat Flux Profile. The peak heat flux occurs slightly upstream of the throat ($M \approx 1$), dictating the cooling jacket requirements. The drop in flux downstream allows for simpler materials.*

## 🧪 Testing Strategy

### Unit Tests (Thermodynamics)

Located in `tests/unit/`.

Example: `tests/unit/test_isentropic.py`

```python
def test_area_mach_relation():
    """Verifies the Area-Mach number relation A/A* for isentropic flow."""
    from oberth.nozzle import isentropic_area_ratio
    # For Gamma=1.4, M=2.0, A/A* should be ~1.6875 (Anderson Table A.1)
    area_ratio = isentropic_area_ratio(mach=2.0, gamma=1.4)
    assert abs(area_ratio - 1.6875) < 1e-4
```

### E2E Tests (Mission Simulation)

Located in `tests/e2e/`.

Example: `tests/e2e/test_mission_staging.py`

```python
def test_two_stage_to_orbit():
    """
    E2E Test: Can this 2-stage configuration reach Low Earth Orbit (LEO)?
    Target Delta-V: ~9400 m/s
    """
    stage1 = Stage(isp=300, wet_mass=100000, dry_mass=8000)
    stage2 = Stage(isp=350, wet_mass=20000, dry_mass=2000)

    total_dv = stage1.delta_v() + stage2.delta_v()
    assert total_dv > 9400
```

## ⚖️ License

MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files... [Standard MIT Text]
