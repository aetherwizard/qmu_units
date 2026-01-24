# qmu_units

Quantum Measurement Units (QMU) calculator and unit database for the Aether Physics Model (APM).

**Live web app:** https://qmuunits.streamlit.app/

## What this repository contains

### Unit database
- **`qmu_units.json`**: authoritative catalog of QMU units, symbols, definitions, and expressions.

### Web application (Streamlit)
- **`apps/streamlit_app.py`**: browser interface for SI ⇄ QMU conversions and unit browsing.

### Conversion engine (Python)
- **`qmu_converter/core.py`**: loads and resolves the full unit graph from `qmu_units.json` and performs conversions.

## Web app usage

The Streamlit app supports:
- **SI → QMU** (accepts common SI spellings and symbols)
- **QMU → SI** (accepts canonical QMU symbols plus a limited alias set)
- **Unit browser** (search by symbol and name)

### Examples

**SI → QMU**
- `1 Hz`
- `1 V` (also `1 volt`, `1 Volt`)
- `1 A` (also `1 amp`, `1 ampere`)
- `\mu_0` (also `mu0`, `μ0`)
- `\epsilon_0` (also `epsilon0`, `\varepsilon_0`)

**QMU → SI**
- `1 Fq` (aliases: `1 freq`, `1 F_q`)
- `1 λC` (alias: `1 leng`)
- `0.051 curr`
- `1 potn`
- `Cd` (alias for `cond`), `h` (alias for `angm`), `c` (alias for `velc`)

## Run locally (Ubuntu/Linux)

1. **Clone**
   - `git clone https://github.com/aetherwizard/qmu_units.git`
   - `cd qmu_units`

2. **Create and activate a virtual environment (recommended)**
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`

3. **Install dependencies**
   - `pip install -r requirements.txt`

4. **Run the Streamlit app**
   - `streamlit run apps/streamlit_app.py`

## Project conventions

- **Source of truth:** `qmu_units.json` defines unit symbols and expressions.
- **Dimensional basis:** the converter resolves unit expressions into SI base dimensions `(kg, m, s, A)` and a numeric scale factor.

### Accepted aliases

**QMU input aliases**
- `Fq = freq = F_q`
- `λC = leng`
- `Cd → cond`
- `h → angm`
- `c → velc`

**SI constants**
- `\mu_0` (also `mu0`, `μ0`)
- `\epsilon_0` (also `epsilon0`, `\varepsilon_0`)

## Contributing

Contributions are welcome, especially:
- SI input aliases and parsing improvements
- Streamlit UI improvements
- Corrections/additions to `qmu_units.json`
- Test coverage and validation checks

**Issues and feature requests:** https://github.com/aetherwizard/qmu_units/issues

Suggested workflow:
1. Fork the repository
2. Create a feature branch
3. Open a Pull Request

## License

Creative Commons Zero v1.0 Universal (CC0-1.0)

## Contact

David Thomson  
Quantum AetherDynamics Institute  
Alma, Illinois  
david@quantumaetherdynamics.org
