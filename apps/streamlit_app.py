# apps/streamlit_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# Ensure repo root is on sys.path so we can import qmu_converter/ when running from apps/
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from qmu_converter.core import (
    load_unit_db,
    convert_si_to_qmu,
    convert_qmu_to_si,
    list_qmu_units,
)

st.set_page_config(page_title="QMU ⇄ SI Converter", layout="wide")

st.title("QMU ⇄ SI Converter")
st.caption(
    "Browser app for converting between SI and QMU using qmu_units.json as the authoritative unit database."
)

DB_PATH = REPO_ROOT / "qmu_units.json"

@st.cache_resource(show_spinner=False)
def _load_db(path: str):
    return load_unit_db(path)

if not DB_PATH.exists():
    st.error(f"qmu_units.json not found at: {DB_PATH}")
    st.stop()

with st.spinner("Loading QMU unit database..."):
    db = _load_db(str(DB_PATH))

st.success(f"Loaded and resolved {len(db.units)} QMU units from qmu_units.json.")

with st.expander("Accepted input forms and aliases", expanded=False):
    st.write(
        """
QMU aliases:
- `Fq = freq = F_q`
- `λC = leng`
- `Cd -> cond`, `h -> angm`, `c -> velc`

SI aliases:
- `V = volt = Volt = volts`
- `A = amp = ampere = amps`
- `Ω = Ohm = ohm = ohms`

Constants accepted in SI input:
- `mu0`, `μ0`, `\\mu_0`
- `epsilon0`, `eps0`, `ε0`, `\\epsilon_0`, `\\varepsilon_0`
- `4π` (interpreted as `4*pi`)
"""
    )

tab1, tab2, tab3 = st.tabs(["SI → QMU", "QMU → SI", "QMU Unit Browser"])

# -------------------------
# SI → QMU
# -------------------------
with tab1:
    c1, c2 = st.columns([2, 3], gap="large")

    with c1:
        st.subheader("Input (SI)")
        si_text = st.text_input(
            "Enter an SI quantity and unit",
            value="1 Hz",
            help="Examples: 1 V, 10 Hz, mu0, \\epsilon_0, 3.83e-17 henry",
        )
        run_si = st.button("Convert SI → QMU", type="primary")

    with c2:
        st.subheader("Result")
        if run_si:
            try:
                res = convert_si_to_qmu(db, si_text)
                if not res.get("ok", False):
                    st.error(res.get("notes", "Conversion failed."))
                    st.json(res)
                else:
                    st.metric("Preferred QMU unit", res["preferred_unit"])
                    st.metric("QMU value", f'{res["qmu_value"]:.15g}')
                    st.write(f"SI dimension (kg,m,s,A): `{res['si_dim']}`")
                    if res.get("notes"):
                        st.info(res["notes"])
                    matches = res.get("matches", [])
                    if matches:
                        st.write("Matching QMU units (same SI dimension):")
                        st.code(", ".join(matches))
            except Exception as e:
                st.error(f"Conversion error: {e}")

# -------------------------
# QMU → SI
# -------------------------
with tab2:
    c1, c2 = st.columns([2, 3], gap="large")

    with c1:
        st.subheader("Input (QMU)")
        qmu_text = st.text_input(
            "Enter a QMU quantity and unit",
            value="1 freq",
            help="Examples: 1 Fq, 1 freq, 1 F_q, 1 λC, 1 leng, 1 potn, 0.051 curr, Cd, h, c",
        )
        run_qmu = st.button("Convert QMU → SI", type="primary")

    with c2:
        st.subheader("Result")
        if run_qmu:
            try:
                res = convert_qmu_to_si(db, qmu_text)
                if not res.get("ok", False):
                    st.error(res.get("error", "Conversion failed."))
                    st.json(res)
                else:
                    st.metric("QMU unit", res["qmu_unit"])
                    st.metric("SI value", f'{res["si_value"]:.15g}')
                    st.write(f"SI dimension (kg,m,s,A): `{res['si_dim']}`")
                    hint = res.get("si_hint") or ""
                    if hint:
                        st.write(f"Best-effort SI unit hint: `{hint}`")
            except Exception as e:
                st.error(f"Conversion error: {e}")

# -------------------------
# Unit Browser
# -------------------------
with tab3:
    st.subheader("Browse QMU units")
    st.caption("Search by symbol or name; select a row to view details.")

    units = list_qmu_units(db)

    # Streamlit includes pandas; using it improves display and filtering.
    import pandas as pd

    df = pd.DataFrame(units)

    search = st.text_input("Search", value="", help="Search symbols/names (case-insensitive).")
    if search.strip():
        s = search.strip().lower()
        df_view = df[
            df["symbol"].str.lower().str.contains(s)
            | df["name"].str.lower().str.contains(s)
            | df["shorthand"].astype(str).str.lower().str.contains(s)
        ].copy()
    else:
        df_view = df.copy()

    st.write(f"Showing {len(df_view)} of {len(df)} units.")

    # Show a compact table; details below
    show_cols = ["symbol", "name", "shorthand", "si_dim", "si_value"]
    st.dataframe(df_view[show_cols], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Details")

    sym = st.selectbox(
        "Select a QMU symbol",
        options=sorted(df_view["symbol"].tolist()) if len(df_view) else sorted(df["symbol"].tolist()),
    )
    row = df[df["symbol"] == sym].iloc[0].to_dict()

    st.write(f"Name: {row.get('name','')}")
    if row.get("shorthand"):
        st.write(f"Shorthand: `{row['shorthand']}`")
    if row.get("expression"):
        st.write("Expression:")
        st.code(row["expression"])
    if row.get("si_equivalent"):
        st.write("si_equivalent:")
        st.code(row["si_equivalent"])
    st.write(f"SI dimension (kg,m,s,A): `{row.get('si_dim','')}`")
    st.write(f"SI numeric value: `{row.get('si_value','')}`")
