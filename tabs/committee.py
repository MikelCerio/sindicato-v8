import streamlit as st
import logging

logger = logging.getLogger(__name__)

def render_tab(ticker: str):
    """
    Renderiza la pestaña del Comité de Inversión con UI de Tarjetas.
    """
    st.header(f"🦈 {ticker} - Investment Committee")
    
    # 0. INYECTAR CSS PARA TARJETAS
    st.markdown("""
    <style>
    .analyst-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #555;
    }
    .card-value { border-left-color: #3498db; }
    .card-growth { border-left-color: #2ecc71; }
    .card-risk { border-left-color: #e74c3c; }
    
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
        color: white;
        background-color: #444;
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. ACTION BUTTONS (GRANULAR - 3 BOTONES)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        run_value = st.button("🛡️ Audit Value", width="stretch")
    with c2:
        run_growth = st.button("🚀 Audit Growth", width="stretch")
    with c3:
        run_risk = st.button("👁️ Audit Risk", width="stretch")

    st.markdown("---")

    # 2. LOGIC FOR RUNNING AUDITS
    if run_value or run_growth or run_risk:
        macro_text = st.session_state.get('macro_context', "Neutral")
        financial_context = st.session_state.oraculo.get_financial_context()
        mode = "small_cap" if "Alpha" in st.session_state.get('discovery_mode', '') else "standard"
        
        # INYECTAR 10-K & OPENBB
        if st.session_state.get('active_doc_content'):
            summary_10k = st.session_state.active_doc_content[:15000]
            financial_context['sec_filing_summary'] = summary_10k
            financial_context['value'] = financial_context.get('value', '') + f"\n\nRESUMEN 10-K:\n{summary_10k[:5000]}..."
            financial_context['risk'] = financial_context.get('risk', '') + f"\n\nRESUMEN 10-K:\n{summary_10k[:5000]}..."
        
        try:
            metrics = st.session_state.openbb.get_key_metrics(ticker)
            stmts = st.session_state.openbb.get_financial_statements(ticker)
            hard_data = f"\n📊 DATOS OPENBB:\nPrice: ${st.session_state.market_service.get_current_price(ticker)}\n"
            if metrics: hard_data += f"P/E: {metrics.pe_ratio}\nDebt/Eq: {metrics.debt_to_equity}\nROE: {metrics.roe}\n"
            if stmts and stmts.balance_sheet is not None:
                hard_data += f"BALANCE:\n{stmts.balance_sheet.iloc[:, 0].to_string()[:1000]}\n"
            
            financial_context['value'] += hard_data
            financial_context['growth'] += hard_data
            financial_context['risk'] += hard_data
        except Exception as e:
            logger.error(f"Error OpenBB: {e}")

        # EJECUCIONES INDIVIDUALES
        if run_value:
            with st.spinner("Auditor Value analizando..."):
                st.session_state.debate_value = st.session_state.committee.run_value_audit(
                    ticker, str(macro_text), financial_context.get('value', ''), mode
                )
        
        if run_growth:
            with st.spinner("Analista Growth investigando..."):
                st.session_state.debate_growth = st.session_state.committee.run_growth_audit(
                    ticker, financial_context.get('growth', ''), mode
                )

        if run_risk:
            with st.spinner("Risk Hunter buscando problemas..."):
                st.session_state.debate_risk = st.session_state.committee.run_risk_audit(
                    ticker, str(macro_text), financial_context.get('risk', ''), mode
                )
        
        st.rerun()

    # 3. RENDER CARDS (Si hay resultados)
    if st.session_state.debate_value or st.session_state.debate_growth or st.session_state.debate_risk:
        c1, c2, c3 = st.columns(3)
        
        # --- VALUE ANALYST CARD ---
        with c1:
            st.markdown('<div class="analyst-card card-value">', unsafe_allow_html=True)
            st.markdown("### 🛡️ Value Investor <span class='status-badge'>Fundamental</span>", unsafe_allow_html=True)
            st.caption("Balance, Deuda, Valoración")
            
            with st.container(height=300):
                if st.session_state.debate_value:
                    st.markdown(st.session_state.debate_value)
                else:
                    st.info("Esperando análisis...")
            
            st.divider()
            st.progress(65, text="Confidence: 65%")
            st.markdown('</div>', unsafe_allow_html=True)

        # --- GROWTH ANALYST CARD ---
        with c2:
            st.markdown('<div class="analyst-card card-growth">', unsafe_allow_html=True)
            st.markdown("### 🚀 Growth Investor <span class='status-badge'>Expansion</span>", unsafe_allow_html=True)
            st.caption("I+D, Mercado, Ventajas")
            
            with st.container(height=300):
                if st.session_state.debate_growth:
                    st.markdown(st.session_state.debate_growth)
                else:
                    st.info("Esperando análisis...")
            
            st.divider()
            st.progress(70, text="Confidence: 70%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # --- RISK ANALYST CARD ---
        with c3:
            st.markdown('<div class="analyst-card card-risk">', unsafe_allow_html=True)
            st.markdown("### 👁️ Devil's Advocate <span class='status-badge'>Risk</span>", unsafe_allow_html=True)
            st.caption("Amenazas, Litigios, Macro")
            
            with st.container(height=300):
                if st.session_state.debate_risk:
                    st.markdown(st.session_state.debate_risk)
                else:
                    st.info("Esperando análisis...")
            
            st.divider()
            st.progress(85, text="Confidence: 85%")
            st.markdown('</div>', unsafe_allow_html=True)

        # 4. DEBATE RAW (Expander)
        if st.session_state.debate_raw:
            with st.expander("📝 Ver Debate Completo (Transcripción)"):
                st.text(st.session_state.debate_raw)
            
        # 5. CONTINUE TO VERDICT BUTTON
        st.write("")
        col_verdict_btn, _ = st.columns([1, 3])
        if col_verdict_btn.button("⚖️ Ir al Veredicto Final", type="secondary"):
             st.info("Ve a la pestaña 'VEREDICTO' para la decisión del CIO.")

    else:
        # Placeholder bonito cuando no hay datos
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Selecciona un auditor arriba para comenzar el análisis.")
        
        # Muestra placeholders visuales
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="analyst-card card-value" style="opacity:0.5"><h3>🛡️ Value</h3>Pulsa auditar...</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="analyst-card card-growth" style="opacity:0.5"><h3>🚀 Growth</h3>Pulsa auditar...</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="analyst-card card-risk" style="opacity:0.5"><h3>👁️ Risk</h3>Pulsa auditar...</div>', unsafe_allow_html=True)
