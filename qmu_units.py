# from sage.all import *

# qmu_units.py

import re
from collections import defaultdict

class QMUUnit:
    def __init__(self, name, symbol, expression=None, si_equivalent=None, shorthand=None):
        self.name = name
        self.symbol = symbol
        self.expression = expression
        self.si_equivalent = si_equivalent
        self.shorthand = shorthand
        self.base_units = self.parse_expression() if expression else {symbol: 1}

    def parse_expression(self):
        if not self.expression:
            return {self.symbol: 1}
        
        base_units = {}
        unit_pattern = r'(me|λC|Fq|eemax)'
        power_pattern = r'\^(-?\d+)'
        parts = re.split(r'\s*([*/])\s*', self.expression)
        
        current_op = '*'
        for part in parts:
            if part in ['*', '/']:
                current_op = part
                continue
            
            part = part.strip('()')
            units = re.findall(f'{unit_pattern}(?:{power_pattern})?', part)
            
            for unit, power in units:
                power = int(power) if power else 1
                if current_op == '*':
                    base_units[unit] = base_units.get(unit, 0) + power
                else:  # division
                    base_units[unit] = base_units.get(unit, 0) - power
        
        base_units = {k: v for k, v in base_units.items() if v != 0}
        print(f"Parsed expression for {self.symbol}: {base_units}")  # Debug output
        return base_units

    def to_base_units(self):
        return self.base_units

    def __eq__(self, other):
        return self.to_base_units() == other.to_base_units()

    def __str__(self):
        if self.expression:
            base_units = self.to_base_units()
            unit_str = "*".join(sym if pow == 1 else f"{sym}^{pow}" for sym, pow in sorted(base_units.items()) if pow != 0)
            return f"{self.name} ({self.symbol}): {unit_str}"
        return f"{self.name} ({self.symbol})"

def simplify_and_match_unit(unit):
    if isinstance(unit, QMUQuantity):
        base_units = unit.unit.to_base_units()
    elif isinstance(unit, QMUUnit):
        base_units = unit.to_base_units()
    else:
        raise TypeError(f"Expected QMUQuantity or QMUUnit, got {type(unit)}")

    simplified_expression = "*".join(sorted([f"{sym}^{pow}" if pow != 1 else sym for sym, pow in base_units.items() if pow != 0]))
    simplified_expression = re.sub(r'\^1(?!\d)', '', simplified_expression)
    print(f"Debug: Simplified expression: {simplified_expression}")
    
    matched_unit = derived_units_map.get(simplified_expression)
    if matched_unit:
        print(f"Debug: Matched unit: {matched_unit.symbol}")
        return matched_unit
    else:
        print(f"Debug: No match found, creating custom unit")
        return QMUUnit("Custom Unit", simplified_expression, simplified_expression)

class QMUQuantity:
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __str__(self):
        return f"{self.value} {self.unit.symbol}"

    def __repr__(self):
        return self.__str__()

    def __mul__(self, other):
        if isinstance(other, QMUQuantity):
            new_value = self.value * other.value
            new_base_units = {k: self.unit.to_base_units().get(k, 0) + other.unit.to_base_units().get(k, 0) 
                              for k in set(self.unit.to_base_units()) | set(other.unit.to_base_units())}
            new_unit = QMUUnit("Composite", "*".join([f"{sym}^{pow}" for sym, pow in new_base_units.items() if pow != 0]))
            return QMUQuantity(new_value, new_unit)
        elif isinstance(other, (int, float)):
            return QMUQuantity(self.value * other, self.unit)
        else:
            raise TypeError(f"Multiplication not supported between QMUQuantity and {type(other)}")

    def __truediv__(self, other):
        if isinstance(other, QMUQuantity):
            new_value = self.value / other.value
            new_base_units = {k: self.unit.to_base_units().get(k, 0) - other.unit.to_base_units().get(k, 0) 
                              for k in set(self.unit.to_base_units()) | set(other.unit.to_base_units())}
            new_unit = QMUUnit("Composite", "*".join([f"{sym}^{pow}" for sym, pow in new_base_units.items() if pow != 0]))
            result = QMUQuantity(new_value, new_unit)
            return simplify_and_match_unit(result)
        elif isinstance(other, (int, float)):
            return QMUQuantity(self.value / other, self.unit)
        else:
            raise TypeError(f"Division not supported between QMUQuantity and {type(other)}")

    def __add__(self, other):
        if not isinstance(other, QMUQuantity):
            raise TypeError(f"Addition not supported between QMUQuantity and {type(other)}")
        if self.unit != other.unit:
            raise ValueError(f"Cannot add quantities with different units: {self.unit.symbol} and {other.unit.symbol}")
        return QMUQuantity(self.value + other.value, self.unit)

    def __sub__(self, other):
        if not isinstance(other, QMUQuantity):
            raise TypeError(f"Subtraction not supported between QMUQuantity and {type(other)}")
        if self.unit != other.unit:
            raise ValueError(f"Cannot subtract quantities with different units: {self.unit.symbol} and {other.unit.symbol}")
        return QMUQuantity(self.value - other.value, self.unit)
        print(f"Multiplying {self.value} {self.unit.symbol} by {other.value} {other.unit.symbol}")
        print(f"New value: {new_value}")
        print(f"New base units: {new_base_units}")
        print(f"New unit expression: {new_unit.expression}")

# Base units
mass = QMUUnit("Electron mass", "me")
leng = QMUUnit("Compton wavelength", "λC")
freq = QMUUnit("Quantum frequency", "Fq")
chrg = QMUUnit("Electron magnetic charge", "eemax")

