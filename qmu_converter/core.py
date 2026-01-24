# qmu_converter/core.py
"""
QMU ⇄ SI conversion core (resolver-based, full unit coverage)

This module:
- Loads qmu_units.json as the authoritative unit graph.
- Resolves every QMU unit into an SI scale factor and SI base-dimension signature (kg, m, s, A).
- Converts:
    * SI expression -> preferred matching QMU unit + list of matches
    * QMU unit -> SI numeric value + SI-dimension signature + best-effort SI symbol hint
- Supports aliasing:
    QMU: Fq = freq = F_q, λC = leng, Cd->cond, h->angm, c->velc
    SI:  V=volt=Volt=volts, A=amp=ampere=amps, Ω=Ohm=ohm=ohms, etc.
    Constants: mu0, μ0, \\mu_0; epsilon0/eps0, ε0, \\epsilon_0, \\varepsilon_0; 4π
- Evaluates qmu_units.json fields:
    * "expression" (in QMU atoms/units, multiplicative)
    * "si_equivalent" (SI expression, multiplicative)

API:
    load_unit_db(json_path="qmu_units.json") -> UnitDB
    list_qmu_units(db) -> list[dict]
    convert_si_to_qmu(db, text) -> dict
    convert_qmu_to_si(db, text) -> dict
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ----------------------------
# Physical constants (SI)
# ----------------------------
PI = math.pi

C_SI = 299_792_458.0                 # exact
ME_SI = 9.1093837015e-31             # kg
E_SI = 1.602176634e-19               # C
ALPHA = 7.2973525693e-3

MU0 = 1.25663706212e-6               # H/m
EPS0 = 8.8541878128e-12              # F/m
LAMBDA_C = 2.42631023867e-12         # m (electron Compton wavelength)

FQ = C_SI / LAMBDA_C                 # 1/s
CURR_SIALIGNED_A = E_SI * FQ         # A
POTN_SIALIGNED_V = ME_SI * (C_SI**2) / E_SI   # V
CCF_E = E_SI / (8.0 * PI * ALPHA)    # Coulomb (dimension of single charge)

SI_BASE_ORDER = ("kg", "m", "s", "A")


# ----------------------------
# SI dimension + quantity algebra
# ----------------------------
@dataclass(frozen=True)
class SIDim:
    exp: Dict[str, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "exp", {k: v for k, v in self.exp.items() if v != 0})

    def sig(self) -> Tuple[int, int, int, int]:
        return tuple(self.exp.get(b, 0) for b in SI_BASE_ORDER)


@dataclass(frozen=True)
class SIQty:
    value: float
    dim: SIDim

    def mul(self, other: "SIQty") -> "SIQty":
        d = dict(self.dim.exp)
        for k, v in other.dim.exp.items():
            d[k] = d.get(k, 0) + v
            if d[k] == 0:
                d.pop(k, None)
        return SIQty(self.value * other.value, SIDim(d))

    def inv(self) -> "SIQty":
        return SIQty(1.0 / self.value, SIDim({k: -v for k, v in self.dim.exp.items()}))

    def pow(self, p: int) -> "SIQty":
        return SIQty(self.value ** p, SIDim({k: v * p for k, v in self.dim.exp.items()}))


# ----------------------------
# Tokenizer + multiplicative expression parser
# ----------------------------
Token = Tuple[str, str]
_TOKEN_RE = re.compile(
    r"""
    (?P<WS>\s+)
  | (?P<NUMBER>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)
  | (?P<NAME>[A-Za-z_λµΩπ]+[A-Za-z0-9_λµΩπ]*)
  | (?P<POW>\^)
  | (?P<MUL>\*)
  | (?P<DIV>/)
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
""",
    re.VERBOSE,
)


class ExprParseError(ValueError):
    pass


def tokenize(s: str) -> List[Token]:
    out: List[Token] = []
    i = 0
    while i < len(s):
        m = _TOKEN_RE.match(s, i)
        if not m:
            raise ExprParseError(f"Unexpected character at position {i}: {s[i:i+20]!r}")
        typ = m.lastgroup
        val = m.group(typ)
        i = m.end()
        if typ == "WS":
            continue
        out.append((typ, val))
    return out


def parse_product_qty(tokens: List[Token], name_to_qty: Dict[str, SIQty]) -> SIQty:
    pos = 0

    def peek() -> Token:
        return tokens[pos] if pos < len(tokens) else ("EOF", "")

    def consume(expected: Optional[str] = None) -> Token:
        nonlocal pos
        tok = peek()
        if expected and tok[0] != expected:
            raise ExprParseError(f"Expected {expected}, got {tok[0]}")
        pos += 1
        return tok

    def parse_int() -> int:
        tok = consume("NUMBER")
        if "." in tok[1] or "e" in tok[1].lower():
            raise ExprParseError("Exponent must be an integer.")
        return int(tok[1])

    def primary() -> SIQty:
        tok = peek()
        if tok[0] == "NUMBER":
            consume("NUMBER")
            return SIQty(float(tok[1]), SIDim({}))
        if tok[0] == "NAME":
            consume("NAME")
            key = tok[1]
            if key not in name_to_qty:
                raise ExprParseError(f"Unknown symbol {key!r}")
            return name_to_qty[key]
        if tok[0] == "LPAREN":
            consume("LPAREN")
            q = expr()
            consume("RPAREN")
            return q
        raise ExprParseError(f"Expected NAME/NUMBER/'(', got {tok}")

    def atom() -> SIQty:
        q = primary()
        if peek()[0] == "POW":
            consume("POW")
            p = parse_int()
            q = q.pow(p)
        return q

    def expr() -> SIQty:
        q = atom()
        while True:
            tok = peek()
            if tok[0] == "MUL":
                consume("MUL")
                q = q.mul(atom())
            elif tok[0] == "DIV":
                consume("DIV")
                q = q.mul(atom().inv())
            else:
                break
        return q

    q = expr()
    if peek()[0] != "EOF":
        raise ExprParseError(f"Unexpected trailing token {peek()}")
    return q


# ----------------------------
# Parsing helpers and normalization
# ----------------------------
def normalize_text_constants(s: str) -> str:
    s = s.strip()
    s = s.replace("4π", "4*pi").replace("π", "pi")
    s = s.replace("\\mu_0", "mu0").replace("mu_0", "mu0").replace("μ0", "mu0")
    s = s.replace("\\epsilon_0", "epsilon0").replace("\\varepsilon_0", "epsilon0")
    s = s.replace("epsilon_0", "epsilon0").replace("ε0", "epsilon0").replace("ϵ0", "epsilon0")
    return s


def parse_value_and_unit(s: str) -> Tuple[float, str]:
    s = s.strip()
    m = re.match(r'^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+(.*)$', s)
    if m:
        return float(m.group(1)), m.group(2).strip()
    return 1.0, s


def si_unit_catalog() -> Dict[str, SIQty]:
    cat: Dict[str, SIQty] = {
        # base units
        "kg": SIQty(1.0, SIDim({"kg": 1})),
        "m":  SIQty(1.0, SIDim({"m": 1})),
        "s":  SIQty(1.0, SIDim({"s": 1})),
        "A":  SIQty(1.0, SIDim({"A": 1})),
        # constants / dimensionless
        "pi": SIQty(PI, SIDim({})),
        "alpha": SIQty(ALPHA, SIDim({})),
        # EM constants
        "mu0": SIQty(MU0, SIDim({"kg": 1, "m": 1, "s": -2, "A": -2})),         # H/m
        "epsilon0": SIQty(EPS0, SIDim({"kg": -1, "m": -3, "s": 4, "A": 2})),    # F/m
        "eps0": SIQty(EPS0, SIDim({"kg": -1, "m": -3, "s": 4, "A": 2})),
    }

    # derived SI unit dimensions (value 1)
    derived = {
        "Hz":  SIDim({"s": -1}),
        "N":   SIDim({"kg": 1, "m": 1, "s": -2}),
        "J":   SIDim({"kg": 1, "m": 2, "s": -2}),
        "W":   SIDim({"kg": 1, "m": 2, "s": -3}),
        "Pa":  SIDim({"kg": 1, "m": -1, "s": -2}),
        "C":   SIDim({"A": 1, "s": 1}),
        "V":   SIDim({"kg": 1, "m": 2, "s": -3, "A": -1}),
        "Ohm": SIDim({"kg": 1, "m": 2, "s": -3, "A": -2}),
        "S":   SIDim({"kg": -1, "m": -2, "s": 3, "A": 2}),
        "F":   SIDim({"kg": -1, "m": -2, "s": 4, "A": 2}),
        "T":   SIDim({"kg": 1, "s": -2, "A": -1}),
        "H":   SIDim({"kg": 1, "m": 2, "s": -2, "A": -2}),
        "Wb":  SIDim({"kg": 1, "m": 2, "s": -2, "A": -1}),
    }
    for k, d in derived.items():
        cat[k] = SIQty(1.0, d)

    # aliases
    aliases = {
        "volt": "V", "volts": "V", "Volt": "V", "Volts": "V",
        "ampere": "A", "amperes": "A", "Ampere": "A", "Amperes": "A",
        "amp": "A", "amps": "A", "Amp": "A", "Amps": "A",
        "ohm": "Ohm", "ohms": "Ohm", "Ω": "Ohm",
        "siemens": "S", "Siemens": "S",
        "henry": "H", "Henry": "H",
        "tesla": "T", "Tesla": "T",
        "weber": "Wb", "Weber": "Wb",
        "mu_0": "mu0", "μ0": "mu0", "\\mu_0": "mu0",
        "epsilon_0": "epsilon0", "\\epsilon_0": "epsilon0", "\\varepsilon_0": "epsilon0",
        "ε0": "epsilon0", "ϵ0": "epsilon0",
    }
    for a, b in aliases.items():
        if b in cat:
            cat[a] = cat[b]
    return cat


def parse_si_quantity(s: str) -> SIQty:
    s = normalize_text_constants(s)
    v, unit_expr = parse_value_and_unit(s)
    cat = si_unit_catalog()

    toks = tokenize(unit_expr)
    norm_tokens: List[Token] = []
    for typ, val in toks:
        if typ == "NAME":
            if val in cat:
                norm_tokens.append((typ, val))
            else:
                low = val.lower()
                norm_tokens.append((typ, low if low in cat else val))
        else:
            norm_tokens.append((typ, val))

    unit_qty = parse_product_qty(norm_tokens, cat)
    return SIQty(v * unit_qty.value, unit_qty.dim)


# ----------------------------
# Unit DB: resolve QMU units to SIQty
# ----------------------------
@dataclass
class QMUUnit:
    symbol: str
    name: str
    expression: Optional[str]
    shorthand: Optional[str]
    si_equivalent_raw: Optional[str]
    si_qty: SIQty


class UnitDBError(RuntimeError):
    pass


class UnitDB:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.units: Dict[str, QMUUnit] = {}
        self._resolve_all()

    @classmethod
    def from_json(cls, path: str | Path) -> "UnitDB":
        data = json.loads(Path(path).read_text(encoding="utf-8"))

        # legacy fix: conductance density label
        if "cden" not in data:
            data["cden"] = {"name": "Conductance Density", "expression": "cond / λC"}
        if "cdns" in data and str(data["cdns"].get("name", "")).strip().lower() == "conductance density":
            data["cden"] = data.pop("cdns")

        return cls(data)

    def si_dim_str(self, dim: SIDim) -> str:
        parts = []
        for b in SI_BASE_ORDER:
            e = dim.exp.get(b, 0)
            if e == 0:
                continue
            parts.append(b if e == 1 else f"{b}^{e}")
        return " * ".join(parts) if parts else "1"

    def _qmu_seed(self) -> Dict[str, SIQty]:
        seed: Dict[str, SIQty] = {}

        # Base atoms: me [kg], λC [m], Fq [1/s], eemax [C]
        fallbacks = {
            "me": SIQty(ME_SI, SIDim({"kg": 1})),
            "λC": SIQty(LAMBDA_C, SIDim({"m": 1})),
            "Fq": SIQty(FQ, SIDim({"s": -1})),
            "eemax": SIQty(E_SI, SIDim({"A": 1, "s": 1})),
        }

        for sym, fb in fallbacks.items():
            meta = self.data.get(sym, {})
            se = meta.get("si_equivalent")
            if isinstance(se, str):
                try:
                    seed[sym] = self._eval_si_equivalent(se)
                    continue
                except Exception:
                    pass
            seed[sym] = fb

        return seed

    def _eval_si_equivalent(self, se: str) -> SIQty:
        s = normalize_text_constants(se)
        s = re.sub(r"\([^)]*\)", "", s).strip()
        # normalize some unit words
        s = s.replace("henry", "H").replace("farad", "F").replace("siemens", "S")
        return parse_si_quantity(s)

    def _eval_qmu_expression(self, expr: str, env: Dict[str, SIQty]) -> SIQty:
        expr = normalize_text_constants(expr)
        toks = tokenize(expr)
        return parse_product_qty(toks, env)

    def _resolve_all(self) -> None:
        unresolved: Dict[str, Any] = dict(self.data)
        resolved: Dict[str, SIQty] = {}

        resolved.update(self._qmu_seed())

        # Add dimensionless constants to env
        resolved["pi"] = SIQty(PI, SIDim({}))
        resolved["alpha"] = SIQty(ALPHA, SIDim({}))
        resolved["ccf_e"] = SIQty(CCF_E, SIDim({"A": 1, "s": 1}))

        # QMU aliases in environment (so expressions can use them)
        # Fq aliases:
        resolved["freq"] = resolved["Fq"]
        resolved["F_q"] = resolved["Fq"]
        # λC aliases:
        resolved["leng"] = resolved["λC"]

        # First, pre-resolve anything with si_equivalent
        for sym in list(unresolved.keys()):
            meta = unresolved[sym]
            se = meta.get("si_equivalent")
            if isinstance(se, str):
                try:
                    q = self._eval_si_equivalent(se)
                    resolved[sym] = q
                    sh = meta.get("shorthand")
                    if sh and sh not in resolved:
                        resolved[sh] = q
                except Exception:
                    pass

        max_iter = 25000
        for _ in range(max_iter):
            progress = False

            for sym in list(unresolved.keys()):
                meta = unresolved[sym]

                if sym in resolved:
                    # install unit record
                    self.units[sym] = QMUUnit(
                        symbol=sym,
                        name=meta.get("name", sym),
                        expression=meta.get("expression"),
                        shorthand=meta.get("shorthand"),
                        si_equivalent_raw=meta.get("si_equivalent"),
                        si_qty=resolved[sym],
                    )
                    unresolved.pop(sym)
                    progress = True
                    continue

                expr = meta.get("expression")
                if not expr:
                    continue

                try:
                    q = self._eval_qmu_expression(expr, resolved)
                except ExprParseError:
                    continue

                resolved[sym] = q
                sh = meta.get("shorthand")
                if sh and sh not in resolved:
                    resolved[sh] = q

                # shortcuts once units exist
                if sym == "cond":
                    resolved["Cd"] = q
                if sym == "angm":
                    resolved["h"] = q
                if sym == "velc":
                    resolved["c"] = q

                self.units[sym] = QMUUnit(
                    symbol=sym,
                    name=meta.get("name", sym),
                    expression=expr,
                    shorthand=meta.get("shorthand"),
                    si_equivalent_raw=meta.get("si_equivalent"),
                    si_qty=q,
                )
                unresolved.pop(sym)
                progress = True

            if not unresolved:
                return
            if not progress:
                missing = ", ".join(sorted(unresolved.keys())[:25])
                raise UnitDBError(f"Could not resolve {len(unresolved)} QMU units. First few: {missing}")

    def find_matches_for_si_dim(self, si_dim: SIDim) -> List[QMUUnit]:
        sig = si_dim.sig()
        matches = [u for u in self.units.values() if u.si_qty.dim.sig() == sig]
        matches.sort(key=lambda x: x.symbol)
        return matches


# ----------------------------
# Public API
# ----------------------------
def load_unit_db(json_path: str | Path = "qmu_units.json") -> UnitDB:
    return UnitDB.from_json(json_path)


def list_qmu_units(db: UnitDB) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for sym in sorted(db.units.keys()):
        u = db.units[sym]
        out.append(
            {
                "symbol": u.symbol,
                "name": u.name,
                "shorthand": u.shorthand or "",
                "expression": u.expression or "",
                "si_equivalent": u.si_equivalent_raw or "",
                "si_value": u.si_qty.value,
                "si_dim": db.si_dim_str(u.si_qty.dim),
            }
        )
    return out


QMU_INPUT_ALIASES = {
    "freq": "Fq",
    "F_q": "Fq",
    "FQ": "Fq",
    "leng": "λC",
    "Cd": "cond",
    "h": "angm",
    "c": "velc",
}


def _canonicalize_qmu_symbol(sym: str) -> str:
    return QMU_INPUT_ALIASES.get(sym, sym)


def convert_si_to_qmu(db: UnitDB, text: str) -> Dict[str, Any]:
    si_qty = parse_si_quantity(text)
    matches = db.find_matches_for_si_dim(si_qty.dim)

    if not matches:
        return {
            "ok": False,
            "input": text,
            "si_value": si_qty.value,
            "si_dim": db.si_dim_str(si_qty.dim),
            "matches": [],
            "preferred_unit": None,
            "qmu_value": None,
            "notes": "No QMU units with matching SI dimension.",
        }

    preferred = matches[0]
    qmu_value = si_qty.value / preferred.si_qty.value

    notes = ""
    if preferred.symbol == "potn":
        notes = f"Reference: 1 potn·ccf_e = m_e c^2/e = {POTN_SIALIGNED_V:.12g} V"
    elif preferred.symbol == "curr":
        notes = f"Reference: 1 curr = e Fq = {CURR_SIALIGNED_A:.12g} A"

    return {
        "ok": True,
        "input": text,
        "si_value": si_qty.value,
        "si_dim": db.si_dim_str(si_qty.dim),
        "matches": [u.symbol for u in matches],
        "preferred_unit": preferred.symbol,
        "qmu_value": qmu_value,
        "notes": notes,
    }


def convert_qmu_to_si(db: UnitDB, text: str) -> Dict[str, Any]:
    text = normalize_text_constants(text)
    v, unit = parse_value_and_unit(text)
    unit = _canonicalize_qmu_symbol(unit)

    if unit not in db.units:
        return {
            "ok": False,
            "input": text,
            "error": f"Unknown QMU unit symbol: {unit!r}",
        }

    u = db.units[unit]
    si_value = v * u.si_qty.value
    sig = u.si_qty.dim.sig()

    # best-effort SI hint by dimension signature
    hint = {
        (0, 0, -1, 0): "Hz",
        (0, 0, 0, 1): "A",
        (0, 0, 1, 1): "C",
        (1, 2, -2, 0): "J",
        (1, 2, -3, 0): "W",
        (1, 2, -3, -1): "V",
        (1, 2, -3, -2): "Ohm",
        (-1, -2, 3, 2): "S",
        (1, 1, -2, -2): "H/m",
        (-1, -3, 4, 2): "F/m",
    }.get(sig, "")

    return {
        "ok": True,
        "input": text,
        "qmu_value": v,
        "qmu_unit": unit,
        "si_value": si_value,
        "si_dim": db.si_dim_str(u.si_qty.dim),
        "si_hint": hint,
    }
