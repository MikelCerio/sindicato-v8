"""
📑 INFORME AUTOMÁTICO DE EMPRESA (equity research)
==================================================

Pipeline en 3 fases:
  1. DATOS      → DataHub.snapshot() + valoración + scores (determinista, sin IA)
  2. REDACCIÓN  → un LLM escribe cada sección SOLO con los datos de la fase 1
  3. MAQUETA    → Markdown + HTML descargable con tablas de apoyo

Si no hay API key de OpenAI, el informe se genera igualmente con los datos
y comentarios automáticos basados en reglas (modo "solo datos").
"""

from __future__ import annotations

import html
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from .data_hub import CompanySnapshot, DataHub, NoMarketData
from . import valuation
from .tools import to_jsonable

logger = logging.getLogger(__name__)

SECTIONS = [
    ("resumen", "Resumen ejecutivo"),
    ("negocio", "Negocio y posicionamiento"),
    ("financiero", "Análisis financiero"),
    ("valoracion", "Valoración"),
    ("riesgos", "Calidad y riesgos"),
    ("vigilar", "Qué vigilar"),
]

WRITER_PROMPT = """Eres un analista de equity research. Redacta un informe en español sobre {name} ({ticker}) \
usando EXCLUSIVAMENTE los datos JSON que siguen. No inventes cifras; si falta un dato, dilo.
Ratios en tanto por uno (0.25 = 25 %): exprésalos en %. Importes grandes en miles de millones o millones.
No des recomendaciones de compra/venta personalizadas; da una valoración razonada \
(atractiva / razonable / exigente) y explica por qué.

Devuelve un objeto JSON con estas claves (texto markdown en cada una, 80-200 palabras):
- "resumen": tesis en 3-4 viñetas + conclusión de valoración
- "negocio": qué hace, cómo gana dinero, posición competitiva
- "financiero": crecimiento, márgenes, generación de caja y balance, con cifras
- "valoracion": múltiplos, DCF (supuestos y sensibilidad), consenso de analistas
- "riesgos": Piotroski, Altman, volatilidad/caídas y riesgos de negocio
- "vigilar": 3-5 indicadores o eventos concretos que confirmarían o romperían la tesis

DATOS:
{data}"""


@dataclass
class EquityReport:
    ticker: str
    name: str
    as_of: str
    sections: Dict[str, str]
    metrics: Dict[str, Any]
    tables: Dict[str, pd.DataFrame] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    ai_generated: bool = False

    # ---------------------------------------------------------------- salida
    def to_markdown(self) -> str:
        out = [f"# {self.name} ({self.ticker}) — Informe de análisis",
               f"*Generado el {self.as_of} · Sindicato V8 · "
               f"{'Redactado con IA a partir de datos' if self.ai_generated else 'Modo solo datos'}*", ""]
        out.append("## Métricas clave")
        out.append(_dict_table(self.metrics))
        for key, title in SECTIONS:
            if self.sections.get(key):
                out += ["", f"## {title}", self.sections[key]]
        for title, df in self.tables.items():
            if df is not None and not df.empty:
                out += ["", f"### {title}", _df_markdown(df)]
        out += ["", "## Fuentes", *[f"- {s}" for s in self.sources], "",
                "> Este informe es un análisis automatizado con fines educativos. "
                "No constituye asesoramiento financiero."]
        return "\n".join(out)

    def to_html(self) -> str:
        try:
            import markdown as md  # opcional
            body = md.markdown(self.to_markdown(), extensions=["tables"])
        except ImportError:
            body = _mini_markdown(self.to_markdown())
        return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>{html.escape(self.ticker)} · Informe Sindicato V8</title>