# Electromagnetic Field and Interaction Units
rmfd = QMUUnit("Rotating Magnetic Field", "rmfd", "me * λC^3 * Fq^2 / eemax^2", shorthand="Au")
mfld = QMUUnit("Magnetic Field", "mfld", "me * λC^3 * Fq / eemax^2")
mvlm = QMUUnit("Magnetic Volume", "mvlm", "me * λC^3 / eemax^2")
potn = QMUUnit("Potential", "potn", "me * λC^2 * Fq^2 / eemax^2")
mflx = QMUUnit("Magnetic Flux", "mflx", "me * λC^2 * Fq / eemax^2")
indc = QMUUnit("Inductance", "indc", "me * λC^2 / eemax^2", "3.8314755224e-17 henry")
elfs = QMUUnit("Electric Field Strength", "elfs", "me * λC * Fq^2 / eemax^2")
magr = QMUUnit("Magnetic Rigidity", "magr", "me * λC * Fq / eemax^2")
perm = QMUUnit("Permeability", "perm", "me * λC / eemax^2", "4π * mu_0")
dvef = QMUUnit("Diverging Electric Field", "dvef", "me * Fq^2 / eemax^2")
mfxd = QMUUnit("Magnetic Flux Density", "mfxd", "me * Fq / eemax^2")
mchg = QMUUnit("Magnetism", "mchg", "me / eemax^2")
mfde = QMUUnit("Magnetic Field Exposure", "mfde", "eemax^2 / (me * λC^3)")
mfir = QMUUnit("Magnetic Flux Intensity Ratio", "mfir", "eemax^2 / (me * λC^3 * Fq)")
ptty = QMUUnit("Permittivity", "ptty", "eemax^2 / (me * λC^3 * Fq^2)", "epsilon_0 / 4π")
aefp = QMUUnit("Aether Fluctuation Potential", "aefp", "eemax^2 / (me * λC^2)")
cond = QMUUnit("Conductance", "cond", "eemax^2 / (me * λC^2 * Fq)", "2.112319309e-4 siemens")
capc = QMUUnit("Capacitance", "capc", "eemax^2 / (me * λC^2 * Fq^2)", "1.7095633318 farad")
curl = QMUUnit("Curl", "curl", "eemax^2 / (me * λC)")
exdf = QMUUnit("Exposure Diffusion Flux", "exdf", "eemax^2 / (me * λC * Fq)")
accp = QMUUnit("Acceptance", "accp", "eemax^2 / (me * λC * Fq^2)")
expr = QMUUnit("Exposure", "expr", "eemax^2 / me")
cdns = QMUUnit("Conductance Density", "cdns", "eemax^2 / (λC^2 * Fq)")
cvef = QMUUnit("Converging Electric Field", "cvef", "eemax^2 / (me * Fq^2)")

# Magnetic Field Resistance and Flow Units
fric = QMUUnit("Friction", "fric", "me * λC^3 * Fq^2 / eemax^4")
mgfi = QMUUnit("Magnetic Flow Impedance", "mgfi", "me * λC^3 * Fq / eemax^4")
ffeq = QMUUnit("Flux Flow Equilibrium", "ffeq", "me * λC^3 / eemax^4")
kfcn = QMUUnit("Kinetic Friction", "kfcn", "me * λC^2 * Fq^2 / eemax^4")
resn = QMUUnit("Resistance", "resn", "me * λC^2 * Fq / eemax^4")
magp = QMUUnit("Magnetic Permeance", "magp", "me * λC^2 / eemax^4")
mfdw = QMUUnit("Magnetic Flux Density Wave", "mfdw", "me * λC * Fq^2 / eemax^4")
mdif = QMUUnit("Magnetic Diffusion Impedance", "mdif", "me * λC * Fq / eemax^4")
thmf = QMUUnit("Thermal Magnetic Friction", "thmf", "me * λC / eemax^4")
arsf = QMUUnit("Aether Resistance Stability Factor", "arsf", "me * Fq^2 / eemax^4")
pccf = QMUUnit("Potential Charge Concentration Factor", "pccf", "me * Fq / eemax^4")
mopp = QMUUnit("Magnetic Opposition", "mopp", "eemax^4 / (me * λC)")
emro = QMUUnit("Electromagnetic Ratio", "emro", "eemax^4 / (me * λC * Fq)")
emic = QMUUnit("Electromagnetic Interaction Coefficient", "emic", "eemax^4 / (me * λC * Fq^2)")
cfff = QMUUnit("Current Flow Facilitation Factor", "cfff", "eemax^4 / (me * λC * Fq^3)")
masc = QMUUnit("Magnetic Spatial Compliance", "masc", "eemax^4 / (me * Fq^2)")
admt = QMUUnit("Admittance", "admt", "chrg / mflx")
mrlc = QMUUnit("Magnetic Reluctance", "mrlc", "curr / mflx")
mcri = QMUUnit("Magnetic Current Impedance", "mcri", "curr / mflx")
mfdr = QMUUnit("Magnetic Field Resistance", "mfdr", "1 / (chgr * mfxd)")
mfen = QMUUnit("Magnetic Field Energy", "mfen", "mfdi * cden")
mcup = QMUUnit("Magnetic Charge per Unit Potential", "mcup", "sfch / potn")
msir = QMUUnit("Magneto-Spatial Impedance Ratio", "msir", "area / resn")

