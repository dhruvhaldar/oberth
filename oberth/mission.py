import math

class Stage:
    """
    Represents a rocket stage for mission delta-v calculations.
    """
    def __init__(self, isp, wet_mass, dry_mass):
        """
        isp: Specific Impulse (s)
        wet_mass: Initial mass (kg)
        dry_mass: Final mass (kg)
        """
        self.isp = isp
        self.wet_mass = wet_mass
        self.dry_mass = dry_mass
        self.g0 = 9.80665 # Standard gravity

    def delta_v(self):
        """
        Calculates the delta-v using the Tsiolkovsky rocket equation.
        """
        if self.dry_mass <= 0 or self.wet_mass <= 0:
            return 0.0
        return self.isp * self.g0 * math.log(self.wet_mass / self.dry_mass)

def hohmann_transfer_dv(r1, r2, mu=3.986e14):
    """
    Calculates the delta-v required for a Hohmann transfer between two circular orbits.

    Args:
        r1 (float): Radius of initial orbit (m)
        r2 (float): Radius of final orbit (m)
        mu (float): Standard gravitational parameter (m^3/s^2). Default is Earth.

    Returns:
        float: Total delta-v (m/s)
    """
    # Semi-major axis of transfer orbit
    a_transfer = (r1 + r2) / 2

    # Velocity at periapsis of transfer orbit (at r1)
    v_transfer_p = math.sqrt(mu * (2/r1 - 1/a_transfer))

    # Velocity at apoapsis of transfer orbit (at r2)
    v_transfer_a = math.sqrt(mu * (2/r2 - 1/a_transfer))

    # Circular velocity at r1
    v1 = math.sqrt(mu / r1)

    # Circular velocity at r2
    v2 = math.sqrt(mu / r2)

    # Delta V 1 (departure burn)
    dv1 = abs(v_transfer_p - v1)

    # Delta V 2 (arrival burn)
    dv2 = abs(v2 - v_transfer_a)

    return dv1 + dv2
