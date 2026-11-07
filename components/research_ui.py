"""
🖥️ UI del Copiloto y del Informe automático (Streamlit)
"""

from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from research import DataHub, ToolRegistry, FinancialCopilot, EquityReportGenerator

TOOL_LABELS = {
    "get_quote": "💲 Cotización", "get_company_profile": "🏢 Perfil", "get_financial_statement": "📒 Estados financieros",
    "get_key_ratios": "📐 Ratios", "get_price_performance": "📈 Rentabilidad", "get_analyst_view": "🎯 Consenso",
    "get_news": "📰 Noticias", "get_sec_filings": "🏛️ SEC filings", "get_sec_fundamentals": "🏛️ Datos XBRL SEC",
    "compare_companies": "🔄 Comparativa", "run_dcf_valuation": "🧮 DCF", "get_quality_scores": "🩺 Piotroski / Altman",
    "search_investment_library": "📚 Biblioteca",
}

SUGGESTIONS = [
    "Hazme un análisis rápido de {t}: negocio, números clave y valoración",
    "¿Está cara {t}? Usa múltiplos y un DCF y explícame los supuestos",
    "Compara {t} con sus 3 principales competidores",
    "¿Qué riesgos contables o de balance ves en {t}?",
    "¿Qué crecimiento está descontando el precio actual de {t}?",
]


@st.cache_resource(show_spinner=False)
def _hub() -> DataHub:
    return DataHub()


def _has_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _copilot() -> FinancialCopilot:
    if "copilot_agent" not in st.session_state:
        library = st.session_state.get("library")
        if library is not None and not getattr(library, "is_loaded", False):
            library = None
        st.session_state.copilot_agent = FinancialCopilot(ToolRegistry(_hub(), library=library))
        st.session_state.copilot_msgs = []
    return st.session_state.copilot_agent


def render_copilot_tab(ticker: str) -> None:
    st.header("🤖 Copiloto de análisis")
    st.caption("Pregunta en lenguaje natural. El copiloto consulta datos reales (Yahoo Finance, SEC) "
               "con herramientas y te enseña qué ha consultado.")

    if not _has_key():
        st.warning("Configura OPENAI_API_KEY (secrets o .env) para usar el copiloto.")
        return

    agent = _copilot()
    msgs = st.session_state.copilot_msgs

    c1, c2 = st.columns([4, 1])
    with c2:
        if st.button("🧹 Nueva conversación", use_container_width=True):
            agent.reset()
            st.session_state.copilot_msgs = []
            st.rerun()

    if not msgs:
        st.markdown("**Prueba con:**")
        cols = st.columns(len(SUGGESTIONS))
        for col, s in zip(cols, SUGGESTIONS):
            q = s.format(t=ticker)
            if col.button(q, use_container_width=True, key=f"sug_{hash(q)}"):
                st.session_state.copilot_pending = q
                st.rerun()

    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("tools"):
                with st.expander(f"🔧 Datos consultados ({len(m['tools'])})"):
                    for t in m["tools"]:
                        st.markdown(f"**{TOOL_LABELS.get(t.name, t.name)}** `{t.arguments}`")
                        st.code(t.result_preview, language="json")

    question = st.chat_input(f"Pregunta sobre {ticker} o cualquier empresa…")
    question = question or st.session_state.pop("copilot_pending", None)
    if not question:
        return

    msgs.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        status = st.status("Analizando…", expanded=False)
        try:
            reply = agent.ask(question, focus_ticker=ticker,
                              on_tool_call=lambda n, a: status.write(f"{TOOL_LABELS.get(n, n)} · {a}"))
            status.update(label=f"Hecho · {len(reply.tool_calls)} consultas de datos", state="complete")
            st.markdown(reply.content)
            msgs.append({"role": "assistant", "content": reply.content, "tools": reply.tool_calls})
        except Exception as exc:
            status.update(label="Error", state="error")
            st.error(f"No se pudo completar la respuesta: {exc}")


def render_report_tab(ticker: str) -> None:
    st.header(f"📑 Informe automático · {ticker}")
    st.caption("Descarga datos, calcula ratios, DCF y scores de calidad, y redacta un informe de análisis "
               "completo. Sin API key genera la versión 'solo datos'.")

    cache = st.session_state.setdefault("auto_reports", {})
    if st.button("⚡ Generar informe", type="primary"):
        bar = st.progress(0.0, text="Empezando…")
        try:
            gen = EquityReportGenerator(_hub())
            cache[ticker] = gen.generate(ticker, progress=lambda msg, p: bar.progress(p, text=msg))
        except Exception as exc:
            st.error(f"Error generando el informe: {exc}")
            return

    report = cache.get(ticker)
    if report is None:
        st.info("Pulsa **Generar informe** para crear el análisis de esta empresa.")
        return

    stamp = datetime.now().strftime("%Y%m%d")
    d1, d2 = st.columns(2)
    d1.download_button("⬇️ Descargar HTML", report.to_html(), file_name=f"{ticker}_informe_{stamp}.html",
                       mime="text/html", use_container_width=True)
    d2.download_button("⬇️ Descargar Markdown", report.to_markdown(), file_name=f"{ticker}_informe_{stamp}.md",
                       mime="text/markdown", use_container_width=True)
    st.markdown(report.to_markdown())