# Quantum Electrodynamic Foundational Units
qpmd = QMUUnit("Quantum Photomagnetic Density", "qpmd", "me * Fq^3 / (λC^3 * eemax^2)")
mcpp = QMUUnit("Magnetic Charge per Photon", "mcpp", "me * Fq^2 / (λC^3 * eemax^2)")
mcdr = QMUUnit("Magnetic Charge Distribution per Rotation", "mcdr", "me * Fq / (λC^3 * eemax^2)")
mcrd = QMUUnit("Magnetic Charge Rotational Density", "mcrd", "me / (λC^3 * eemax^2)")
qild = QMUUnit("Quantum Illumination Density", "qild", "1 / (eemax^2 * λC^3 * Fq^3)")
qecf = QMUUnit("Quantum Electric Charge Flux", "qecf", "1 / (eemax^2 * λC^2 * Fq^2)")
cscc = QMUUnit("Charge Surface - Temporal Confinement Coefficient", "cscc", "1 / (eemax^2 * λC^2 * Fq)")
chcc = QMUUnit("Charge Surface Confinement Coefficient", "chcc", "1 / (eemax^2 * λC^2)")
qecj = QMUUnit("Quantum Electric Charge Jerk", "qecj", "1 / (eemax^2 * λC * Fq^3)")
qeca = QMUUnit("Quantum Electric Charge Acceleration", "qeca", "1 / (eemax^2 * λC * Fq^2)")
qecd = QMUUnit("Quantum Electric Charge Drift", "qecd", "1 / (eemax^2 * λC * Fq)")
ecdp = QMUUnit("Quantum Electric Charge Displacement", "ecdp", "1 / (eemax^2 * λC)")
qeci = QMUUnit("Quantum Electric Charge Intensity", "qeci", "1 / (eemax^2 * Fq^3)")
qeco = QMUUnit("Quantum Electric Charge Oscillation", "qeco", "1 / (eemax^2 * Fq^2)")
ecfx = QMUUnit("Quantum Electric Charge Fluctuation", "ecfx", "1 / (eemax^2 * Fq)")
mcaf = QMUUnit("Magnetic Charge Affinity", "mcaf", "1 / eemax^2")
efvr = QMUUnit("Quantum Electric Field Volumetric Resonance", "efvr", "eemax^2 * λC^3 * Fq^3")
efva = QMUUnit("Quantum Electric Field Volumetric Adaptability", "efva", "eemax^2 * λC^3 * Fq^2")
efvc = QMUUnit("Quantum Electric Field Volumetric Compliance", "efvc", "eemax^2 * λC^3 * Fq")
chvm = QMUUnit("Charge Volume", "chvm", "eemax^2 * λC^3")
ball = QMUUnit("Ball Lightning", "ball", "eemax^2 * λC^2 * Fq^3")
plsm = QMUUnit("Plasma", "plsm", "eemax^2 * λC^2 * Fq^2")
magm = QMUUnit("Magnetic Moment", "magm", "eemax^2 * λC^2 * Fq")
sfch = QMUUnit("Surface Charge", "sfch", "eemax^2 * λC^2")
efdr = QMUUnit("Quantum Electric Field Dynamic Responsivity", "efdr", "eemax^2 * λC * Fq^3")
chac = QMUUnit("Charge Acceleration", "chac", "eemax^2 * λC * Fq^2")
chvl = QMUUnit("Charge Velocity", "chvl", "eemax^2 * λC * Fq")
chgl = QMUUnit("Charge Length", "chgl", "eemax^2 * λC")
efti = QMUUnit("Quantum Electric Field Temporal Intensity", "efti", "eemax^2 * Fq^3")
chrs = QMUUnit("Charge Resonance", "chrs", "eemax^2 * Fq^2")
curr = QMUUnit("Current", "curr", "eemax^2 * Fq")

# Quantum Electromagnetic Distribution Units
qvci = QMUUnit("Quantum Volumetric Charge Inertia", "qvci", "λC^3 / (eemax^2 * Fq^3)")
qvcr = QMUUnit("Quantum Volumetric Charge Reluctance", "qvcr", "λC^3 / (eemax^2 * Fq^2)")
qvcp = QMUUnit("Quantum Volumetric Charge Persistence", "qvcp", "λC^3 / (eemax^2 * Fq)")
spch = QMUUnit("Specific Charge", "spch", "λC^3 / eemax^2")
qcdr = QMUUnit("Quantum Charge Distribution Resistance", "qcdr", "λC^2 / (eemax^2 * Fq^3)")
qcdp = QMUUnit("Quantum Charge Distribution Periodicity", "qcdp", "λC^2 / (eemax^2 * Fq^2)")
qcdd = QMUUnit("Quantum Charge Distribution Dynamics", "qcdd", "λC^2 / (eemax^2 * Fq)")
chds = QMUUnit("Charge Distribution", "chds", "λC^2 / eemax^2", shorthand="strk")
qcrr = QMUUnit("Quantum Charge Radius Resistance", "qcrr", "λC / (eemax^2 * Fq^3)")
qcrp = QMUUnit("Quantum Charge Radius Periodicity", "qcrp", "λC / (eemax^2 * Fq^2)")
qcrd = QMUUnit("Quantum Charge Radius Dynamics", "qcrd", "λC / (eemax^2 * Fq)")
chgr = QMUUnit("Charge Radius", "chgr", "λC / eemax^2")
qcdi = QMUUnit("Quantum Charge Density Intensity", "qcdi", "eemax^2 * Fq^3 / λC^3")
cdrs = QMUUnit("Quantum Charge Density Resonance", "cdrs", "eemax^2 * Fq^2 / λC^3")
cdos = QMUUnit("Quantum Charge Density Oscillation", "cdos", "eemax^2 * Fq / λC^3")
chgd = QMUUnit("Charge Density", "chgd", "eemax^2 / λC^3")
qefi = QMUUnit("Quantum Electric Field Intensity", "qefi", "eemax^2 * Fq^3 / λC^2")
qefr = QMUUnit("Quantum Electric Field Resonance", "qefr", "eemax^2 * Fq^2 / λC^2")
cdns = QMUUnit("Current Density", "cdns", "eemax^2 * Fq / λC^2")
efxd = QMUUnit("Electric Flux Density", "efxd", "eemax^2 / λC^2")
qegi = QMUUnit("Quantum Electric Gradient Intensity", "qegi", "eemax^2 * Fq^3 / λC")
qegr = QMUUnit("Quantum Electric Gradient Resonance", "qegr", "eemax^2 * Fq^2 / λC")
mfdi = QMUUnit("Magnetic Field Intensity", "mfdi", "eemax^2 * Fq / λC")
elcg = QMUUnit("Electric Charge Gradient", "elcg", "eemax^2 / λC")

