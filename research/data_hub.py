"""
🛰️ DATA HUB - Capa de datos unificada del Sindicato V8
=======================================================

Una sola puerta de entrada a los datos de mercado, pensada para que la usen
tanto la interfaz como los agentes de IA (copiloto e informes automáticos).

Idea de diseño (propia): "una función = una pregunta financiera", con salidas
pequeñas y serializables (dict / DataFrame) para poder pasarlas a un LLM.

Fuentes:
- yfinance (Yahoo Finance)      → cotización, perfil, estados financieros, noticias
- SEC EDGAR (API pública, gratis) → filings y datos XBRL oficiales (solo EE.UU.)

No depende de Streamlit ni de OpenBB, así que funciona en Streamlit Cloud
(Python 3.13), en Colab y en tests.
"""

from __future__ import annotations

import logging
import math
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

SEC_BASE = "https://data.sec.gov"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


# ============================================================================
# Utilidades
# ============================================================================

def _ttl_cache(seconds: int = 900) -> Callable:
    """Caché en memoria con caducidad, por instancia y argumentos."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            hit = self._cache.get(key)
            now = time.time()
            if hit and now - hit[0] < seconds:
                return hit[1]
            value = func(self, *args, **kwargs)
            self._cache[key] = (now, value)
            return value
        return wrapper
    return decorator


def _num(value: Any) -> Optional[float]:
    """Convierte a float limpio (None si no es un número válido)."""
    try:
        if value is None:
            return None
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _row(df: Optional[pd.DataFrame], *names: str) -> Optional[pd.Series]:
    """Devuelve la primera fila que exista entre varios nombres posibles."""
    if df is None or df.empty:
        return None
    for name in names:
        if name in df.index:
            return df.loc[name]
    return None


def _first(series: Optional[pd.Series], pos: int = 0) -> Optional[float]:
    if series is None or len(series) <= pos:
        return None
    return _num(series.iloc[pos])


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b in (None, 0):
        return None
    return a / b


def _round(value: Optional[float], nd: int = 4) -> Optional[float]:
    return None if value is None else round(value, nd)


@dataclass
class CompanySnapshot:
    """Foto completa de una empresa, lista para un informe o un LLM."""
    ticker: str
    as_of: str
    quote: Dict[str, Any] = field(default_factory=dict)
    profile: Dict[str, Any] = field(default_factory=dict)
    ratios: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    analyst: Dict[str, Any] = field(default_factory=dict)
    income: Optional[pd.DataFrame] = None
    balance: Optional[pd.DataFrame] = None
    cashflow: Optional[pd.DataFrame] = None
    news: List[Dict[str, Any]] = field(default_factory=list)
    filings: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# DataHub
# ============================================================================

class DataHub:
    """
    Fachada de datos financieros.

    Ejemplo:
        hub = DataHub()
        hub.quote("AAPL")
        hub.financial_statement("AAPL", "income", period="annual")
        hub.key_ratios("AAPL")
    """

    STATEMENTS = {
        "income": ("income_stmt", "quarterly_income_stmt"),
        "balance": ("balance_sheet", "quarterly_balance_sheet"),
        "cashflow": ("cashflow", "quarterly_cashflow"),
    }

    def __init__(self, sec_user_agent: Optional[str] = None, ticker_factory: Optional[Callable] = None,
                 http_get: Optional[Callable] = None):
        """
        Args:
            sec_user_agent: la SEC exige un User-Agent con contacto
                (variable SEC_USER_AGENT, p.ej. "Sindicato V8 tu@email.com").
            ticker_factory: inyectable para tests (por defecto yfinance.Ticker).
            http_get: inyectable para tests (por defecto requests.get).
        """
        self._cache: Dict[Any, Any] = {}
        self.sec_user_agent = sec_user_agent or os.getenv("SEC_USER_AGENT", "SindicatoV8 research contact@example.com")
        self._ticker_factory = ticker_factory
        self._http_get = http_get
        self._cik_map: Optional[Dict[str, str]] = None

    # ------------------------------------------------------------------ infra
    def _ticker(self, ticker: str):
        if self._ticker_factory is None:
            import yfinance as yf
            self._ticker_factory = yf.Ticker
        return self._ticker_factory(ticker.upper().strip())

    def _get_json(self, url: str) -> Optional[Dict]:
        try:
            if self._http_get is None:
                import requests
                self._http_get = requests.get
            resp = self._http_get(url, headers={"User-Agent": self.sec_user_agent}, timeout=15)
            if getattr(resp, "status_code", 200) != 200:
                logger.warning("HTTP %s en %s", resp.status_code, url)
                return None
            return resp.json()
        except Exception as exc:  # red caída, JSON inválido...
            logger.warning("Error leyendo %s: %s", url, exc)
            return None

    @_ttl_cache(600)
    def _info(self, ticker: str) -> Dict[str, Any]:
        try:
            return dict(self._ticker(ticker).info or {})
        except Exception as exc:
            logger.warning("yfinance info falló para %s: %s", ticker, exc)
            return {}

    # --------------------------------------------------------------- mercado
    def quote(self, ticker: str) -> Dict[str, Any]:
        """Precio actual, capitalización y rango de 52 semanas."""
        i = self._info(ticker)
        price = _num(i.get("currentPrice") or i.get("regularMarketPrice"))
        high, low = _num(i.get("fiftyTwoWeekHigh")), _num(i.get("fiftyTwoWeekLow"))
        return {
            "ticker": ticker.upper(),
            "name": i.get("longName") or i.get("shortName"),
            "price": price,
            "currency": i.get("currency"),
            "change_pct": _round(_num(i.get("regularMarketChangePercent")), 2),
            "market_cap": _num(i.get("marketCap")),
            "week52_high": high,
            "week52_low": low,
            "pct_from_52w_high": _round(_safe_div((price or 0) - (high or 0), high) if price and high else None),
            "beta": _num(i.get("beta")),
            "source": "Yahoo Finance",
        }

    def profile(self, ticker: str) -> Dict[str, Any]:
        """Descripción del negocio, sector, país y empleados."""
        i = self._info(ticker)
        summary = i.get("longBusinessSummary") or ""
        return {
            "ticker": ticker.upper(),
            "name": i.get("longName") or i.get("shortName"),
            "sector": i.get("sector"),
            "industry": i.get("industry"),
            "country": i.get("country"),
            "employees": i.get("fullTimeEmployees"),
            "website": i.get("website"),
            "exchange": i.get("exchange"),
            "summary": summary[:1500],
            "source": "Yahoo Finance",
        }

    @_ttl_cache(900)
    def price_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        try:
            df = self._ticker(ticker).history(period=period, interval=interval)
            return df if df is not None else pd.DataFrame()
        except Exception as exc:
            logger.warning("history falló para %s: %s", ticker, exc)
            return pd.DataFrame()

    def price_performance(self, ticker: str) -> Dict[str, Any]:
        """Rentabilidades por periodo, volatilidad anualizada y máxima caída (1 año)."""
        df = self.price_history(ticker, period="1y")
        if df.empty or "Close" not in df:
            return {"ticker": ticker.upper(), "error": "Sin histórico de precios"}
        close = df["Close"].dropna()
        last = close.iloc[-1]

        def ret(days: int) -> Optional[float]:
            if len(close) <= days:
                return None
            return _round(last / close.iloc[-days - 1] - 1)

        daily = close.pct_change().dropna()
        drawdown = (close / close.cummax() - 1).min()
        idx = close.index
        ytd_base = close[idx >= pd.Timestamp(year=idx[-1].year, month=1, day=1, tz=idx.tz)]
        return {
            "ticker": ticker.upper(),
            "return_1m": ret(21),
            "return_3m": ret(63),
            "return_6m": ret(126),
            "return_1y": _round(last / close.iloc[0] - 1),
            "return_ytd": _round(last / ytd_base.iloc[0] - 1) if len(ytd_base) else None,
            "volatility_annual": _round(float(daily.std() * math.sqrt(252))) if len(daily) > 5 else None,
            "max_drawdown_1y": _round(float(drawdown)),
            "last_close": _round(float(last), 2),
            "source": "Yahoo Finance",
        }

    # ------------------------------------------------------------ contables
    @_ttl_cache(3600)
    def financial_statement(self, ticker: str, statement: str = "income", period: str = "annual",
                            limit: int = 4) -> pd.DataFrame:
        """
        Estado financiero (filas = partidas, columnas = fechas, más reciente primero).
        statement: income | balance | cashflow ; period: annual | quarterly
        """
        if statement not in self.STATEMENTS:
            raise ValueError(f"statement debe ser uno de {list(self.STATEMENTS)}")
        attr = self.STATEMENTS[statement][0 if period == "annual" else 1]
        try:
            df = getattr(self._ticker(ticker), attr)
        except Exception as exc:
            logger.warning("%s falló para %s: %s", attr, ticker, exc)
            return pd.DataFrame()
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.sort_index(axis=1, ascending=False).iloc[:, :limit]
        df.columns = [c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c) for c in df.columns]
        return df

    def key_ratios(self, ticker: str) -> Dict[str, Any]:
        """
        Ratios de valoración, rentabilidad, solidez y crecimiento.
        Combina los que da Yahoo con los calculados desde los estados financieros.
        """
        i = self._info(ticker)
        inc = self.financial_statement(ticker, "income")
        bal = self.financial_statement(ticker, "balance")
        cf = self.financial_statement(ticker, "cashflow")

        revenue = _row(inc, "Total Revenue", "Operating Revenue")
        net_income = _row(inc, "Net Income", "Net Income Common Stockholders")
        op_income = _row(inc, "Operating Income", "EBIT")
        gross = _row(inc, "Gross Profit")
        fcf = _row(cf, "Free Cash Flow")
        ocf = _row(cf, "Operating Cash Flow")
        equity = _row(bal, "Stockholders Equity", "Common Stock Equity")
        debt = _row(bal, "Total Debt")
        cash = _row(bal, "Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments")
        assets = _row(bal, "Total Assets")

        rev0, rev1 = _first(revenue), _first(revenue, 1)
        ni0 = _first(net_income)
        fcf0 = _first(fcf)
        mcap = _num(i.get("marketCap"))

        rev_cagr = None
        if revenue is not None and len(revenue.dropna()) >= 3:
            r = revenue.dropna()
            years = len(r) - 1
            if _num(r.iloc[-1]) and _num(r.iloc[0]) and r.iloc[-1] > 0 and r.iloc[0] > 0:
                rev_cagr = (r.iloc[0] / r.iloc[-1]) ** (1 / years) - 1

        return {
            "ticker": ticker.upper(),
            "valuation": {
                "pe_trailing": _round(_num(i.get("trailingPE")), 2),
                "pe_forward": _round(_num(i.get("forwardPE")), 2),
                "price_to_book": _round(_num(i.get("priceToBook")), 2),
                "price_to_sales": _round(_num(i.get("priceToSalesTrailing12Months")), 2),
                "ev_to_ebitda": _round(_num(i.get("enterpriseToEbitda")), 2),
                "fcf_yield": _round(_safe_div(fcf0, mcap)),
                "dividend_yield": _round(_num(i.get("dividendYield")), 4),
            },
            "profitability": {
                "gross_margin": _round(_safe_div(_first(gross), rev0) or _num(i.get("grossMargins"))),
                "operating_margin": _round(_safe_div(_first(op_income), rev0) or _num(i.get("operatingMargins"))),
                "net_margin": _round(_safe_div(ni0, rev0) or _num(i.get("profitMargins"))),
                "roe": _round(_safe_div(ni0, _first(equity)) or _num(i.get("returnOnEquity"))),
                "roa": _round(_safe_div(ni0, _first(assets)) or _num(i.get("returnOnAssets"))),
                "fcf_margin": _round(_safe_div(fcf0, rev0)),
                "cash_conversion": _round(_safe_div(_first(ocf), ni0)),
            },
            "balance_sheet": {
                "total_debt": _first(debt) or _num(i.get("totalDebt")),
                "cash": _first(cash) or _num(i.get("totalCash")),
                "net_debt": (_first(debt) or 0) - (_first(cash) or 0) if (debt is not None or cash is not None) else None,
                "debt_to_equity": _round(_safe_div(_first(debt), _first(equity))),
                "current_ratio": _round(_num(i.get("currentRatio")), 2),
            },
            "growth": {
                "revenue_growth_yoy": _round(_safe_div((rev0 or 0) - (rev1 or 0), rev1) if rev0 and rev1 else None),
                "revenue_cagr": _round(rev_cagr),
                "revenue_cagr_years": (len(revenue.dropna()) - 1) if revenue is not None else None,
                "earnings_growth_yahoo": _round(_num(i.get("earningsGrowth"))),
            },
            "units": "ratios en tanto por uno (0.25 = 25%); importes en la divisa de los estados",
            "source": "Yahoo Finance (calculado por Sindicato V8)",
        }

    # ------------------------------------------------------------- consenso
    def analyst_view(self, ticker: str) -> Dict[str, Any]:
        """Precio objetivo y recomendación media de analistas."""
        i = self._info(ticker)
        price = _num(i.get("currentPrice") or i.get("regularMarketPrice"))
        target = _num(i.get("targetMeanPrice"))
        return {
            "ticker": ticker.upper(),
            "recommendation": i.get("recommendationKey"),
            "recommendation_mean": _num(i.get("recommendationMean")),
            "analysts": i.get("numberOfAnalystOpinions"),
            "target_mean": target,
            "target_high": _num(i.get("targetHighPrice")),
            "target_low": _num(i.get("targetLowPrice")),
            "upside_to_mean_target": _round(_safe_div((target or 0) - (price or 0), price) if target and price else None),
            "source": "Yahoo Finance",
        }

    def news(self, ticker: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Titulares recientes (compatible con formato antiguo y nuevo de yfinance)."""
        try:
            raw = self._ticker(ticker).news or []
        except Exception as exc:
            logger.warning("news falló para %s: %s", ticker, exc)
            return []
        items = []
        for n in raw[:limit]:
            c = n.get("content", n)
            ts = c.get("pubDate") or c.get("providerPublishTime")
            if isinstance(ts, (int, float)):
                ts = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            elif isinstance(ts, str):
                ts = ts[:10]
            provider = c.get("provider")
            url = c.get("canonicalUrl") or c.get("clickThroughUrl") or c.get("link")
            items.append({
                "title": c.get("title"),
                "date": ts,
                "publisher": provider.get("displayName") if isinstance(provider, dict) else c.get("publisher"),
                "url": url.get("url") if isinstance(url, dict) else url,
                "summary": (c.get("summary") or "")[:300],
            })
        return items

    # ----------------------------------------------------------------- SEC
    def _cik(self, ticker: str) -> Optional[str]:
        if self._cik_map is None:
            data = self._get_json(SEC_TICKERS_URL) or {}
            self._cik_map = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in data.values()
                             if isinstance(v, dict) and "ticker" in v}
        return self._cik_map.get(ticker.upper())

    @_ttl_cache(3600)
    def sec_filings(self, ticker: str, forms: tuple = ("10-K", "10-Q", "8-K"), limit: int = 10) -> List[Dict[str, Any]]:
        """Últimos documentos oficiales presentados ante la SEC (solo empresas de EE.UU.)."""
        cik = self._cik(ticker)
        if not cik:
            return []
        data = self._get_json(f"{SEC_BASE}/submissions/CIK{cik}.json")
        if not data:
            return []
        recent = data.get("filings", {}).get("recent", {})
        out = []
        for form, date, acc, doc in zip(recent.get("form", []), recent.get("filingDate", []),
                                        recent.get("accessionNumber", []), recent.get("primaryDocument", [])):
            if form in forms:
                out.append({
                    "form": form,
                    "date": date,
                    "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}",
                })
            if len(out) >= limit:
                break
        return out

    @_ttl_cache(3600)
    def sec_fundamentals(self, ticker: str, concepts: tuple = ("Revenues", "NetIncomeLoss", "EarningsPerShareDiluted"),
                         years: int = 5) -> Dict[str, Any]:
        """
        Cifras anuales oficiales (XBRL de los 10-K). Útil para contrastar con Yahoo.
        Devuelve {concepto: [{"year":..., "value":...}, ...]}
        """
        cik = self._cik(ticker)
        if not cik:
            return {"ticker": ticker.upper(), "error": "Ticker sin CIK en la SEC (¿empresa no estadounidense?)"}
        data = self._get_json(f"{SEC_BASE}/api/xbrl/companyfacts/CIK{cik}.json")
        if not data:
            return {"ticker": ticker.upper(), "error": "SEC no disponible"}
        gaap = data.get("facts", {}).get("us-gaap", {})
        aliases = {"Revenues": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]}
        result: Dict[str, Any] = {"ticker": ticker.upper(), "source": "SEC EDGAR XBRL"}
        for concept in concepts:
            for name in aliases.get(concept, [concept]):
                units = gaap.get(name, {}).get("units", {})
                if not units:
                    continue
                series = next(iter(units.values()))
                annual = {}
                for f in series:
                    if f.get("form") == "10-K" and f.get("fp") == "FY" and f.get("fy"):
                        annual[f["fy"]] = f.get("val")  # la última presentación de cada año gana
                if annual:
                    result[concept] = [{"year": y, "value": annual[y]} for y in sorted(annual)[-years:]]
                    break
        return result

    # ------------------------------------------------------------ compuestos
    def compare(self, tickers: List[str]) -> pd.DataFrame:
        """Tabla comparativa de varias empresas (filas = empresas)."""
        rows = []
        for t in tickers[:8]:
            q, r = self.quote(t), self.key_ratios(t)
            rows.append({
                "ticker": t.upper(),
                "name": q.get("name"),
                "market_cap": q.get("market_cap"),
                "pe_forward": r["valuation"]["pe_forward"],
                "ev_to_ebitda": r["valuation"]["ev_to_ebitda"],
                "fcf_yield": r["valuation"]["fcf_yield"],
                "operating_margin": r["profitability"]["operating_margin"],
                "roe": r["profitability"]["roe"],
                "revenue_growth_yoy": r["growth"]["revenue_growth_yoy"],
                "debt_to_equity": r["balance_sheet"]["debt_to_equity"],
            })
        return pd.DataFrame(rows)

    def snapshot(self, ticker: str, include_sec: bool = True) -> CompanySnapshot:
        """Recoge todo lo necesario para un informe en una sola llamada."""
        t = ticker.upper().strip()
        return CompanySnapshot(
            ticker=t,
            as_of=datetime.now().strftime("%Y-%m-%d %H:%M"),
            quote=self.quote(t),
            profile=self.profile(t),
            ratios=self.key_ratios(t),
            performance=self.price_performance(t),
            analyst=self.analyst_view(t),
            income=self.financial_statement(t, "income"),
            balance=self.financial_statement(t, "balance"),
            cashflow=self.financial_statement(t, "cashflow"),
            news=self.news(t, limit=6),
            filings=self.sec_filings(t, limit=5) if include_sec else [],
        )