<style>
body{{font-family:Inter,Helvetica,Arial,sans-serif;max-width:900px;margin:40px auto;padding:0 24px;
color:#1a1a2e;line-height:1.6;background:#fafafa}}
h1{{border-bottom:3px solid #238636;padding-bottom:8px}} h2{{color:#0d4f1c;margin-top:32px}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0}}
th,td{{border:1px solid #ddd;padding:6px 10px;text-align:right}} th:first-child,td:first-child{{text-align:left}}
th{{background:#f0f4f0}} blockquote{{color:#666;border-left:4px solid #ccc;margin:24px 0;padding-left:12px}}
</style></head><body>{body}</body></html>"""


# ============================================================================
# Generador
# ============================================================================

class EquityReportGenerator:
    def __init__(self, hub: Optional[DataHub] = None, client: Any = None, model: Optional[str] = None,
                 use_ai: Optional[bool] = None):
        self.hub = hub or DataHub()
        self._client = client
        self.model = model or os.getenv("REPORT_MODEL", "gpt-4o")
        self.use_ai = use_ai if use_ai is not None else bool(client or os.getenv("OPENAI_API_KEY"))

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def generate(self, ticker: str, progress: Optional[Callable[[str, float], None]] = None) -> EquityReport:
        step = progress or (lambda msg, pct: None)
        t = ticker.upper().strip()

        step("Descargando datos de mercado y estados financieros…", 0.1)
        if not self.hub.has_market_data(t):
            raise NoMarketData(f"No se han podido descargar datos de {t}. Revisa el ticker "
                               f"(p.ej. ITX.MC para Inditex) o tu conexión con Yahoo Finance.")
        snap = self.hub.snapshot(t)

        step("Calculando valoración (DCF) y scores de calidad…", 0.4)
        val = valuation.auto_valuation(self.hub, t)
        quality = valuation.quality_scores(self.hub, t)

        metrics = _headline_metrics(snap, val, quality)
        data = _llm_payload(snap, val, quality)

        sections: Dict[str, str] = {}
        ai = False
        if self.use_ai:
            step("Redactando el informe con IA…", 0.6)
            try:
                sections = self._write_with_ai(snap, data)
                ai = True
            except Exception as exc:
                logger.warning("Fallo redactando con IA, uso modo solo datos: %s", exc)
        if not sections:
            sections = _rule_based_sections(snap, val, quality)

        step("Maquetando…", 0.9)
        report = EquityReport(
            ticker=t,
            name=snap.quote.get("name") or snap.profile.get("name") or t,
            as_of=snap.as_of,
            sections=sections,
            metrics=metrics,
            tables={
                "Cuenta de resultados (millones)": _summary_statement(snap.income, [
                    "Total Revenue", "Gross Profit", "Operating Income", "Net Income", "Diluted EPS"]),
                "Flujos de caja (millones)": _summary_statement(snap.cashflow, [
                    "Operating Cash Flow", "Capital Expenditure", "Free Cash Flow", "Repurchase Of Capital Stock",
                    "Cash Dividends Paid"]),
                "Balance (millones)": _summary_statement(snap.balance, [
                    "Total Assets", "Total Debt", "Cash And Cash Equivalents", "Stockholders Equity"]),
                "Sensibilidad DCF (valor por acción)": pd.DataFrame(val.get("sensitivity", {})),
            },
            sources=_sources(snap),
            ai_generated=ai,
        )
        step("Listo", 1.0)
        return report

    def _write_with_ai(self, snap: CompanySnapshot, data: Dict[str, Any]) -> Dict[str, str]:
        prompt = WRITER_PROMPT.format(name=snap.quote.get("name") or snap.ticker, ticker=snap.ticker,
                                      data=json.dumps(data, ensure_ascii=False, default=str)[:24000])
        resp = self.client.chat.completions.create(
            model=self.model, temperature=0.2, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": f"Hoy es {date.today().isoformat()}."},
                      {"role": "user", "content": prompt}],
        )
        parsed = json.loads(resp.choices[0].message.content or "{}")
        return {k: str(parsed.get(k, "")).strip() for k, _ in SECTIONS if parsed.get(k)}


# ============================================================================
# Helpers
# ============================================================================

def _pct(v: Optional[float]) -> str:
    return "n/d" if v is None else f"{v * 100:.1f} %"


def _money(v: Optional[float]) -> str:
    if v is None:
        return "n/d"
    a = abs(v)
    if a >= 1e12:
        return f"{v / 1e12:.2f} B"
    if a >= 1e9:
        return f"{v / 1e9:.1f} mil M"
    if a >= 1e6:
        return f"{v / 1e6:.0f} M"
    return f"{v:,.0f}"


def _x(v: Optional[float]) -> str:
    return "n/d" if v is None else f"{v:.1f}x"


def _headline_metrics(s: CompanySnapshot, val: Dict, q: Dict) -> Dict[str, str]:
    r = s.ratios
    cur = s.quote.get("currency") or ""
    price = s.quote.get("price")
    return {
        "Precio": f"{price:.2f} {cur}" if price else "n/d",
        "Capitalización": _money(s.quote.get("market_cap")),
        "PER (adelantado)": _x(r["valuation"]["pe_forward"]),
        "EV/EBITDA": _x(r["valuation"]["ev_to_ebitda"]),
        "FCF yield": _pct(r["valuation"]["fcf_yield"]),
        "Margen operativo": _pct(r["profitability"]["operating_margin"]),
        "ROE": _pct(r["profitability"]["roe"]),
        "Crecimiento ingresos (a/a)": _pct(r["growth"]["revenue_growth_yoy"]),
        "Deuda / patrimonio": _x(r["balance_sheet"]["debt_to_equity"]),
        "Valor DCF / acción": (f"{val['fair_value_per_share']:.2f} {cur} ({_pct(val.get('upside'))})"
                               if val.get("applicable") else "No aplicable"),
        "Crecimiento implícito en precio": _pct(val.get("implied_growth_at_price")) if val.get("applicable") else "n/d",
        "Piotroski F-Score": (f"{q['piotroski']['score']}/9 ({q['piotroski']['label']})"
                              if q["piotroski"]["score"] is not None else "n/d"),
        "Altman Z": f"{q['altman_z']['score']} ({q['altman_z']['zone']})" if q["altman_z"]["score"] else "n/d",
        "Rentabilidad 1 año": _pct(s.performance.get("return_1y")),
        "Máx. caída 1 año": _pct(s.performance.get("max_drawdown_1y")),
        "Objetivo analistas": (f"{s.analyst['target_mean']:.2f} ({_pct(s.analyst.get('upside_to_mean_target'))})"
                               if s.analyst.get("target_mean") else "n/d"),
    }


def _llm_payload(s: CompanySnapshot, val: Dict, q: Dict) -> Dict[str, Any]:
    val = {k: v for k, v in val.items() if k != "sensitivity"} | {"sensitivity": val.get("sensitivity")}
    return to_jsonable({
        "quote": s.quote, "profile": s.profile, "ratios": s.ratios, "performance": s.performance,
        "analyst": s.analyst, "valuation_dcf": val, "quality": q,
        "income_statement": _summary_statement(s.income, ["Total Revenue", "Gross Profit", "Operating Income",
                                                          "Net Income", "Diluted EPS"]),
        "cashflow": _summary_statement(s.cashflow, ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]),
        "news": [{"title": n["title"], "date": n["date"]} for n in s.news],
    })


def _summary_statement(df: Optional[pd.DataFrame], rows: List[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    present = [r for r in rows if r in df.index]
    out = df.loc[present].copy()
    for r in present:
        if "EPS" not in r:
            out.loc[r] = out.loc[r].astype(float) / 1e6
    return out.astype(float).round(2)


def _sources(s: CompanySnapshot) -> List[str]:
    src = ["Yahoo Finance (cotización, estados financieros, consenso, noticias)",
           "Cálculos propios Sindicato V8 (ratios, DCF, Piotroski, Altman)"]
    if s.filings:
        src += [f"SEC EDGAR {f['form']} ({f['date']}): {f['url']}" for f in s.filings[:3]]
    src += [f"Noticia: {n['title']} — {n.get('publisher') or ''} ({n.get('date') or ''})" for n in s.news[:3]
            if n.get("title")]
    return src


def _rule_based_sections(s: CompanySnapshot, val: Dict, q: Dict) -> Dict[str, str]:
    """Comentarios automáticos sin IA: reglas simples y transparentes."""
    r = s.ratios
    om, roe = r["profitability"]["operating_margin"], r["profitability"]["roe"]
    g, de = r["growth"]["revenue_growth_yoy"], r["balance_sheet"]["debt_to_equity"]
    pe = r["valuation"]["pe_forward"]

    bullets = []
    if g is not None:
        bullets.append(f"- Ingresos {'crecen' if g > 0 else 'caen'} un {_pct(abs(g))} interanual.")
    if om is not None:
        bullets.append(f"- Margen operativo del {_pct(om)} "
                       f"({'alto' if om > 0.2 else 'moderado' if om > 0.08 else 'bajo'}).")
    if roe is not None:
        bullets.append(f"- ROE del {_pct(roe)} ({'excelente' if roe > 0.2 else 'aceptable' if roe > 0.1 else 'débil'}).")
    if val.get("applicable") and val.get("upside") is not None:
        u = val["upside"]
        verdict = "atractiva" if u > 0.15 else "razonable" if u > -0.15 else "exigente"
        bullets.append(f"- El DCF base sitúa el valor en {val['fair_value_per_share']} ({_pct(u)} vs. precio): "
                       f"valoración **{verdict}** con estos supuestos.")
    elif pe is not None:
        bullets.append(f"- PER adelantado de {_x(pe)}.")

    risks = ([f"- Piotroski {q['piotroski']['score']}/9 → calidad contable {q['piotroski']['label'].lower()}."]
             if q["piotroski"]["score"] is not None else ["- Piotroski: datos insuficientes."])
    if q["altman_z"]["score"] is not None:
        risks.append(f"- Altman Z {q['altman_z']['score']} → zona {q['altman_z']['zone'].lower()}.")
    if de is not None and de > 1.5:
        risks.append(f"- Apalancamiento elevado (deuda/patrimonio {_x(de)}).")
    if s.performance.get("max_drawdown_1y") is not None:
        risks.append(f"- Caída máxima en 12 meses: {_pct(s.performance['max_drawdown_1y'])}; "
                     f"volatilidad anual {_pct(s.performance.get('volatility_annual'))}.")

    v = []
    if val.get("applicable"):
        a = val["assumptions"]
        v.append(f"DCF de 5 años con crecimiento del FCF {_pct(a['growth'])}, tasa {_pct(a['discount_rate'])} "
                 f"y crecimiento terminal {_pct(a['terminal_growth'])}. El valor terminal pesa un "
                 f"{_pct(val['terminal_share_of_ev'])} del total. El precio actual descuenta un crecimiento del "
                 f"{_pct(val.get('implied_growth_at_price'))} anual.")
    else:
        v.append(val.get("reason", "DCF no aplicable."))
    if s.analyst.get("target_mean"):
        v.append(f"Consenso: {s.analyst.get('recommendation')} con objetivo medio {s.analyst['target_mean']} "
                 f"({s.analyst.get('analysts')} analistas).")

    return {
        "resumen": "\n".join(bullets) or "Datos insuficientes para un resumen.",
        "negocio": f"**{s.profile.get('sector') or 'n/d'} · {s.profile.get('industry') or 'n/d'}** — "
                   f"{s.profile.get('summary') or 'Sin descripción disponible.'}",
        "financiero": "Ver tablas de cuenta de resultados, flujos y balance más abajo.",
        "valoracion": " ".join(v),
        "riesgos": "\n".join(risks),
        "vigilar": "- Evolución del margen operativo\n- Generación de FCF frente a beneficio\n"
                   "- Crecimiento de ingresos vs. el implícito en el precio\n- Próximos resultados trimestrales",
    }


def _df_markdown(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    fmt = lambda v: "n/d" if v is None or (isinstance(v, float) and pd.isna(v)) else (f"{v:,.2f}" if isinstance(v, (int, float)) else str(v))
    lines = ["| | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    lines += ["| " + str(idx) + " | " + " | ".join(fmt(v) for v in row) + " |" for idx, row in df.iterrows()]
    return "\n".join(lines)


def _dict_table(d: Dict[str, Any]) -> str:
    lines = ["| Métrica | Valor |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in d.items()]
    return "\n".join(lines)


def _mini_markdown(text: str) -> str:
    """Conversor mínimo markdown→HTML (títulos, viñetas, tablas, negrita) por si no está `markdown`."""
    import re
    out, in_list, table = [], False, []

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)

    def flush_table():
        nonlocal table
        if table:
            rows = [[c.strip() for c in r.strip("|").split("|")] for r in table if not re.match(r"^\|?\s*:?-", r)]
            head, *body = rows
            out.append("<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) +
                       "</table>")
            table = []

    for line in text.splitlines():
        if line.startswith("|"):
            table.append(line)
            continue
        flush_table()
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        m = re.match(r"^(#{1,3}) (.*)", line)
        if m:
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush_table()
    if in_list:
        out.append("</ul>")
    return "\n".join(out)