# Electromagnetic Behavioral Units
trmo = QMUUnit("Trivariate Magnetic Oscillation", "trmo", "λC^3 * Fq^3 / eemax^2")
vefd = QMUUnit("Varying Electric Field", "vefd", "λC^3 * Fq^2 / eemax^2")
efld = QMUUnit("Electric Field", "efld", "λC^3 * Fq / eemax^2")
spch = QMUUnit("Specific Charge", "spch", "λC^3 / eemax^2")
defi = QMUUnit("Dynamic Electric Field Intensity", "defi", "λC^2 * Fq^3 / eemax^2")
chgt = QMUUnit("Charge Temperature", "chgt", "λC^2 * Fq^2 / eemax^2")
chgs = QMUUnit("Charge Sweep", "chgs", "λC^2 * Fq / eemax^2")
chds = QMUUnit("Charge Distribution", "chds", "λC^2 / eemax^2")
deff = QMUUnit("Dynamic Electric Field Flux", "deff", "λC * Fq^3 / eemax^2")
chga = QMUUnit("Charge Acceleration", "chga", "λC * Fq^2 / eemax^2")
chgv = QMUUnit("Charge Velocity", "chgv", "λC * Fq / eemax^2")
chgr = QMUUnit("Charge Radius", "chgr", "λC / eemax^2")
defo = QMUUnit("Dynamic Electric Field Oscillation", "defo", "Fq^3 / eemax^2")
crsn = QMUUnit("Charge Resonance", "crsn", "Fq^2 / eemax^2")
mcur = QMUUnit("Magnetic Current", "mcur", "Fq / eemax^2", shorthand="chgf")
mcaf = QMUUnit("Magnetic Charge Affinity", "mcaf", "1 / eemax^2")
qefs = QMUUnit("Quantum Electric Field Susceptibility", "qefs", "eemax^2 / (λC^3 * Fq^3)")
qefr = QMUUnit("Quantum Electric Field Receptivity", "qefr", "eemax^2 / (λC^3 * Fq^2)")
qefc = QMUUnit("Quantum Electric Field Compliance", "qefc", "eemax^2 / (λC^3 * Fq)")
chgd = QMUUnit("Charge Density", "chgd", "eemax^2 / λC^3")
qefi = QMUUnit("Quantum Electric Field Intensity", "qefi", "eemax^2 / (λC^2 * Fq^3)")
efrs = QMUUnit("Quantum Electric Field Resonance", "efrs", "eemax^2 / (λC^2 * Fq^2)")
mcdf = QMUUnit("Magnetic Charge Density Frequency", "mcdf", "eemax^2 / (λC^2 * Fq)")
efxd = QMUUnit("Electric Flux Density", "efxd", "eemax^2 / λC^2")
qefp = QMUUnit("Quantum Electric Field Permeability", "qefp", "eemax^2 / Fq^3")
qefe = QMUUnit("Quantum Electric Field Elasticity", "qefe", "eemax^2 / (λC * Fq^2)")
efcd = QMUUnit("Quantum Electric Field Conductance", "efcd", "eemax^2 / (λC * Fq)")
elcg = QMUUnit("Electric Charge Gradient", "elcg", "eemax^2 / λC")
efsu = QMUUnit("Quantum Electric Field Susceptibility", "efsu", "eemax^2 / Fq^2")
efpt = QMUUnit("Quantum Electric Field Permittivity", "efpt", "eemax^2 / Fq")
chrg = QMUUnit("Charge", "chrg", "eemax^2")

# Fundamental Inertial and Behavioral Units
ligt = QMUUnit("Light", "ligt", "me * λC^3 * Fq^3")
phtn = QMUUnit("Photon", "phtn", "me * λC^3 * Fq^2")
qanr = QMUUnit("Quantum Angular Reach", "qanr", "me * λC^3 * Fq")
vrtx = QMUUnit("Vortex", "vrtx", "me * λC^3")
powr = QMUUnit("Power", "powr", "me * λC^2 * Fq^3")
enrg = QMUUnit("Energy", "enrg", "me * λC^2 * Fq^2")
angm = QMUUnit("Angular Momentum", "angm", "me * λC^2 * Fq", shorthand="h")
minr = QMUUnit("Moment of Inertia", "minr", "me * λC^2")
lint = QMUUnit("Light Intensity", "lint", "me * λC * Fq^3")
forc = QMUUnit("Force", "forc", "me * λC * Fq^2")
momt = QMUUnit("Momentum", "momt", "me * λC * Fq")
torq = QMUUnit("Torque", "torq", "me * λC")
irrd = QMUUnit("Irradiance", "irrd", "me * Fq^3")
sten = QMUUnit("Surface Tension", "sten", "me * Fq^2")
ints = QMUUnit("Intensity", "ints", "me * Fq")
mass = QMUUnit("Mass", "mass", "me")
ocmp = QMUUnit("Optical Compliance", "ocmp", "1 / (me * λC^3 * Fq^3)")
inpr = QMUUnit("Innate Particulate Resolvability", "inpr", "1 / (me * λC^3 * Fq^2)")
qvrc = QMUUnit("Quantum Volumetric Receptivity", "qvrc", "1 / (me * λC^3 * Fq)")
qvoi = QMUUnit("Quantum Volumetric Inertia", "qvoi", "1 / (me * λC^3)")
qsrc = QMUUnit("Quantum Surface Receptivity", "qsrc", "1 / (me * λC^2 * Fq^3)")
qusi = QMUUnit("Quantum Surface Inertia", "qusi", "1 / (me * λC^2 * Fq^2)")
qarg = QMUUnit("Quantum Angular Receptivity Gauge", "qarg", "1 / (me * λC^2 * Fq)")
qari = QMUUnit("Quantum Area Inertia", "qari", "1 / (me * λC^2)")
qili = QMUUnit("Quantum Inverse Light Intensity", "qili", "1 / (me * λC * Fq^3)")
sptn = QMUUnit("Spatial Tensility", "sptn", "1 / (me * λC * Fq^2)")
qmob = QMUUnit("Quantum Mobility", "qmob", "1 / (me * λC * Fq)")
qflx = QMUUnit("Quantum Flexibility", "qflx", "1 / (me * λC)")
qopq = QMUUnit("Quantum Opacity", "qopq", "1 / (me * Fq^3)")
qspr = QMUUnit("Quantum Spreadability", "qspr", "1 / (me * Fq^2)")
dfld = QMUUnit("Displacement Field", "dfld", "1 / (me * Fq)")
qexl = QMUUnit("Quantum Existential Limit", "qexl", "1 / me")

