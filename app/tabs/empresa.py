
import streamlit as st

def render():
    st.header("EMPRESA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Básicos")
        st.text_input("Nombre", key="empresa_nombre")
        st.text_input("Ticker", key="empresa_ticker")
        st.text_input("País", key="empresa_pais")
        st.text_input("Sector", key="empresa_sector")
        st.text_input("Industria", key="empresa_industria")

    with col2:
        st.subheader("Datos Clave")
        st.number_input("Market Cap (M)", key="empresa_mcap")
        st.number_input("Ingresos (M)", key="empresa_revenues")
        st.number_input("Crecimiento Ingresos (%)", key="empresa_rev_growth")
        st.number_input("EBITDA (M)", key="empresa_ebitda")
        st.number_input("Margen EBITDA (%)", key="empresa_ebitda_margin")
        st.number_input("Beneficio Neto (M)", key="empresa_net_income")
        st.number_input("ROIC (%)", key="empresa_roic")
        st.number_input("Deuda Neta (M)", key="empresa_net_debt")
    
    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Valoración")
        st.number_input("PER", key="empresa_per")
        st.number_input("EV/EBITDA", key="empresa_ev_ebitda")
        st.number_input("P/FCF", key="empresa_p_fcf")
        
    with col4:
        st.subheader("Flujos de Caja")
        st.number_input("Free Cash Flow (M)", key="empresa_fcf")
        st.selectbox("Estabilidad FCF", ["Estable", "Cíclico", "Errático"], key="empresa_fcf_stability")

    st.divider()
    st.subheader("Riesgos Estructurales (Datos)")
    c1, c2, c3 = st.columns(3)
    c1.text_area("Deuda", key="empresa_risk_debt", height=100)
    c2.text_area("Márgenes", key="empresa_risk_margins", height=100)
    c3.text_area("Dependencia Macro", key="empresa_risk_macro", height=100)
