
import streamlit as st
import sys
import os

# Add root directory to sys.path to allow imports from agents/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import tabs. Since we are in app/, and app is a package (if __init__ exists), or just a folder.
# If we run 'streamlit run app/app.py', we can import from tabs directly if we are careful,
# but using the root path allows absolute imports.

try:
    from app.tabs import empresa, contexto, analisis, sintesis
except ImportError:
    # Fallback if running directly from app folder without root context (less likely with the sys.path append but possible)
    from tabs import empresa, contexto, analisis, sintesis

st.set_page_config(layout="wide", page_title="Sindicato v8 - Clean Arch")

st.title("Sindicato v8: Arquitectura Limpia")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["1️⃣ EMPRESA", "2️⃣ CONTEXTO", "3️⃣ ANÁLISIS", "4️⃣ SÍNTESIS"])

with tab1:
    empresa.render()

with tab2:
    contexto.render()

with tab3:
    analisis.render()

with tab4:
    sintesis.render()