# Density and Distributional Behavioral Units
qmfa = QMUUnit("Quantum Mass Frequency Activity", "qmfa", "me * Fq^3 / λC^3")
qmro = QMUUnit("Quantum Mass Resonance Occupation", "qmro", "me * Fq^2 / λC^3")
qmfo = QMUUnit("Quantum Mass Frequency Oscillation", "qmfo", "me * Fq / λC^3")
masd = QMUUnit("Mass Density", "masd", "me / λC^3")
qsac = QMUUnit("Quantum Surface Activity", "qsac", "me * Fq^3 / λC^2")
fdns = QMUUnit("Force Density", "fdns", "me * Fq^2 / λC^2")
momd = QMUUnit("Momentum Density", "momd", "me * Fq / λC^2")
sfcd = QMUUnit("Surface Density", "sfcd", "me / λC^2")
pdrt = QMUUnit("Pressure Diffusion Rate", "pdrt", "me * Fq^3 / λC")
pres = QMUUnit("Pressure", "pres", "me * Fq^2 / λC")
visc = QMUUnit("Viscosity", "visc", "me * Fq / λC")
ldns = QMUUnit("Length Density", "ldns", "me / λC", shorthand="rbnd")
qvfi = QMUUnit("Quantum Volume Fluctuation Impedance", "qvfi", "λC^3 / (me * Fq^3)")
qvtc = QMUUnit("Quantum Volume Temporal Compliance", "qvtc", "λC^3 / (me * Fq^2)")
qvdf = QMUUnit("Quantum Volume Dynamic Flux", "qvdf", "λC^3 / (me * Fq)")
spcv = QMUUnit("Specific Volume", "spcv", "λC^3 / me")
qarc = QMUUnit("Quantum Area Resonance Compliance", "qarc", "λC^2 / (me * Fq^2)")
qsdc = QMUUnit("Quantum Surface Dynamic Compliance", "qsdc", "λC^2 / (me * Fq)")
spar = QMUUnit("Specific Area", "spar", "λC^2 / me")
qlod = QMUUnit("Quantum Linear Oscillation Density", "qlod", "λC / (me * Fq^3)")
qldc = QMUUnit("Quantum Linear Dynamic Compliance", "qldc", "λC / (me * Fq^2)")
qltc = QMUUnit("Quantum Linear Temporal Compliance", "qltc", "λC / (me * Fq)")
spln = QMUUnit("Specific Length", "spln", "λC / me")

# Coupling and Interactional Behavioral Units
qdir = QMUUnit("Quantum Density Intensity Resistance", "qdir", "me / (λC^3 * Fq^3)")
mrcr = QMUUnit("Mass-Resonance Coupling Ratio", "mrcr", "me / (λC^3 * Fq^2)")
mfdr = QMUUnit("Mass-Frequency Distribution Ratio", "mfdr", "me / (λC^3 * Fq)")
scir = QMUUnit("Surface Charge Intensity Ratio", "scir", "me / (λC^2 * Fq^3)")
scoc = QMUUnit("Surface Charge Orbital Coefficient", "scoc", "me / (λC^2 * Fq^2)")
sctf = QMUUnit("Surface Charge Temporal Factor", "sctf", "me / (λC^2 * Fq)")
ldqr = QMUUnit("Length Density Quantum Ratio", "ldqr", "me / (λC * Fq^3)")
ldoc = QMUUnit("Length Density Orbital Coefficient", "ldoc", "me / (λC * Fq^2)")
ldtf = QMUUnit("Length Density Temporal Factor", "ldtf", "me / (λC * Fq)")
qmir = QMUUnit("Quantum Mass Intensity Resistance", "qmir", "me / Fq^3")
qmop = QMUUnit("Quantum Mass Orbital Period", "qmop", "me / Fq^2")
qmtc = QMUUnit("Quantum Mass Temporal Coefficient", "qmtc", "me / Fq")
qvod = QMUUnit("Quantum Volume Oscillation Density", "qvod", "Fq^3 * λC^3 / me")
qagm = QMUUnit("Quantum Aether Gravitational Mobility", "qagm", "λC^3 * Fq^2 / me")
qavm = QMUUnit("Quantum Aether Volumetric Flux Mobility", "qavm", "λC^3 * Fq / me")
qasm = QMUUnit("Quantum Aether Surface Oscillation Mobility", "qasm", "λC^2 * Fq^3 / me")
qatm = QMUUnit("Quantum Aether Thermal Mobility", "qatm", "λC^2 * Fq^2 / me")
qaam = QMUUnit("Quantum Aether Angular Mobility", "qaam", "λC^2 * Fq / me")
qadi = QMUUnit("Quantum Aether Dynamic Intensity", "qadi", "λC * Fq^3 / me")
qadm = QMUUnit("Quantum Aether Dynamic Mobility", "qadm", "λC * Fq^2 / me")
qamo = QMUUnit("Quantum Aether Mobility", "qamo", "λC * Fq / me")

