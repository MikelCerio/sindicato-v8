"""
🏛️ SINDICATO V8 ELITE - Institutional Investment Platform
APP PRINCIPAL (Modularized)

Features:
- Dashboard con datos OpenBB
- Portfolio Optimizer
- Knowledge Library
- Comité de Inversiones con CrewAI (Card Layout)
"""

import streamlit as st
import threading
import signal
import os
from datetime import datetime

# --- FIX: PATCH SIGNAL ON NON-MAIN THREAD (Python 3.13+) ---
if threading.current_thread() is not threading.main_thread():
    original_signal = signal.signal
    def safe_signal(signalnum, handler):
        try:
            return original_signal(signalnum, handler)
        except ValueError:
            pass 
    signal.signal = safe_signal

# Configuración PRIMERO (debe ser lo primero en la app)
st.set_page_config(
    page_title="Sindicato V8 Elite", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports
from config import CSS_STYLES, PATHS, initialize
from services import (
    OraculoV8, MarketDataService, SentimentAnalyzer, 
    PDFGenerator, SessionManager, get_macro_context,
    TickerComparator, PriceChartService,
    OpenBBService, PortfolioOptimizer, KnowledgeLibrary,
    SECAnalyzer, ScreenerService, MacroService
)
from agents import InvestmentCommittee, MentorAgent

# Import Tabs Modules
import tabs.data as tab_data
import tabs.committee as tab_committee
import tabs.sec as tab_sec
import tabs.mentor as tab_mentor
import tabs.discovery as tab_discovery
import tabs.library as tab_library
# import tabs.charts as tab_charts # To be implemented if specialized charting needed beyond data tab

# Initialize
initialize()
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

def init_state():
    """Inicializa todos los servicios y estados."""
    defaults = {
        # Services
        'oraculo': OraculoV8(),
        'market_service': MarketDataService(),
        'sentiment_analyzer': SentimentAnalyzer(),
        'session_manager': SessionManager(),
        'pdf_generator': PDFGenerator(),
        'committee': InvestmentCommittee(),
        'mentor': MentorAgent(),
        'chart_service': PriceChartService(),
        'comparator': TickerComparator(),
        'openbb': OpenBBService(),
        'optimizer': PortfolioOptimizer(),
        'library': KnowledgeLibrary(),
        'sec_analyzer': SECAnalyzer(),
        'screener': ScreenerService(),
        'macro_strategy': MacroService(),
        
        # State Data
        'active_doc_name': None,
        'active_doc_content': None, # IMPORTANTE: Contenido raw para agentes
        'doc_structure': None,
        'debate_raw': None,
        'debate_value': None,
        'debate_growth': None,
        'debate_risk': None,
        'veredicto_final': None,
        'allocation_final': None,
        'last_ticker': None,
        'audit_history': {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
macro = get_macro_context() # Load macro once

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🏛️ SINDICATO V8")
    st.caption("ELITE Edition • Modular")
    st.markdown("---")
    
    # API KEY & Macro Widget (Simplificado para brevedad, idealmente un componente sidebar.py)
    # ... (Copiar lógica de sidebar existente si es necesario, o mantener simple) ...
    
    st.subheader("🔑 Configuración")
    api_key_configured = bool(os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY'))
    if api_key_configured:
        st.success("✅ API Key Activa")
    else:
        st.warning("⚠️ Sin API Key")
        key = st.text_input("API Key", type="password")
        if key:
            os.environ['OPENAI_API_KEY'] = key
            st.rerun()

    st.markdown("---")
    
    # Macro Status Mini
    st.caption("🌍 Macro Status")
    st.metric("Régimen", f"{macro.regime_emoji} {macro.regime}")
    st.metric("10Y Yield", f"{macro.treasury_10y:.2f}%")

# ============================================================================
# MAIN CONTENT
# ============================================================================

from components import ticker_selector

st.title("🎯 Sindicato de Inversión")

col_search, col_macro = st.columns([3, 1])

with col_search:
    ticker = ticker_selector(
        key="main_ticker",
        default_ticker="TSLA",
        label="Busca empresa por Ticker",
        show_manual_input=True
    )

with col_macro:
    # Mostrar alerta macro si es grave
    if macro.is_crisis:
        st.error("⚠️ CRISIS")
    elif macro.is_elevated:
        st.warning("⚡ Volatilidad")
    else:
        st.success("✅ Mercado Estable")

# GESTIÓN MEMORIA (Restaurar análisis previo si volvemos al ticker)
if st.session_state.last_ticker != ticker:
    st.session_state.last_ticker = ticker
    # Limpiar o recuperar estado (Lógica simplificada)
    if ticker in st.session_state.audit_history:
        h = st.session_state.audit_history[ticker]
        st.session_state.debate_value = h.get('debate_value')
        st.session_state.debate_growth = h.get('debate_growth')
        st.session_state.debate_risk = h.get('debate_risk')
        st.session_state.debate_raw = h.get('debate_raw')
        st.toast(f"Memoria recuperada para {ticker}")
    else:
        # Reset visuales
        st.session_state.debate_value = None
        st.session_state.debate_growth = None
        st.session_state.debate_risk = None
        st.session_state.debate_raw = None

st.markdown("---")

# TABS PRINCIPALES
# Definimos los tabs y delegamos el renderizado a los módulos
tab_names = [
    "📊 DATOS",
    "🦈 COMITÉ",
    "📄 SEC FILLINGS",
    "🕵️ DESCUBRIR",
    "👨‍🏫 MENTOR",
    "📚 BIBLIOTECA",
    # "⚖️ VEREDICTO", # To be refactored
    # "📈 GRÁFICOS", # Fusionado en Datos
]

tabs = st.tabs(tab_names)

# 1. TAB DATOS
with tabs[0]:
    tab_data.render_tab(ticker)

# 2. TAB COMITÉ (Core UI renovada)
with tabs[1]:
    tab_committee.render_tab(ticker)

# 3. TAB SEC
with tabs[2]:
    tab_sec.render_tab(ticker)

# 4. TAB DESCUBRIR
with tabs[3]:
    tab_discovery.render_tab(ticker)

# 5. TAB MENTOR
with tabs[4]:
    tab_mentor.render_tab(ticker)

# 6. TAB BIBLIOTECA
with tabs[5]:
    tab_library.render_tab(ticker)

# Footer
st.markdown("---")
st.caption(f"Sindicato V8 Elite | {datetime.now().year} | Powered by OpenRouter & crewAI")
