
import streamlit as st
# Import mocked agents for now
from agents.value_agent import ValueAgent
from agents.growth_agent import GrowthAgent
from agents.risk_agent import RiskAgent
from agents.macro_agent import MacroAgent

def render():
    st.header("ANÁLISIS (Paralelo)")
    
    if st.button("Ejecutar Agentes"):
        # Gather data from session state
        company_data = {k: v for k, v in st.session_state.items() if k.startswith('empresa_')}
        
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        with col1:
            st.subheader("Value Agent")
            agent = ValueAgent()
            result = agent.analyze(company_data)
            st.json(result)
            st.session_state['analysis_value'] = result
            
        with col2:
            st.subheader("Growth Agent")
            agent = GrowthAgent()
            result = agent.analyze(company_data)
            st.json(result)
            st.session_state['analysis_growth'] = result
            
        with col3:
            st.subheader("Risk Agent")
            agent = RiskAgent()
            result = agent.analyze(company_data)
            st.json(result)
            st.session_state['analysis_risk'] = result
            
        with col4:
            st.subheader("Macro Agent (Pablo Gil)")
            agent = MacroAgent()
            result = agent.analyze(company_data, {}) # macro data placeholder
            st.json(result)
            st.session_state['analysis_macro'] = result
