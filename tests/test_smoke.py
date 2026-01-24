from __future__ import annotations

from pathlib import Path

import pytest

from qmu_converter.core import load_unit_db, convert_si_to_qmu, convert_qmu_to_si


REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "qmu_units.json"


@pytest.fixture(scope="session")
def db():
    if not DB_PATH.exists():
        raise RuntimeError(f"qmu_units.json not found at {DB_PATH}")
    return load_unit_db(DB_PATH)


def _qmu_value_for_unit_from_si_result(db, si_result: dict, unit_symbol: str) -> float:
    """
    Given the SI→QMU conversion result dict, compute the QMU value for a specific
    matching unit symbol using the resolved db scale factors.
    """
    assert si_result.get("ok", False), f"SI→QMU conversion failed: {si_result}"
    if unit_symbol not in db.units:
        raise AssertionError(f"Unit {unit_symbol!r} not present in db.units.")
    si_value = float(si_result["si_value"])
    unit_si_value = float(db.units[unit_symbol].si_qty.value)
    return si_value / unit_si_value


def test_db_resolves_all_units(db):
    # If load_unit_db succeeds, the unit graph fully resolves by construction.
    assert len(db.units) > 0


def test_hz_maps_to_frequency_unit(db):
    res = convert_si_to_qmu(db, "1 Hz")
    assert res.get("ok", False)
    # Prefer Fq if it is present; otherwise accept any dimensionally-matching unit.
    assert "Fq" in res.get("matches", []) or res.get("preferred_unit") == "Fq"


def test_current_anchor_amp_to_curr(db):
    # Known reference expectation from your manual check: 1 A ≈ 0.051 curr
    res = convert_si_to_qmu(db, "1 A")
    assert res.get("ok", False)
    assert "curr" in res.get("matches", []) or res.get("preferred_unit") == "curr"

    curr_per_amp = _qmu_value_for_unit_from_si_result(db, res, "curr")
    # Loose but meaningful tolerance around the expected ~0.051
    assert curr_per_amp == pytest.approx(0.051, rel=0.03)

    # Internal-consistency cross-check: invert (A per curr)
    back = convert_qmu_to_si(db, "1 curr")
    assert back.get("ok", False)
    A_per_curr = float(back["si_value"])
    assert curr_per_amp == pytest.approx(1.0 / A_per_curr, rel=1e-12)


def test_voltage_anchor_volt_to_potn(db):
    # Known reference expectation from your manual check: 1 V ≈ 1.957e-6 potn
    res = convert_si_to_qmu(db, "1 V")
    assert res.get("ok", False)
    assert "potn" in res.get("matches", []) or res.get("preferred_unit") == "potn"

    potn_per_volt = _qmu_value_for_unit_from_si_result(db, res, "potn")
    assert potn_per_volt == pytest.approx(1.957e-6, rel=0.03)

    # Internal-consistency cross-check: invert (V per potn)
    back = convert_qmu_to_si(db, "1 potn")
    assert back.get("ok", False)
    V_per_potn = float(back["si_value"])
    assert potn_per_volt == pytest.approx(1.0 / V_per_potn, rel=1e-12)


def test_mu0_and_epsilon0_symbols_parse(db):
    # These tests ensure the SI parser accepts the common spellings.
    # They do not force a particular preferred unit symbol; they verify conversion succeeds.
    for expr in ["mu0", "\\mu_0", "μ0"]:
        res = convert_si_to_qmu(db, expr)
        assert res.get("ok", False), f"Failed for {expr}: {res}"

    for expr in ["epsilon0", "eps0", "\\epsilon_0", "\\varepsilon_0", "ε0"]:
        res = convert_si_to_qmu(db, expr)
        assert res.get("ok", False), f"Failed for {expr}: {res}"
