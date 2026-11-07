"""
🧰 TOOLS - Herramientas que el copiloto puede invocar (function calling)
========================================================================

Cada herramienta = esquema JSON (lo que ve el LLM) + función Python (lo que se ejecuta).
El LLM decide qué herramienta llamar; nosotros ejecutamos y le devolvemos el resultado.
Así los números SIEMPRE salen de datos reales y no de la "memoria" del modelo.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from .data_hub import DataHub
from . import valuation

logger = logging.getLogger(__name__)

MAX_RESULT_CHARS = 6000  # recorte para no saturar el contexto del LLM


@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]

    def schema(self) -> Dict[str, Any]:
        return {"type": "function",
                "function": {"name": self.name, "description": self.description, "parameters": self.parameters}}


def _ticker_param(desc: str = "Ticker bursátil, p.ej. AAPL, MSFT, SAN.MC, ITX.MC") -> Dict:
    return {"type": "string", "description": desc}


def to_jsonable(obj: Any) -> Any:
    """Convierte DataFrames y tipos numpy a algo serializable y compacto."""
    if isinstance(obj, pd.DataFrame):
        if obj.empty:
            return {"error": "Sin datos"}
        return json.loads(obj.to_json(orient="index", double_precision=4))
    if isinstance(obj, pd.Series):
        return json.loads(obj.to_json(double_precision=4))
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    return obj


def serialize(result: Any) -> str:
    text = json.dumps(to_jsonable(result), ensure_ascii=False, default=str)
    if len(text) > MAX_RESULT_CHARS:
        text = text[:MAX_RESULT_CHARS] + '… [recortado]"'
    return text


class ToolRegistry:
    """Catálogo de herramientas sobre un DataHub (y opcionalmente la biblioteca)."""

    def __init__(self, hub: Optional[DataHub] = None, library: Any = None):
        self.hub = hub or DataHub()
        self.library = library
        self._tools: Dict[str, Tool] = {}
        self._register_defaults()

    # ------------------------------------------------------------- registro
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def schemas(self) -> List[Dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]

    @property
    def names(self) -> List[str]:
        return list(self._tools)

    def call(self, name: str, arguments: Dict[str, Any] | str) -> Any:
        if isinstance(arguments, str):
            arguments = json.loads(arguments or "{}")
        tool = self._tools.get(name)
        if tool is None:
            return {"error": f"Herramienta desconocida: {name}"}
        try:
            return tool.func(**arguments)
        except Exception as exc:
            logger.exception("Error en herramienta %s", name)
            return {"error": f"{type(exc).__name__}: {exc}"}

    # ----------------------------------------------------------- catálogo
    def _register_defaults(self) -> None:
        h = self.hub
        T = lambda **kw: self.register(Tool(**kw))
        one_ticker = {"type": "object", "properties": {"ticker": _ticker_param()}, "required": ["ticker"]}

        T(name="get_quote", description="Precio actual, capitalización, beta y distancia al máximo de 52 semanas.",
          parameters=one_ticker, func=h.quote)

        T(name="get_company_profile", description="Descripción del negocio, sector, industria, país y empleados.",
          parameters=one_ticker, func=h.profile)

        T(name="get_financial_statement",
          description="Estado financiero histórico: cuenta de resultados, balance o flujos de caja.",
          parameters={"type": "object", "properties": {
              "ticker": _ticker_param(),
              "statement": {"type": "string", "enum": ["income", "balance", "cashflow"]},
              "period": {"type": "string", "enum": ["annual", "quarterly"], "default": "annual"},
              "limit": {"type": "integer", "default": 4, "description": "Nº de periodos"}},
              "required": ["ticker", "statement"]},
          func=lambda ticker, statement, period="annual", limit=4: h.financial_statement(ticker, statement, period, limit))

        T(name="get_key_ratios",
          description="Ratios de valoración (PER, EV/EBITDA, FCF yield), márgenes, ROE, deuda y crecimiento.",
          parameters=one_ticker, func=h.key_ratios)

        T(name="get_price_performance",
          description="Rentabilidad 1m/3m/6m/1a/YTD, volatilidad anual y máxima caída del último año.",
          parameters=one_ticker, func=h.price_performance)

        T(name="get_analyst_view", description="Consenso de analistas: recomendación y precio objetivo.",
          parameters=one_ticker, func=h.analyst_view)

        T(name="get_news", description="Titulares recientes sobre la empresa.",
          parameters={"type": "object", "properties": {"ticker": _ticker_param(),
                                                      "limit": {"type": "integer", "default": 6}},
                      "required": ["ticker"]},
          func=lambda ticker, limit=6: h.news(ticker, limit))

        T(name="get_sec_filings", description="Últimos documentos oficiales en la SEC (10-K, 10-Q, 8-K). Solo EE.UU.",
          parameters=one_ticker, func=lambda ticker: h.sec_filings(ticker))

        T(name="get_sec_fundamentals",
          description="Ingresos, beneficio neto y BPA anuales oficiales (XBRL de la SEC) para contrastar datos. Solo EE.UU.",
          parameters=one_ticker, func=lambda ticker: h.sec_fundamentals(ticker))

        T(name="compare_companies", description="Tabla comparativa de valoración, rentabilidad y crecimiento entre 2-8 empresas.",
          parameters={"type": "object", "properties": {
              "tickers": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 8}},
              "required": ["tickers"]},
          func=lambda tickers: h.compare(tickers))

        T(name="run_dcf_valuation",
          description=("DCF de dos etapas sobre FCF con DCF inverso y tabla de sensibilidad. "
                       "Si no se pasan supuestos se estiman de los datos (CAGR de ingresos, CAPM)."),
          parameters={"type": "object", "properties": {
              "ticker": _ticker_param(),
              "growth": {"type": "number", "description": "Crecimiento anual del FCF, p.ej. 0.08"},
              "discount_rate": {"type": "number", "description": "Tasa de descuento, p.ej. 0.09"},
              "terminal_growth": {"type": "number", "default": 0.025}},
              "required": ["ticker"]},
          func=lambda ticker, growth=None, discount_rate=None, terminal_growth=0.025:
              valuation.auto_valuation(h, ticker, growth, discount_rate, terminal_growth))

        T(name="get_quality_scores",
          description="Piotroski F-Score (calidad contable, 0-9) y Altman Z-Score (riesgo de quiebra).",
          parameters=one_ticker, func=lambda ticker: valuation.quality_scores(h, ticker))

        if self.library is not None:
            T(name="search_investment_library",
              description="Busca principios en la biblioteca de inversión del usuario (Buffett, Graham, etc.).",
              parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
              func=self._search_library)

    def _search_library(self, query: str) -> Any:
        try:
            if hasattr(self.library, "get_wisdom_for_topic"):
                return {"results": self.library.get_wisdom_for_topic(query)}
            return {"results": [str(r) for r in self.library.search(query)]}
        except Exception as exc:
            return {"error": f"Biblioteca no disponible: {exc}"}
