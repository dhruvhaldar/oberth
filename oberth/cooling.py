import math

# Performance Optimization: Calculating the combined expression of default properties
# as a module-level constant bypasses redundant calculation overhead inside the tight function
# when defaults are used.
_DEFAULT_PROP_FACTOR = 0.026 * 2500 * 1.0 * (8e-5)**0.2 * 0.8**(-0.6)

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

    # Performance Optimization: Checking if the dictionary is empty before extracting multiple optional
    # values avoids executing four separate `.get(key, default)` function calls.
    # Additionally, directly assigning a pre-calculated `_DEFAULT_PROP_FACTOR` completely avoids
    # exponentiation and multiplication overhead for the default case.
    if not prop_data:
        prop_factor = _DEFAULT_PROP_FACTOR
    else:
        mu = prop_data.get('viscosity', 8e-5)
        cp = prop_data.get('cp', 2500)
        pr = prop_data.get('prandtl', 0.8)
        # gamma is removed as it was unused in the equation below
        sigma = 1.0
        prop_factor = 0.026 * cp * sigma * mu**0.2 * pr**(-0.6)

    # Bartz Equation:
    # hg = [0.026 / Dt^0.2] * [(mu^0.2 * Cp) / Pr^0.6] * [(Pc * g0 / c*)^0.8] * [(Dt / Rc)^0.1] * [(At / A)^0.9] * sigma
    # Note: g0 is often implicitly handled in units. If Pc/c* represents mass flux parameter.

    # Mass flux G = rho * u = P / (R*T) * M * sqrt(gamma*R*T)
    # At throat Gt ~ Pc / c*
    # Here we use the standard correlation form.

    # If radius_curvature is 0 or not provided, assume Dt/2
    if radius_curvature <= 0:
        radius_curvature = diameter_throat

    # Performance Optimization: Algebraically refactored the expression to precompute and combine
    # exponents of the throat diameter (Dt). Instead of executing three separate exponentiations
    # containing division (e.g. (mu/Dt)**0.2 * (Dt/Rc)**0.1 * (Dt/D)**1.8), combining the terms yields
    # Dt**1.7. This eliminates two division operations and reduces exponentiation overhead.
    # We further group the `prop_factor` to reduce runtime multiplications.
    return (
        prop_factor
        * diameter_throat**1.7              # Combined throat diameter scaling
        * radius_curvature**(-0.1)          # Curvature enhancement
        * diameter**(-1.8)                  # Local area ratio scaling (velocity effect)
        * (pc / c_star)**0.8                # Chamber pressure / Mass flux dependence
    )