# Oscillation and Spatial Dynamics Units
qvos = QMUUnit("Quantum Volume Oscillation", "qvos", "λC^3 * Fq^3")
dtrd = QMUUnit("Double Toroid or Volume Resonance", "dtrd", "λC^3 * Fq^2")
flow = QMUUnit("Flow", "flow", "λC^3 * Fq")
volm = QMUUnit("Volume", "volm", "λC^3")
qsfo = QMUUnit("Quantum Surface Oscillation", "qsfo", "λC^2 * Fq^3")
temp = QMUUnit("Temperature", "temp", "λC^2 * Fq^2")
swep = QMUUnit("Sweep or Angular Velocity", "swep", "λC^2 * Fq")
area = QMUUnit("Area", "area", "λC^2")
qdyf = QMUUnit("Quantum Dynamic Frequency", "qdyf", "λC * Fq^3")
accl = QMUUnit("Acceleration", "accl", "λC * Fq^2")
velc = QMUUnit("Quantum Velocity", "velc", "λC * Fq", shorthand="c")
qinf = QMUUnit("Quantum Intensity Factor", "qinf", "Fq^3")
rson = QMUUnit("Resonance", "rson", "Fq^2")
qvor = QMUUnit("Quantum Volume Oscillation Resistance", "qvor", "1 / (λC^3 * Fq^3)")
invr = QMUUnit("Inverse Volume Resonance", "invr", "1 / (λC^3 * Fq^2)")
vfdn = QMUUnit("Volumetric Field Density", "vfdn", "1 / (λC^3 * Fq)")
fint = QMUUnit("Field Intensity", "fint", "1 / λC^3")
qsfi = QMUUnit("Quantum Surface Frequency Impedance", "qsfi", "1 / (λC^2 * Fq^3)")
qsin = QMUUnit("Quantum Surface Intensity", "qsin", "1 / (λC^2 * Fq^2)")
sfrs = QMUUnit("Surface Flux Resistance", "sfrs", "1 / (λC^2 * Fq)")
bndr = QMUUnit("Bending Radius", "bndr", "1 / λC^2")
qdfr = QMUUnit("Quantum Dynamic Frequency Resistance", "qdfr", "1 / (λC * Fq^3)")
morc = QMUUnit("Momentum Resistance Coefficient", "morc", "1 / (λC * Fq^2)")
quid = QMUUnit("Quantum Inertial Density", "quid", "1 / (λC * Fq)")
wavn = QMUUnit("Wave Number", "wavn", "1 / λC")
qire = QMUUnit("Quantum Intensity Resistance", "qire", "1 / Fq^3")
orbt = QMUUnit("Orbit", "orbt", "1 / Fq^2")
time = QMUUnit("Time", "time", "1 / Fq")

# Spatial-Temporal Dynamics Units
ovev = QMUUnit("Orbital Volume Evolution", "ovev", "λC^3 * Fq^3")
voco = QMUUnit("Volumetric Orbital Coherence", "voco", "λC^3 * Fq^2")
vlmt = QMUUnit("Volume-Time", "vlmt", "λC^3 * Fq")
tafx = QMUUnit("Temporal Area Flux", "tafx", "λC^2 * Fq^3")
atfx = QMUUnit("Area-Time Flux", "atfx", "λC^2 * Fq^2")
acta = QMUUnit("Active Area", "acta", "λC^2 * Fq")
hepl = QMUUnit("Helical Path Length", "hepl", "λC * Fq^3")
qtrl = QMUUnit("Quantum Trajectory Length", "qtrl", "λC * Fq^2")
dynl = QMUUnit("Dynamic Length", "dynl", "λC * Fq")
voqo = QMUUnit("Volumetric Quantum Oscillation", "voqo", "Fq^3 / λC^3")
vlmr = QMUUnit("Volumetric Resonance", "vlmr", "Fq^2 / λC^3")
vlmw = QMUUnit("Volumetric Wave Frequency", "vlmw", "Fq / λC^3")
tqod = QMUUnit("Transverse Quantum Oscillation Density", "tqod", "Fq^3 / λC^2")
tvsr = QMUUnit("Transverse Surface Resonance", "tvsr", "Fq^2 / λC^2")
tvsw = QMUUnit("Transverse Surface Wave", "tvsw", "Fq / λC^2")
sqod = QMUUnit("Scalar Quantum Oscillation Density", "sqod", "Fq^3 / λC")
sclr = QMUUnit("Scalar Resonance", "sclr", "Fq^2 / λC")
sclw = QMUUnit("Scalar Wave", "sclw", "Fq / λC")

# Lone Unit
eddy = QMUUnit("Eddy Current", "eddy", "mflx^2")

# Create a reverse mapping from base unit expressions to derived units
derived_units_map = {}

def create_derived_units_map():
    for symbol, unit in all_units.items():
        if unit.expression:
            base_units = unit.to_base_units()
            expression = "*".join(sorted([f"{sym}^{pow}" if pow != 1 else sym for sym, pow in base_units.items() if pow != 0]))
            expression = re.sub(r'\^1(?!\d)', '', expression)
            derived_units_map[expression] = unit
            print(f"Debug: Added to derived_units_map - {expression}: {symbol}")  # Debug output
    
    print("\nDebug: Derived units map:")
    for expr, unit in derived_units_map.items():
        print(f"{expr}: {unit.symbol}")
            
