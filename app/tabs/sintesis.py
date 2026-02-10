
import streamlit as st
from agents.verdict_agent import VerdictAgent
from agents.oracle_agent import OracleAgent

def render():
    st.header("SÍNTESIS")
    
    if all(key in st.session_state for key in ['analysis_value', 'analysis_growth', 'analysis_risk', 'analysis_macro']):
        analyses = {
            "value": st.session_state['analysis_value'],
            "growth": st.session_state['analysis_growth'],
            "risk": st.session_state['analysis_risk'],
            "macro": st.session_state['analysis_macro']
        }
        
        verdict_agent = VerdictAgent()
        verdict = verdict_agent.synthesize(analyses)
        
        st.subheader("Veredicto del Meta-Agente")
        st.json(verdict)
        
        st.divider()
        
        oracle_agent = OracleAgent()
        questions = oracle_agent.generate_questions(verdict)
        
        st.subheader("Preguntas para NotebookLM (Mentor)")
        for q in questions:
            st.markdown(f"- **{q}**")
            
    else:
        st.warning("Ejecuta primero el análisis en la tab 'ANÁLISIS' para ver la síntesis.")
