import math

def bartz_equation(diameter, mach, prop_data, pc, c_star, diameter_throat, radius_curvature):
    """
    Estimates the convective heat transfer coefficient (hg) using the Bartz equation.

    Args:
        diameter (float): Local diameter (m)
        mach (float): Local Mach number
        prop_data (dict): Property data (viscosity, cp, prandtl, gamma)
        pc (float): Chamber pressure (Pa)
        c_star (float): Characteristic velocity (m/s)
        diameter_throat (float): Throat diameter (m)
        radius_curvature (float): Radius of curvature at throat (m)

    Returns:
        float: Heat transfer coefficient (W/m^2-K)
    """

    mu = prop_data.get('viscosity', 8e-5) # Average gas viscosity
    cp = prop_data.get('cp', 2500)        # Specific heat
    pr = prop_data.get('prandtl', 0.8)    # Prandtl number
    gamma = prop_data.get('gamma', 1.2)

    # Sigma correction factor for property variation across boundary layer
    # Simplified: usually between 0.8 and 1.2 depending on wall temperature
    # Using a constant for preliminary sizing
    sigma = 1.0

    # Bartz Equation:
    # hg = [0.026 / Dt^0.2] * [(mu^0.2 * Cp) / Pr^0.6] * [(Pc * g0 / c*)^0.8] * [(Dt / Rc)^0.1] * [(At / A)^0.9] * sigma
    # Note: g0 is often implicitly handled in units. If Pc/c* represents mass flux parameter.

    # Mass flux G = rho * u = P / (R*T) * M * sqrt(gamma*R*T)
    # At throat Gt ~ Pc / c*
    # Here we use the standard correlation form.

    # Term 1: Geometric scaling
    term1 = 0.026 / (diameter_throat**0.2)

    # Term 2: Gas properties
    term2 = (mu**0.2 * cp) / (pr**0.6)

    # Term 3: Chamber pressure / Mass flux dependence
    # Using Pc directly in Pa.
    term3 = (pc / c_star)**0.8

    # Term 4: Curvature enhancement
    # If radius_curvature is 0 or not provided, assume Dt/2
    if radius_curvature <= 0:
        radius_curvature = diameter_throat

    term4 = (diameter_throat / radius_curvature)**0.1

    # Term 5: Area ratio scaling (velocity effect)
    # A/At = (D/Dt)^2
    # We need (At/A)^0.9 = ((Dt/D)^2)^0.9 = (Dt/D)^1.8
    term5 = (diameter_throat / diameter)**1.8

    hg = term1 * term2 * term3 * term4 * term5 * sigma
    return hg