# Dictionary of all units for easy access
# Complete dictionary of all units for easy access
all_units = {
    'mass': mass, 'leng': leng, 'freq': freq, 'chrg': chrg,
    'rmfd': rmfd, 'mfld': mfld, 'mvlm': mvlm, 'potn': potn,
    'mflx': mflx, 'indc': indc, 'elfs': elfs, 'magr': magr,
    'perm': perm, 'dvef': dvef, 'mfxd': mfxd, 'mchg': mchg,
    'mfde': mfde, 'mfir': mfir, 'ptty': ptty, 'aefp': aefp,
    'cond': cond, 'capc': capc, 'curl': curl, 'exdf': exdf,
    'accp': accp, 'expr': expr, 'cdns': cdns, 'cvef': cvef,
    'fric': fric, 'mgfi': mgfi, 'ffeq': ffeq, 'kfcn': kfcn,
    'resn': resn, 'magp': magp, 'mfdw': mfdw, 'mdif': mdif,
    'thmf': thmf, 'arsf': arsf, 'pccf': pccf, 'mopp': mopp,
    'emro': emro, 'emic': emic, 'cfff': cfff, 'masc': masc,
    'admt': admt, 'mrlc': mrlc, 'mcri': mcri, 'mfdr': mfdr,
    'mfen': mfen, 'mcup': mcup, 'msir': msir, 'qpmd': qpmd,
    'mcpp': mcpp, 'mcdr': mcdr, 'mcrd': mcrd, 'qild': qild,
    'qecf': qecf, 'cscc': cscc, 'chcc': chcc, 'qecj': qecj,
    'qeca': qeca, 'qecd': qecd, 'ecdp': ecdp, 'qeci': qeci,
    'qeco': qeco, 'ecfx': ecfx, 'mcaf': mcaf, 'efvr': efvr,
    'efva': efva, 'efvc': efvc, 'chvm': chvm, 'ball': ball,
    'plsm': plsm, 'magm': magm, 'sfch': sfch, 'efdr': efdr,
    'chac': chac, 'chvl': chvl, 'chgl': chgl, 'efti': efti,
    'chrs': chrs, 'curr': curr, 'qvci': qvci, 'qvcr': qvcr,
    'qvcp': qvcp, 'spch': spch, 'qcdr': qcdr, 'qcdp': qcdp,
    'qcdd': qcdd, 'chds': chds, 'qcrr': qcrr, 'qcrp': qcrp,
    'qcrd': qcrd, 'chgr': chgr, 'qcdi': qcdi, 'cdrs': cdrs,
    'cdos': cdos, 'chgd': chgd, 'qefi': qefi, 'qefr': qefr,
    'efxd': efxd, 'qegi': qegi, 'qegr': qegr, 'mfdi': mfdi,
    'elcg': elcg, 'trmo': trmo, 'vefd': vefd, 'efld': efld,
    'defi': defi, 'chgt': chgt, 'chgs': chgs, 'deff': deff,
    'chga': chga, 'chgv': chgv, 'defo': defo, 'crsn': crsn,
    'mcur': mcur, 'qefs': qefs, 'qefc': qefc, 'efrs': efrs,
    'mcdf': mcdf, 'qefp': qefp, 'qefe': qefe, 'efcd': efcd,
    'efsu': efsu, 'efpt': efpt, 'ligt': ligt, 'phtn': phtn,
    'qanr': qanr, 'vrtx': vrtx, 'powr': powr, 'enrg': enrg,
    'angm': angm, 'minr': minr, 'lint': lint, 'forc': forc,
    'momt': momt, 'torq': torq, 'irrd': irrd, 'sten': sten,
    'ints': ints, 'ocmp': ocmp, 'inpr': inpr, 'qvrc': qvrc,
    'qvoi': qvoi, 'qsrc': qsrc, 'qusi': qusi, 'qarg': qarg,
    'qari': qari, 'qili': qili, 'sptn': sptn, 'qmob': qmob,
    'qflx': qflx, 'qopq': qopq, 'qspr': qspr, 'dfld': dfld,
    'qexl': qexl, 'qmfa': qmfa, 'qmro': qmro, 'qmfo': qmfo,
    'masd': masd, 'qsac': qsac, 'fdns': fdns, 'momd': momd,
    'sfcd': sfcd, 'pdrt': pdrt, 'pres': pres, 'visc': visc,
    'ldns': ldns, 'qvfi': qvfi, 'qvtc': qvtc, 'qvdf': qvdf,
    'spcv': spcv, 'qarc': qarc, 'qsdc': qsdc, 'spar': spar,
    'qlod': qlod, 'qldc': qldc, 'qltc': qltc, 'spln': spln,
    'qdir': qdir, 'mrcr': mrcr, 'scir': scir, 'scoc': scoc,
    'sctf': sctf, 'ldqr': ldqr, 'ldoc': ldoc, 'ldtf': ldtf,
    'qmir': qmir, 'qmop': qmop, 'qmtc': qmtc, 'qvod': qvod,
    'qagm': qagm, 'qavm': qavm, 'qasm': qasm, 'qatm': qatm,
    'qaam': qaam, 'qadi': qadi, 'qadm': qadm, 'qamo': qamo,
    'qvos': qvos, 'dtrd': dtrd, 'flow': flow, 'volm': volm,
    'qsfo': qsfo, 'temp': temp, 'swep': swep, 'area': area,
    'qdyf': qdyf, 'accl': accl, 'velc': velc, 'qinf': qinf,
    'rson': rson, 'qvor': qvor, 'invr': invr, 'vfdn': vfdn,
    'fint': fint, 'qsfi': qsfi, 'qsin': qsin, 'sfrs': sfrs,
    'bndr': bndr, 'qdfr': qdfr, 'morc': morc, 'quid': quid,
    'wavn': wavn, 'qire': qire, 'orbt': orbt, 'time': time,
    'ovev': ovev, 'voco': voco, 'vlmt': vlmt, 'tafx': tafx,
    'atfx': atfx, 'acta': acta, 'hepl': hepl, 'qtrl': qtrl,
    'dynl': dynl, 'voqo': voqo, 'vlmr': vlmr, 'vlmw': vlmw,
    'tqod': tqod, 'tvsr': tvsr, 'tvsw': tvsw, 'sqod': sqod,
    'sclr': sclr, 'sclw': sclw, 'eddy': eddy
}
# Create a reverse mapping from base unit expressions to derived units
derived_units_map = {}

