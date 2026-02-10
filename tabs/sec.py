import streamlit as st
import logging

logger = logging.getLogger(__name__)

def render_tab(ticker: str):
    """
    Renderiza la pestaña de Análisis SEC (10-K/10-Q).
    """
    st.header(f"📄 {ticker} - SEC Filings Analyzer")
    
    # 0. ACTION BUTTONS AT TOP
    col_act, col_info = st.columns([1, 3])
    
    with col_act:
        analyze_btn = st.button("📥 Indexar Último 10-K", type="primary", width="stretch", key="sec_analyze_btn")
    
    with col_info:
        if st.session_state.active_doc_name:
            st.success(f"Documento Activo: {st.session_state.active_doc_name}")
        else:
            st.info("Sin documento cargado")

    st.markdown("---")

    # 1. LOGICA DE ANALISIS
    if analyze_btn:
        with st.spinner(f"Descargando y analizando último 10-K de {ticker}..."):
            try:
                # Usar SECAnalyzer service (asumiendo que existe en el session_state)
                # Nota: Esto es simplificado, idealmente llamaríamos a methods específicos
                filings = st.session_state.sec_analyzer.get_filings(ticker, form_type="10-K", limit=1)
                
                if filings:
                    filing = filings[0]
                    # Procesar y guardar en vectorstore (Oracle)
                    chars = st.session_state.oraculo.index_text(filing.content, f"{ticker}_10K_{filing.date}")
                    
                    st.session_state.active_doc_name = f"{ticker} 10-K ({filing.date})"
                    st.session_state.active_doc_content = filing.content # Guardar para agentes
                    
                    st.success(f"✅ 10-K Indexado ({chars} caracteres). Agentes listos.")
                    st.rerun()
                else:
                    st.error("No se encontró 10-K reciente.")
            except Exception as e:
                st.error(f"Error analizando SEC: {e}")
                logger.error(f"SEC Error: {e}")

    # 2. VISOR DE CONTENIDO (Si hay documento)
    if st.session_state.active_doc_name:
        st.subheader("Contenido Indexado")
        
        # Tabs internas para secciones del 10-K detectadas
        # Usamos el oráculo para buscar secciones
        sec_tabs = st.tabs(["Resumen", "Business", "Risk Factors", "MD&A"])
        
        with sec_tabs[0]:
             st.info("Este documento está disponible para el Comité y el Mentor.")
             if st.session_state.get('active_doc_content'):
                 st.text_area("Raw snippet", st.session_state.active_doc_content[:2000] + "...", height=300)

        with sec_tabs[1]: # Business
             res = st.session_state.oraculo.search("Business Description Strategy Products", k=5)
             st.markdown(res)
             
        with sec_tabs[2]: # Risks
             res = st.session_state.oraculo.search("Risk Factors Competition Regulation", k=5)
             st.markdown(res)
             
        with sec_tabs[3]: # MD&A
             res = st.session_state.oraculo.search("Management Discussion Analysis Results Operations", k=5)
             st.markdown(res)
    else:

        # Historial de filings disponibles
        st.subheader("📋 Filings Recientes")
        try:
            filings = st.session_state.sec_analyzer.get_filings(ticker, limit=5)
            for f in filings:
                with st.expander(f"{f.date} - {f.form_type}"):
                    st.write(f.link)
        except:
            st.caption("Carga el ticker para ver filings.")
