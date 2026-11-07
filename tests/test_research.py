"""
Tests del paquete research con datos simulados (sin red ni API keys).
Ejecutar:  pytest -q
"""

import json
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research import DataHub, ToolRegistry, FinancialCopilot, EquityReportGenerator  # noqa: E402
from research import valuation  # noqa: E402

YEARS = pd.to_datetime(["2025-12-31", "2024-12-31", "2023-12-31", "2022-12-31"])


class FakeTicker:
    """Imita la interfaz de yfinance.Ticker con cifras coherentes."""

    def __init__(self, symbol):
        self.symbol = symbol
        self.info = {
            "longName": "Acme Corp", "currentPrice": 100.0, "currency": "USD", "marketCap": 100e9,
            "sharesOutstanding": 1e9, "beta": 1.1, "fiftyTwoWeekHigh": 120.0, "fiftyTwoWeekLow": 80.0,
            "trailingPE": 25.0, "forwardPE": 22.0, "enterpriseToEbitda": 15.0, "priceToBook": 6.0,
            "sector": "Technology", "industry": "Software", "country": "United States",
            "longBusinessSummary": "Acme vende software.", "targetMeanPrice": 115.0,
            "recommendationKey": "buy", "numberOfAnalystOpinions": 20,
        }
        self.income_stmt = pd.DataFrame({
            "Total Revenue": [20e9, 18e9, 16e9, 14e9], "Gross Profit": [14e9, 12.4e9, 10.8e9, 9.2e9],
            "Operating Income": [5e9, 4.3e9, 3.6e9, 3e9], "EBIT": [5e9, 4.3e9, 3.6e9, 3e9],
            "Net Income": [4e9, 3.4e9, 2.9e9, 2.4e9], "Diluted EPS": [4.0, 3.4, 2.9, 2.4],
        }, index=YEARS).T
        self.balance_sheet = pd.DataFrame({
            "Total Assets": [40e9, 37e9, 34e9, 31e9], "Total Debt": [8e9, 9e9, 9e9, 10e9],
            "Cash And Cash Equivalents": [6e9, 5e9, 4e9, 3e9], "Stockholders Equity": [20e9, 18e9, 16e9, 14e9],
            "Long Term Debt": [7e9, 8e9, 8e9, 9e9], "Current Assets": [15e9, 13e9, 12e9, 11e9],
            "Current Liabilities": [8e9, 8e9, 8e9, 8e9], "Ordinary Shares Number": [1e9, 1.01e9, 1.02e9, 1.03e9],
            "Total Liabilities Net Minority Interest": [20e9, 19e9, 18e9, 17e9],
            "Working Capital": [7e9, 5e9, 4e9, 3e9], "Retained Earnings": [10e9, 8e9, 6e9, 4e9],
        }, index=YEARS).T
        self.cashflow = pd.DataFrame({
            "Operating Cash Flow": [5.5e9, 4.8e9, 4e9, 3.4e9], "Capital Expenditure": [-1e9, -0.9e9, -0.8e9, -0.7e9],
            "Free Cash Flow": [4.5e9, 3.9e9, 3.2e9, 2.7e9],
        }, index=YEARS).T
        self.quarterly_income_stmt = self.income_stmt
        self.quarterly_balance_sheet = self.balance_sheet
        self.quarterly_cashflow = self.cashflow
        self.news = [{"content": {"title": "Acme bate previsiones", "pubDate": "2026-11-01T10:00:00Z",
                                  "provider": {"displayName": "Reuters"},
                                  "canonicalUrl": {"url": "https://example.com/n1"}}}]

    def history(self, period="1y", interval="1d"):
        idx = pd.bdate_range(end="2026-11-06", periods=252, tz="America/New_York")
        prices = np.linspace(80, 100, 252) + np.sin(np.arange(252) / 5)
        return pd.DataFrame({"Close": prices}, index=idx)


def fake_http_get(url, headers=None, timeout=None):
    if "company_tickers" in url:
        data = {"0": {"ticker": "ACME", "cik_str": 123}}
    elif "submissions" in url:
        data = {"filings": {"recent": {"form": ["10-K", "4", "10-Q"], "filingDate": ["2026-02-01", "2026-01-05", "2025-11-01"],
                                       "accessionNumber": ["0001-26-000001", "x", "0001-25-000009"],
                                       "primaryDocument": ["acme10k.htm", "f4.xml", "acme10q.htm"]}}}
    else:
        data = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
            {"form": "10-K", "fp": "FY", "fy": 2024, "val": 18e9},
            {"form": "10-K", "fp": "FY", "fy": 2025, "val": 20e9}]}}}}}
    return SimpleNamespace(status_code=200, json=lambda: data)


@pytest.fixture
def hub():
    return DataHub(ticker_factory=FakeTicker, http_get=fake_http_get)


# ------------------------------------------------------------------ DataHub
def test_quote_and_ratios(hub):
    q = hub.quote("acme")
    assert q["price"] == 100.0 and q["ticker"] == "ACME"
    r = hub.key_ratios("ACME")
    assert r["profitability"]["operating_margin"] == pytest.approx(0.25)
    assert r["growth"]["revenue_growth_yoy"] == pytest.approx(20 / 18 - 1, rel=1e-3)
    assert r["balance_sheet"]["net_debt"] == pytest.approx(2e9)
    assert r["valuation"]["fcf_yield"] == pytest.approx(0.045)


def test_statement_order_and_limit(hub):
    df = hub.financial_statement("ACME", "income", limit=2)
    assert list(df.columns) == ["2025-12-31", "2024-12-31"]


def test_performance(hub):
    p = hub.price_performance("ACME")
    assert p["return_1y"] > 0 and p["max_drawdown_1y"] <= 0


