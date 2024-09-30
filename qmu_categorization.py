from qmu_units import all_units, QMUUnit

# Define categories
categories = {
    'base_units': 'Base Units of Dimension',
    'em_field': 'Electromagnetic Field and Interaction',
    'magnetic_resistance': 'Magnetic Field Resistance and Flow',
    'quantum_electrodynamics': 'Quantum Electrodynamic Foundational',
    'quantum_distribution': 'Quantum Electromagnetic Distribution',
    'em_behavior': 'Electromagnetic Behavioral',
    'fundamental_inertial': 'Fundamental Inertial and Behavioral',
    'density_distribution': 'Density and Distributional Behavior',
    'coupling_interaction': 'Coupling and Interactional Behavior',
    'oscillation_spatial': 'Oscillation and Spatial Dynamics',
    'spatial_temporal': 'Spatial-Temporal Dynamics',
    'other': 'Other Units'
}

# Create a dictionary to store units by category
categorized_units = {category: [] for category in categories.keys()}

# Function to categorize units
def categorize_units():
    categorized_units.clear()  # Clear existing categorizations
    for category in categories.keys():
        categorized_units[category] = []  # Reset each category to an empty list
    
    for unit_code, unit in all_units.items():
        if unit_code in ['me', 'λC', 'Fq', 'eemax']:
            categorized_units['base_units'].append(unit)
        elif unit_code in ['rmfd', 'mfld', 'mvlm', 'potn', 'mflx', 'indc', 'elfs', 'magr', 'perm', 'dvef', 'mfxd', 'mchg', 'mfde', 'mfir', 'ptty', 'aefp', 'cond', 'capc', 'curl', 'exdf', 'accp', 'expr', 'cdns', 'cvef']:
            categorized_units['em_field'].append(unit)
        elif unit_code in ['fric', 'mgfi', 'ffeq', 'kfcn', 'resn', 'magp', 'mfdw', 'mdif', 'thmf', 'arsf', 'pccf', 'mopp', 'emro', 'emic', 'cfff', 'masc', 'admt', 'mrlc', 'mcri', 'mfdr', 'mfen', 'mcup', 'msir']:
            categorized_units['magnetic_resistance'].append(unit)
        elif unit_code in ['qpmd', 'mcpp', 'mcdr', 'mcrd', 'qild', 'qecf', 'cscc', 'chcc', 'qecj', 'qeca', 'qecd', 'ecdp', 'qeci', 'qeco', 'ecfx', 'mcaf', 'efvr', 'efva', 'efvc', 'chvm', 'ball', 'plsm', 'magm', 'sfch', 'efdr', 'chac', 'chvl', 'chgl', 'efti', 'chrs', 'curr', 'chrg']:
            categorized_units['quantum_electrodynamics'].append(unit)
        elif unit_code in ['qvci', 'qvcr', 'qvcp', 'spch', 'qcdr', 'qcdp', 'qcdd', 'chds', 'qcrr', 'qcrp', 'qcrd', 'chgr', 'qcdi', 'cdrs', 'cdos', 'chgd', 'qefi', 'qefr', 'cdns', 'efxd', 'qegi', 'qegr', 'mfdi', 'elcg']:
            categorized_units['quantum_distribution'].append(unit)
        elif unit_code in ['trmo', 'vefd', 'efld', 'spch', 'defi', 'chgt', 'chgs', 'chds', 'deff', 'chga', 'chgv', 'chgr', 'defo', 'crsn', 'mcur', 'mcaf', 'qefs', 'qefr', 'qefc', 'chgd', 'qefi', 'efrs', 'mcdf', 'efxd', 'qefp', 'qefe', 'efcd', 'elcg', 'efsu', 'efpt', 'chrg']:
            categorized_units['em_behavior'].append(unit)
        elif unit_code in ['ligt', 'phtn', 'qanr', 'vrtx', 'powr', 'enrg', 'angm', 'minr', 'lint', 'forc', 'momt', 'torq', 'irrd', 'sten', 'ints', 'mass', 'ocmp', 'inpr', 'qvrc', 'qvoi', 'qsrc', 'qusi', 'qarg', 'qari', 'qili', 'sptn', 'qmob', 'qflx', 'qopq', 'qspr', 'dfld', 'qexl']:
            categorized_units['fundamental_inertial'].append(unit)
        elif unit_code in ['qmfa', 'qmro', 'qmfo', 'masd', 'qsac', 'fdns', 'momd', 'sfcd', 'pdrt', 'pres', 'visc', 'ldns', 'qvfi', 'qvtc', 'qvdf', 'spcv', 'qsfr', 'qarc', 'qsdc', 'spar', 'qlod', 'qldc', 'qltc', 'spln']:
            categorized_units['density_distribution'].append(unit)
        elif unit_code in ['qdir', 'mrcr', 'mfdr', 'scir', 'scoc', 'sctf', 'ldqr', 'ldoc', 'ldtf', 'qmir', 'qmop', 'qmtc', 'qvod', 'qagm', 'qavm', 'qasm', 'qatm', 'qaam', 'qadi', 'qadm', 'qamo']:
            categorized_units['coupling_interaction'].append(unit)
        elif unit_code in ['qvos', 'dtrd', 'flow', 'volm', 'qsfo', 'temp', 'swep', 'area', 'qdyf', 'accl', 'velc', 'qinf', 'rson', 'qvor', 'invr', 'vfdn', 'fint', 'qsfi', 'qsin', 'sfrs', 'bndr', 'qdfr', 'morc', 'quid', 'wavn', 'qire', 'orbt', 'time']:
            categorized_units['oscillation_spatial'].append(unit)
        elif unit_code in ['ovev', 'voco', 'vlmt', 'tafx', 'atfx', 'acta', 'hepl', 'qtrl', 'dynl', 'voqo', 'vlmr', 'vlmw', 'tqod', 'tvsr', 'tvsw', 'sqod', 'sclr', 'sclw']:
            categorized_units['spatial_temporal'].append(unit)
        else:
            categorized_units['other'].append(unit)

# Function to display units by category
def display_categorized_units():
    for category, units in categorized_units.items():
        if units:  # Only display categories that have units
            print(f"\n{categories[category]}:")
            for unit in units:
                print(f"  {unit.symbol}: {unit.name}")

# Function to get units by category
def get_units_by_category(category):
    return categorized_units.get(category, [])

# Function to search for a unit by name or symbol
def search_unit(query):
    query = query.lower()
    results = []
    for unit in all_units.values():
        if query in unit.name.lower() or query in unit.symbol.lower():
            results.append(unit)
    return results

# Initialize categorization
categorize_units()
