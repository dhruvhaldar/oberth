# Database of common rocket propellants

PROPELLANTS = {
    'LOX': {
        'name': 'Liquid Oxygen',
        'formula': 'O2',
        'density': 1141, # kg/m3 at boiling point
        'boiling_point': 90.19, # K
        'molecular_weight': 31.999, # g/mol
    },
    'RP-1': {
        'name': 'Rocket Propellant 1 (Kerosene)',
        'formula': 'CH1.95', # Approximation
        'density': 810, # kg/m3
        'boiling_point': 490, # K approx
        'molecular_weight': 175, # Approx average
    },
    'LH2': {
        'name': 'Liquid Hydrogen',
        'formula': 'H2',
        'density': 70.85, # kg/m3
        'boiling_point': 20.28, # K
        'molecular_weight': 2.016, # g/mol
    },
    'LCH4': {
        'name': 'Liquid Methane',
        'formula': 'CH4',
        'density': 422.6, # kg/m3
        'boiling_point': 111.6, # K
        'molecular_weight': 16.04, # g/mol
    }
}

def get_propellant(name):
    """Retrieves propellant properties by name (case-insensitive)."""
    name = name.upper()
    if name in PROPELLANTS:
        return PROPELLANTS[name]

    # Try aliases
    if name == 'KEROSENE':
        return PROPELLANTS['RP-1']
    if name == 'HYDROGEN':
        return PROPELLANTS['LH2']
    if name == 'METHANE':
        return PROPELLANTS['LCH4']
    if name == 'OXYGEN':
        return PROPELLANTS['LOX']

    return None