def test_news_new_format(hub):
    n = hub.news("ACME")
    assert n[0]["publisher"] == "Reuters" and n[0]["date"] == "2026-11-01"


def test_sec(hub):
    f = hub.sec_filings("ACME")
    assert [x["form"] for x in f] == ["10-K", "10-Q"]
    assert f[0]["url"].endswith("/123/000126000001/acme10k.htm")
    facts = hub.sec_fundamentals("ACME", concepts=("Revenues",))
    assert facts["Revenues"][-1] == {"year": 2025, "value": 20e9}


# ---------------------------------------------------------------- Valuation
def test_dcf_math():
    res = valuation.dcf(100, growth=0.0, years=1, terminal_growth=0.0, discount_rate=0.10)
    # flujo plano de 100 a perpetuidad al 10 % = 1000
    assert res.enterprise_value == pytest.approx(1000, rel=1e-6)


def test_reverse_dcf_roundtrip():
    base = valuation.dcf(1000, 0.07, 5, 0.025, 0.09, net_debt=500, shares=100)
    implied = valuation.reverse_dcf(base.fair_value_per_share, 100, 1000, 500, 5, 0.025, 0.09)
    assert implied == pytest.approx(0.07, abs=1e-3)


def test_scores(hub):
    q = valuation.quality_scores(hub, "ACME")
    assert q["piotroski"]["score"] >= 7
    assert q["altman_z"]["zone"] == "Segura"


def test_auto_valuation(hub):
    v = valuation.auto_valuation(hub, "ACME")
    assert v["applicable"] and v["fair_value_per_share"] > 0
    assert v["implied_growth_at_price"] is not None


# -------------------------------------------------------------------- Tools
def test_tools_serializable(hub):
    reg = ToolRegistry(hub)
    assert "run_dcf_valuation" in reg.names and len(reg.schemas()) == len(reg.names)
    for name, args in [("get_key_ratios", {"ticker": "ACME"}),
                       ("get_financial_statement", {"ticker": "ACME", "statement": "cashflow"}),
                       ("compare_companies", {"tickers": ["ACME", "ACME"]}),
                       ("run_dcf_valuation", {"ticker": "ACME", "growth": 0.05})]:
        from research.tools import serialize
        json.loads(serialize(reg.call(name, args)).replace('… [recortado]"', ""))
    assert "error" in reg.call("no_existe", {})


# ------------------------------------------------------------------ Copilot
class FakeLLM:
    """Primero pide una herramienta, luego responde usando su resultado."""

    def __init__(self):
        self.calls = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            call = SimpleNamespace(id="c1", function=SimpleNamespace(name="get_quote", arguments='{"ticker":"ACME"}'))
            msg = SimpleNamespace(content=None, tool_calls=[call])
        else:
            tool_msg = [m for m in kwargs["messages"] if m["role"] == "tool"][-1]
            price = json.loads(tool_msg["content"])["price"]
            msg = SimpleNamespace(content=f"Acme cotiza a {price} USD (Yahoo Finance).", tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def test_copilot_tool_loop(hub):
    seen = []
    cp = FinancialCopilot(ToolRegistry(hub), client=FakeLLM())
    reply = cp.ask("¿A cuánto cotiza?", focus_ticker="ACME", on_tool_call=lambda n, a: seen.append(n))
    assert "100.0" in reply.content
    assert seen == ["get_quote"] and reply.tool_calls[0].name == "get_quote"
    assert cp.history[-1]["role"] == "assistant"


# ------------------------------------------------------------------- Report
def test_report_data_only(hub):
    rep = EquityReportGenerator(hub, use_ai=False).generate("ACME")
    md = rep.to_markdown()
    assert "Acme Corp (ACME)" in md and "Piotroski" in md and "Sensibilidad DCF" in md
    assert "<table>" in rep.to_html() or "<table" in rep.to_html()
    assert not rep.ai_generated


def test_report_with_ai(hub):
    sections = {k: f"Texto {k}" for k in ["resumen", "negocio", "financiero", "valoracion", "riesgos", "vigilar"]}
    msg = SimpleNamespace(content=json.dumps(sections))
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **kw: SimpleNamespace(choices=[SimpleNamespace(message=msg)]))))
    rep = EquityReportGenerator(hub, client=client).generate("ACME")
    assert rep.ai_generated and rep.sections["valoracion"] == "Texto valoracion"


# --------------------------------------------------------- sin red / sin datos
class EmptyTicker:
    def __init__(self, s):
        self.info, self.news = {}, []
        self.income_stmt = self.balance_sheet = self.cashflow = pd.DataFrame()
        self.quarterly_income_stmt = self.quarterly_balance_sheet = self.quarterly_cashflow = pd.DataFrame()

    def history(self, **kw):
        return pd.DataFrame()


def down_http_get(url, headers=None, timeout=None):
    raise ConnectionError("sin red")


def test_no_data_is_reported_honestly():
    from research import NoMarketData
    h = DataHub(ticker_factory=EmptyTicker, http_get=down_http_get)
    assert h.sec_fundamentals("MSFT")["error"] == "SEC no disponible ahora mismo"
    assert "error" in h.sec_filings("MSFT")[0]
    assert valuation.quality_scores(h, "MSFT")["piotroski"]["score"] is None
    with pytest.raises(NoMarketData):
        EquityReportGenerator(h, use_ai=False).generate("MSFT")


def test_sec_retries_after_failure():
    state = {"up": False}

    def flaky(url, headers=None, timeout=None):
        if not state["up"]:
            raise ConnectionError
        return fake_http_get(url)

    h = DataHub(ticker_factory=FakeTicker, http_get=flaky)
    assert "error" in h.sec_filings("ACME")[0]
    state["up"] = True
    assert h.sec_filings("ACME")[0]["form"] == "10-K"
