"""
🧮 VALUATION - Modelos de valoración y calidad (implementación propia)
======================================================================

Fórmulas estándar de finanzas corporativas, escritas desde cero:
- DCF de dos etapas sobre flujo de caja libre (FCF)
- DCF inverso: qué crecimiento descuenta el precio actual
- Tabla de sensibilidad WACC × crecimiento terminal
- Coste de capital por CAPM (WACC simplificado)
- Piotroski F-Score (9 señales de calidad contable)
- Altman Z-Score (riesgo de quiebra, versión original para industriales)

Todo trabaja con DataFrames de DataHub.financial_statement()
(filas = partidas, columnas = años, más reciente primero).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

import pandas as pd

from .data_hub import _row, _num, _safe_div


# ============================================================================
# DCF
# ============================================================================

@dataclass
class DCFResult:
    fair_value_per_share: Optional[float]
    enterprise_value: float
    equity_value: float
    pv_explicit: float
    pv_terminal: float
    terminal_share_of_ev: float
    assumptions: Dict[str, float]

    def to_dict(self) -> Dict:
        return asdict(self)


def dcf(fcf0: float, growth: float, years: int = 5, terminal_growth: float = 0.025,
        discount_rate: float = 0.09, net_debt: float = 0.0, shares: Optional[float] = None) -> DCFResult:
    """
    DCF de dos etapas:
      1) `years` años creciendo al `growth` anual
      2) valor terminal con crecimiento perpetuo `terminal_growth` (Gordon)
    """
    if discount_rate <= terminal_growth:
        raise ValueError("La tasa de descuento debe ser mayor que el crecimiento terminal")
    pv_explicit, fcf = 0.0, fcf0
    for t in range(1, years + 1):
        fcf *= (1 + growth)
        pv_explicit += fcf / (1 + discount_rate) ** t
    terminal = fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_terminal = terminal / (1 + discount_rate) ** years
    ev = pv_explicit + pv_terminal
    equity = ev - net_debt
    return DCFResult(
        fair_value_per_share=round(equity / shares, 2) if shares else None,
        enterprise_value=round(ev, 0),
        equity_value=round(equity, 0),
        pv_explicit=round(pv_explicit, 0),
        pv_terminal=round(pv_terminal, 0),
        terminal_share_of_ev=round(pv_terminal / ev, 3) if ev else 0.0,
        assumptions={"fcf0": fcf0, "growth": growth, "years": years, "terminal_growth": terminal_growth,
                     "discount_rate": discount_rate, "net_debt": net_debt, "shares": shares or 0},
    )


def reverse_dcf(price: float, shares: float, fcf0: float, net_debt: float = 0.0, years: int = 5,
                terminal_growth: float = 0.025, discount_rate: float = 0.09) -> Optional[float]:
    """Crecimiento anual de FCF que justifica el precio actual (búsqueda binaria)."""
    if fcf0 <= 0 or shares <= 0:
        return None
    target = price * shares + net_debt
    lo, hi = -0.5, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        ev = dcf(fcf0, mid, years, terminal_growth, discount_rate).enterprise_value
        lo, hi = (mid, hi) if ev < target else (lo, mid)
    implied = round((lo + hi) / 2, 4)
    return None if implied >= 0.999 or implied <= -0.499 else implied


def sensitivity_table(fcf0: float, growth: float, net_debt: float, shares: float, years: int = 5,
                      rates: Optional[List[float]] = None, terminals: Optional[List[float]] = None) -> pd.DataFrame:
    """Valor por acción para combinaciones de tasa de descuento (filas) y crecimiento terminal (columnas)."""
    rates = rates or [0.07, 0.08, 0.09, 0.10, 0.11]
    terminals = terminals or [0.015, 0.02, 0.025, 0.03]
    data = {}
    for g in terminals:
        data[f"g={g:.1%}"] = [
            dcf(fcf0, growth, years, g, r, net_debt, shares).fair_value_per_share if r > g else None for r in rates
        ]
    return pd.DataFrame(data, index=[f"r={r:.0%}" for r in rates])


def capm_discount_rate(beta: Optional[float], risk_free: float = 0.042, equity_premium: float = 0.05,
                       floor: float = 0.07, cap: float = 0.14) -> float:
    """Coste del capital por CAPM, acotado a un rango razonable."""
    b = beta if beta is not None and 0 < beta < 4 else 1.0
    return round(min(max(risk_free + b * equity_premium, floor), cap), 4)


# ============================================================================
# Calidad contable
# ============================================================================

def piotroski_f_score(income: pd.DataFrame, balance: pd.DataFrame, cashflow: pd.DataFrame) -> Dict:
    """
    Piotroski F-Score (0-9). Necesita al menos dos años.
    8-9 = muy sólida · 0-2 = débil.
    """
    def pair(df, *names):
        s = _row(df, *names)
        if s is None or len(s) < 2:
            return None, None
        return _num(s.iloc[0]), _num(s.iloc[1])

    if income is None or income.empty or balance is None or balance.empty or income.shape[1] < 2:
        return {"score": None, "max": 9, "label": "Datos insuficientes", "checks": {}}
    ni, ni_p = pair(income, "Net Income")
    ta, ta_p = pair(balance, "Total Assets")
    ocf, _ = pair(cashflow, "Operating Cash Flow")
    ltd, ltd_p = pair(balance, "Long Term Debt")
    ca, ca_p = pair(balance, "Current Assets")
    cl, cl_p = pair(balance, "Current Liabilities")
    sh, sh_p = pair(balance, "Ordinary Shares Number", "Share Issued")
    gp, gp_p = pair(income, "Gross Profit")
    rev, rev_p = pair(income, "Total Revenue")

    roa, roa_p = _safe_div(ni, ta), _safe_div(ni_p, ta_p)
    checks = {
        "roa_positivo": roa is not None and roa > 0,
        "flujo_operativo_positivo": ocf is not None and ocf > 0,
        "roa_mejora": roa is not None and roa_p is not None and roa > roa_p,
        "caja_supera_beneficio": ocf is not None and ni is not None and ocf > ni,
        "menos_apalancamiento": (_safe_div(ltd, ta) or 0) <= (_safe_div(ltd_p, ta_p) or 0) if ta and ta_p else False,
        "mejor_liquidez": (_safe_div(ca, cl) or 0) > (_safe_div(ca_p, cl_p) or 0) if cl and cl_p else False,
        "sin_dilucion": sh is not None and sh_p is not None and sh <= sh_p,
        "mejor_margen_bruto": (_safe_div(gp, rev) or 0) > (_safe_div(gp_p, rev_p) or 0) if rev and rev_p else False,
        "mejor_rotacion_activos": (_safe_div(rev, ta) or 0) > (_safe_div(rev_p, ta_p) or 0) if ta and ta_p else False,
    }
    score = sum(bool(v) for v in checks.values())
    label = "Fuerte" if score >= 7 else "Media" if score >= 4 else "Débil"
    return {"score": score, "max": 9, "label": label, "checks": checks}


def altman_z_score(income: pd.DataFrame, balance: pd.DataFrame, market_cap: Optional[float]) -> Dict:
    """
    Altman Z (1968). >2.99 zona segura · 1.81-2.99 zona gris · <1.81 zona de riesgo.
    Pensado para industriales; en bancos y aseguradoras no es aplicable.
    """
    v = lambda df, *n: _num(_row(df, *n).iloc[0]) if _row(df, *n) is not None else None
    ta = v(balance, "Total Assets")
    tl = v(balance, "Total Liabilities Net Minority Interest", "Total Liabilities")
    wc = v(balance, "Working Capital")
    re_ = v(balance, "Retained Earnings")
    ebit = v(income, "EBIT", "Operating Income")
    sales = v(income, "Total Revenue")
    if not ta or not tl or market_cap is None:
        return {"score": None, "zone": "Datos insuficientes"}
    z = (1.2 * (wc or 0) / ta + 1.4 * (re_ or 0) / ta + 3.3 * (ebit or 0) / ta
         + 0.6 * market_cap / tl + 1.0 * (sales or 0) / ta)
    zone = "Segura" if z > 2.99 else "Gris" if z >= 1.81 else "Riesgo"
    return {"score": round(z, 2), "zone": zone}


# ============================================================================
# Valoración automática a partir de DataHub
# ============================================================================

def auto_valuation(hub, ticker: str, growth: Optional[float] = None, discount_rate: Optional[float] = None,
                   terminal_growth: float = 0.025, years: int = 5) -> Dict:
    """
    DCF con supuestos razonables sacados de los datos:
    - FCF base = último FCF anual (si es negativo, el DCF no aplica)
    - crecimiento = CAGR de ingresos acotado a [0%, 15%] si no se indica
    - tasa = CAPM con la beta de la acción si no se indica
    """
    q = hub.quote(ticker)
    r = hub.key_ratios(ticker)
    cf = hub.financial_statement(ticker, "cashflow")
    info_shares = None
    try:
        info_shares = _num(hub._info(ticker).get("sharesOutstanding"))
    except Exception:
        pass

    fcf_row = _row(cf, "Free Cash Flow")
    fcf0 = _num(fcf_row.iloc[0]) if fcf_row is not None and len(fcf_row) else None
    price, shares = q.get("price"), info_shares
    net_debt = r["balance_sheet"].get("net_debt") or 0.0

    if not fcf0 or fcf0 <= 0 or not shares:
        return {"ticker": ticker.upper(), "applicable": False,
                "reason": "FCF negativo o sin datos de acciones: el DCF no es fiable para esta empresa."}

    cagr = r["growth"].get("revenue_cagr")
    g = growth if growth is not None else min(max(cagr if cagr is not None else 0.04, 0.0), 0.15)
    rate = discount_rate if discount_rate is not None else capm_discount_rate(q.get("beta"))
    base = dcf(fcf0, g, years, terminal_growth, rate, net_debt, shares)
    implied = reverse_dcf(price, shares, fcf0, net_debt, years, terminal_growth, rate) if price else None
    upside = _safe_div((base.fair_value_per_share or 0) - price, price) if price else None
    return {
        "ticker": ticker.upper(),
        "applicable": True,
        "price": price,
        "fair_value_per_share": base.fair_value_per_share,
        "upside": round(upside, 4) if upside is not None else None,
        "implied_growth_at_price": implied,
        "terminal_share_of_ev": base.terminal_share_of_ev,
        "assumptions": base.assumptions,
        "sensitivity": sensitivity_table(fcf0, g, net_debt, shares, years).to_dict(),
        "warning": "Modelo simplificado: los resultados dependen mucho de los supuestos.",
    }


def quality_scores(hub, ticker: str) -> Dict:
    inc = hub.financial_statement(ticker, "income")
    bal = hub.financial_statement(ticker, "balance")
    cf = hub.financial_statement(ticker, "cashflow")
    return {
        "ticker": ticker.upper(),
        "piotroski": piotroski_f_score(inc, bal, cf),
        "altman_z": altman_z_score(inc, bal, hub.quote(ticker).get("market_cap")),
    }
