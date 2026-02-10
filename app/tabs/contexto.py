
import streamlit as st

def render():
    st.header("CONTEXTO")
    
    st.toggle("Noticias (ON/OFF)", key="contexto_news_toggle")
    
    st.subheader("Comparables Automáticos")
    st.info("Comparables basados en Sector, País y Capitalización.")
    
    # Placeholder logic for comparables
    if 'empresa_sector' in st.session_state and st.session_state['empresa_sector']:
        st.write(f"Buscando comparables para el sector: {st.session_state['empresa_sector']}")
        st.write("- Comparable 1 (Placeholder)")
        st.write("- Comparable 2 (Placeholder)")
    else:
        st.warning("Define el sector en la tab 'EMPRESA' para ver comparables.")