def create_derived_units_map():
    for unit in all_units.values():
        if unit.expression:
            base_units = unit.to_base_units()
            expression = "*".join([f"{sym}^{pow}" if pow != 1 else sym for sym, pow in sorted(base_units.items()) if pow != 0])
            derived_units_map[expression] = unit
    
    print("Debug: Derived units map:")  # Debug output
    for expr, unit in derived_units_map.items():
        print(f"{expr}: {unit.symbol}")

def simplify_and_match_unit(unit):
    if isinstance(unit, QMUQuantity):
        base_units = unit.unit.to_base_units()
    elif isinstance(unit, QMUUnit):
        base_units = unit.to_base_units()
    else:
        raise TypeError(f"Expected QMUQuantity or QMUUnit, got {type(unit)}")

    simplified_expression = "*".join(sorted([f"{sym}^{pow}" if pow != 1 else sym for sym, pow in base_units.items() if pow != 0]))
    simplified_expression = re.sub(r'\^1(?!\d)', '', simplified_expression)
    print(f"Debug: Simplified expression: {simplified_expression}")
    
    matched_unit = derived_units_map.get(simplified_expression)
    if matched_unit:
        print(f"Debug: Matched unit: {matched_unit.symbol}")
        return matched_unit
    else:
        print(f"Debug: No match found, creating custom unit")
        return QMUUnit("Custom Unit", simplified_expression, simplified_expression)

class QMUQuantity:
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __str__(self):
        return f"{self.value} {self.unit.symbol}"

    def __repr__(self):
        return self.__str__()

    def __mul__(self, other):
        if isinstance(other, QMUQuantity):
            new_value = self.value * other.value
            new_base_units = {k: self.unit.to_base_units().get(k, 0) + other.unit.to_base_units().get(k, 0) 
                              for k in set(self.unit.to_base_units()) | set(other.unit.to_base_units())}
            new_unit = QMUUnit("Composite", "*".join([f"{sym}^{pow}" for sym, pow in new_base_units.items() if pow != 0]))
            return QMUQuantity(new_value, new_unit)
        elif isinstance(other, (int, float)):
            return QMUQuantity(self.value * other, self.unit)
        else:
            raise TypeError(f"Multiplication not supported between QMUQuantity and {type(other)}")

    def __truediv__(self, other):
        if isinstance(other, QMUQuantity):
            new_value = self.value / other.value
            new_base_units = {k: self.unit.to_base_units().get(k, 0) - other.unit.to_base_units().get(k, 0) 
                              for k in set(self.unit.to_base_units()) | set(other.unit.to_base_units())}
            new_unit = QMUUnit("Composite", "*".join([f"{sym}^{pow}" for sym, pow in new_base_units.items() if pow != 0]))
            return QMUQuantity(new_value, new_unit)
        elif isinstance(other, (int, float)):
            return QMUQuantity(self.value / other, self.unit)
        else:
            raise TypeError(f"Division not supported between QMUQuantity and {type(other)}")

    def __add__(self, other):
        if not isinstance(other, QMUQuantity):
            raise TypeError(f"Addition not supported between QMUQuantity and {type(other)}")
        if self.unit != other.unit:
            raise ValueError(f"Cannot add quantities with different units: {self.unit.symbol} and {other.unit.symbol}")
        return QMUQuantity(self.value + other.value, self.unit)

    def __sub__(self, other):
        if not isinstance(other, QMUQuantity):
            raise TypeError(f"Subtraction not supported between QMUQuantity and {type(other)}")
        if self.unit != other.unit:
            raise ValueError(f"Cannot subtract quantities with different units: {self.unit.symbol} and {other.unit.symbol}")
        return QMUQuantity(self.value - other.value, self.unit)

# Call this function to initialize the derived_units_map
create_derived_units_map()

# Test function for multiplication
def test_multiplication():
    print("\nTesting multiplication of phtn and freq:")
    phtn_quantity = QMUQuantity(25, all_units['phtn'])
    freq_quantity = QMUQuantity(4, all_units['freq'])
    result = phtn_quantity * freq_quantity
    print(f"Result: {result}")
    print(f"Debug: Result unit type: {type(result.unit)}")
    print(f"Debug: Result unit: {result.unit}")

# Main test function
def run_tests():
    print("Testing QMU Units and Operations")
    print("=================================")

    # Test parse_expression
    print("\nTesting parse_expression:")
    for unit_name, unit in all_units.items():
        if unit.expression:
            print(f"{unit}")
            print(f"Base units: {unit.base_units}")

    # Test addition and subtraction
    print("\nTesting addition and subtraction:")
    length1 = QMUQuantity(5, all_units['leng'])
    length2 = QMUQuantity(3, all_units['leng'])
    
    sum_length = length1 + length2
    diff_length = length1 - length2
    
    print(f"Sum of lengths: {sum_length}")
    print(f"Difference of lengths: {diff_length}")
    
    # Test incompatible units
    print("\nTesting incompatible units:")
    mass1 = QMUQuantity(10, all_units['mass'])
    try:
        invalid_sum = length1 + mass1
    except ValueError as e:
        print(f"Error (as expected): {e}")
    
    # Test multiplication and division
    print("\nTesting multiplication and division:")
    area = length1 * length2
    print(f"Area: {area}")
    
    try:
        velocity = length1 / QMUQuantity(2, all_units['time'])
        print(f"Velocity: {velocity}")
    except KeyError:
        print("Note: 'time' unit not defined, skipping velocity calculation")

    test_multiplication()

if __name__ == "__main__":
    run_tests()
