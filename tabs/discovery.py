import streamlit as st
import pandas as pd

def render_tab(ticker: str):
    """
    Renderiza la pestaña de Descubrimiento / Screener.
    """
    st.header(f"🕵️ Radar de Oportunidades: Sector {ticker}")
    
    # 0. ACTION BUTTONS AT TOP
    col_mode, col_btn = st.columns([3, 1])
    with col_mode:
        mode_screen = st.radio(
            "Criterio de Búsqueda:", 
            ["Institucional (Blue Chips)", "Alpha (Small Cap)"], 
            horizontal=True,
            help="Institucional: Busca solidez. Alpha: Busca gemas con ownership y ROCE alto",
            key="discovery_mode"
        )
        mode_key = "small_cap" if "Alpha" in mode_screen else "standard"
    
    with col_btn:
        st.write("")  # Espacio
        run_screen = st.button("🚀 Buscar Gemas", type="primary", key="discovery_btn")

    st.info("""
    **¿Cómo funciona?**
    1. Busca empresas similares a tu ticker (mismo sector)
    2. Las analiza con criterios Alpha o Institucionales
    3. Te muestra cuál es la mejor alternativa según los datos
    """)

    if run_screen:
        st.info(f"Buscando empresas similares a {ticker} y aplicando filtro {mode_screen}...")
        
        # Ejecutar Screener
        try:
            df_results = st.session_state.screener.run_screen(ticker, mode=mode_key)
            
            if not df_results.empty:
                # Destacar la ganadora
                best = df_results.iloc[0]
                
                if best['Ticker'] == ticker:
                    st.success(f"🏆 **{ticker}** es la mejor opción del sector según los criterios {mode_screen}")
                else:
                    st.warning(f"🔍 Encontré una alternativa mejor: **{best['Ticker']}** ({best['Tag']})")
                
                # Mostrar Tabla Interactiva
                st.dataframe(
                    df_results,
                    width="stretch",
                    hide_index=True
                )
                
                # Leyenda
                with st.expander("📖 ¿Cómo se calcula el Score?"):
                    if mode_key == "small_cap":
                        st.markdown("""
                        **Criterios Alpha (Small Cap):**
                        - ✅ **+2 puntos**: Deuda/Equity < 0.5 (deuda baja)
                        - ✅ **+3 puntos**: ROE > 15% (negocio de calidad)
                        - ✅ **+1 punto**: P/E entre 0 y 25 (valoración razonable)
                        - ✅ **+1 punto**: Margen > 10%
                        - ❌ **-2 puntos**: Deuda/Equity > 1.5 (deuda alta)
                        
                        **Score ≥ 4**: 💎 Posible Gema  
                        **Score 2-3**: ⚠️ Revisar  
                        **Score < 2**: ❌ Evitar
                        """)
                    else:
                        st.markdown("""
                        **Criterios Institucionales:**
                        - ✅ **+1 punto**: ROE > 10%
                        - ✅ **+1 punto**: P/E < 30
                        - ✅ **+1 punto**: Deuda/Equity < 1.0
                        - ✅ **+1 punto**: Margen > 8%
                        
                        **Score ≥ 3**: 🏢 Sólida  
                        **Score 2**: 📊 Neutral  
                        **Score < 2**: 📉 Débil
                        """)
            else:
                st.warning("No se encontraron datos suficientes de competidores.")
        except Exception as e:
            st.error(f"Error en el screener: {str(e)}")
