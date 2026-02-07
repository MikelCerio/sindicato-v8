"""
🏛️ SINDICATO V8 ELITE - Institutional Investment Platform
APP PRINCIPAL CON TODAS LAS FEATURES ELITE

Features:
- Dashboard con datos OpenBB (Financial Statements, Ratios, etc.)
- Portfolio Optimizer (Markowitz)
- Knowledge Library (Libros de inversión)
- Chain of Thought en prompts
- Comité de inversiones con CrewAI
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuración PRIMERO (debe ser lo primero en la app)
st.set_page_config(
    page_title="Sindicato V8 Elite", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports después de config
from config import CSS_STYLES, PATHS, initialize
from prompts import SUGGESTED_QUESTIONS
from services import (
    OraculoV8, MarketDataService, SentimentAnalyzer, 
    PDFGenerator, SessionManager, get_macro_context,
    TickerComparator, PriceChartService,
    # === ELITE SERVICES ===
    OpenBBService, PortfolioOptimizer, KnowledgeLibrary,
    create_portfolio_pie_chart, create_efficient_frontier_chart,
    add_essential_wisdom,
    HTMLReportRenderer,  # Report renderer estilo FinRobot
    # === SEC ANALYZER (FinRobot-inspired) ===
    SECAnalyzer, format_filing_date, get_filing_icon,
    # === SCREENER (Discovery) ===
    ScreenerService,
    # === MACRO SERVICE (Pablo Gil) ===
    MacroService
)
from agents import InvestmentCommittee, MentorAgent

# Initialize
initialize()
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

def init_state():
    """Inicializa todos los servicios y estados."""
    defaults = {
        # === CORE SERVICES ===
        'oraculo': OraculoV8(),
        'market_service': MarketDataService(),
        'sentiment_analyzer': SentimentAnalyzer(),
        'session_manager': SessionManager(),
        'pdf_generator': PDFGenerator(),
        'committee': InvestmentCommittee(),
        'mentor': MentorAgent(),
        'chart_service': PriceChartService(),
        'comparator': TickerComparator(),
        
        # === ELITE SERVICES ===
        'openbb': OpenBBService(),
        'optimizer': PortfolioOptimizer(),
        'library': KnowledgeLibrary(),
        'renderer': HTMLReportRenderer(),  # HTML Report Generator
        'sec_analyzer': SECAnalyzer(),  # SEC Filings Analyzer
        'screener': ScreenerService(),  # Stock Screener/Discovery
        'macro_strategy': MacroService(),  # Macro Analysis (Pablo Gil)
        
        # === STATE ===
        'active_doc_name': None,
        'doc_structure': None,
        'debate_raw': None,
        'debate_value': None,
        'debate_growth': None,
        'debate_risk': None,
        'veredicto_final': None,
        'allocation_final': None,
        'optimization_result': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
macro = get_macro_context()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🏛️ SINDICATO V8")
    st.caption("ELITE Edition • Chain of Thought")
    st.markdown("---")
    
    # === API KEY CONFIGURATION ===
    st.subheader("🔑 Configuración")
    
    # Check if API key is configured
    api_key_configured = False
    api_key_source = None
    
    # Priority 1: Session state (user input)
    if 'user_api_key' in st.session_state and st.session_state.user_api_key:
        api_key_configured = True
        api_key_source = "Usuario"
    # Priority 2: Streamlit secrets
    elif hasattr(st, 'secrets') and 'openai' in st.secrets:
        api_key_configured = True
        api_key_source = "Secrets"
    # Priority 3: Environment variable
    elif os.getenv('OPENAI_API_KEY'):
        api_key_configured = True
        api_key_source = "Entorno"
    
    if api_key_configured:
        st.success(f"✅ API Key configurada ({api_key_source})")
    else:
        st.warning("⚠️ API Key no configurada")
        
        with st.expander("🔧 Configurar API Key", expanded=not api_key_configured):
            st.caption("Ingresa tu API key de OpenAI para usar la app")
            
            user_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-proj-...",
                help="Tu API key se guardará solo en esta sesión"
            )
            
            if st.button("💾 Guardar API Key"):
                if user_key and user_key.startswith("sk-"):
                    st.session_state.user_api_key = user_key
                    # Set environment variable for this session
                    os.environ['OPENAI_API_KEY'] = user_key
                    st.success("✅ API Key guardada!")
                    st.rerun()
                else:
                    st.error("❌ API Key inválida (debe empezar con 'sk-')")
            
            st.markdown("---")
            st.caption("💡 **¿Dónde conseguir una API key?**")
            st.markdown("[🔗 OpenAI Platform](https://platform.openai.com/api-keys)")
            st.caption("La API key solo se guarda en tu sesión actual y no se comparte.")
    
    st.markdown("---")
    
    # === MACRO DASHBOARD (Pablo Gil Style) ===
    st.subheader("🌍 Visión Macro")
    
    # Botón para actualizar análisis macro completo
    with st.expander("📊 Dashboard Pablo Gil", expanded=False):
        if st.button("🔄 Actualizar Macro", use_container_width=True):
            st.session_state.macro_dashboard = st.session_state.macro_strategy.get_dashboard()
        
        if hasattr(st.session_state, 'macro_dashboard'):
            dash = st.session_state.macro_dashboard
            
            # Régimen
            st.metric("Régimen", f"{dash.macro_emoji} {dash.macro_regime}")
            
            # Curva de Tipos
            st.caption("📈 Curva de Tipos (10Y-2Y)")
            spread_color = "🔴" if dash.yield_curve_spread < 0 else "🟢"
            st.write(f"{spread_color} Spread: **{dash.yield_curve_spread:.2f}%**")
            st.caption(dash.curve_status)
            
            # Indicadores clave
            c1, c2 = st.columns(2)
            c1.metric("VIX", f"{dash.vix:.1f}")
            c2.metric("DXY", f"{dash.dxy:.1f}")
            
            c3, c4 = st.columns(2)
            c3.metric("Oro", f"${dash.gold_price:.0f}")
            c4.metric("10Y", f"{dash.treasury_10y:.2f}%")
            
            # Señal de Recesión
            signal = st.session_state.macro_strategy.check_recession_signal()
            st.info(f"**Recesión:** {signal['status']}\n\n{signal['explanation']}")
            
            # Lo que diría Pablo Gil
            st.warning(f"🎙️ **Pablo Gil:** {dash.pablo_gil_says[:150]}...")
    
    # Régimen simple (siempre visible)
    st.metric("Estado Mercado", f"{macro.regime_emoji} {macro.regime}")
    c1, c2 = st.columns(2)
    c1.metric("VIX", f"{macro.vix:.1f}")
    c2.metric("10Y", f"{macro.treasury_10y:.2f}%")
    
    if macro.is_crisis:
        st.error("⚠️ MODO CRISIS - Preservar Capital")
    elif macro.is_elevated:
        st.warning("⚡ Volatilidad elevada - Precaución")
    
    st.markdown("---")
    
    # === DOCUMENTO ACTIVO ===
    st.subheader("📂 Documento Activo")
    if st.session_state.active_doc_name:
        st.success(st.session_state.active_doc_name[:25] + "...")
        s = st.session_state.doc_structure
        if s:
            cols = st.columns(3)
            if s.has_balance_sheet: cols[0].write("✅ Balance")
            if s.has_risk_factors: cols[1].write("✅ Risks")
            if s.has_mda: cols[2].write("✅ MD&A")
    else:
        st.info("Sin documento cargado")
    
    st.markdown("---")
    
    # === BIBLIOTECA ===
    st.subheader("📚 Biblioteca")
    lib = st.session_state.library
    st.metric("Libros", lib.book_count)
    if lib.book_count == 0:
        if st.button("🧠 Cargar Sabiduría", help="Añade principios de Buffett, Munger, Graham"):
            with st.spinner("Indexando sabiduría..."):
                n = add_essential_wisdom(lib)
                st.success(f"✅ {n} fuentes añadidas")
                st.rerun()
    
    st.markdown("---")
    
    # === NAVEGACIÓN RÁPIDA ===
    st.subheader("🧭 Navegación")
    st.caption("Secciones principales:")
    
    nav_options = {
        "📊 Análisis": "Datos y fundamentos",
        "🦈 Comité": "Auditoría del equipo",
        "⚖️ Veredicto": "Decisión final",
        "📄 SEC": "Filings oficiales",
        "🕵️ Descubrir": "Encontrar alternativas"
    }
    
    for nav, desc in nav_options.items():
        st.caption(f"**{nav}** - {desc}")

# ============================================================================
# MAIN CONTENT
# ============================================================================

from components import ticker_selector

st.header("🎯 Selecciona una Empresa")

ticker = ticker_selector(
    key="main_ticker",
    default_ticker="TSLA",
    label="Busca por nombre o ticker",
    show_manual_input=True,
    show_info=True
)

st.markdown("---")

# Tabs (estructura temporal - pendiente reorganización UX)
tabs = st.tabs([
    "📊 DATOS",
    "🧠 OPENBB",
    "🕵️ DESCUBRIR",
    "📈 GRÁFICOS", 
    "🔄 COMPARAR",
    "⚖️ OPTIMIZER",
    "🦈 COMITÉ",
    "⚖️ VEREDICTO",
    "📚 BIBLIOTECA",
    "👨‍🏫 MENTOR",
    "📂 DOCS",
    "📄 SEC"
])

# ============================================================================
# TAB 0: OVERVIEW - DASHBOARD UNIFICADO (Estilo Bloomberg Terminal)
# ============================================================================

with tabs[0]:
    from components import (
        render_ticker_header,
        render_key_metrics_compact,
        render_sentiment_news_card,
        render_financial_statements_collapsible,
        render_price_chart,
        render_quick_actions
    )
    
    # === 1. TICKER HEADER ===
    # Obtener datos fundamentales
    f = st.session_state.market_service.get_fundamentals(ticker)
    
    if f:
        # Calcular cambio porcentual (simulado - en producción vendría de API)
        change_pct = 2.3  # TODO: Obtener de API en tiempo real
        
        render_ticker_header(
            ticker=ticker,
            company_name=f.company_name if hasattr(f, 'company_name') else f"Company {ticker}",
            price=f.price,
            change_pct=change_pct,
            market_cap=f.market_cap
        )
        
        # === 2. KEY METRICS ===
        metrics = {
            'pe_ratio': f.pe_ratio,
            'forward_pe': f.forward_pe,
            'roe': f.roe,
            'debt_to_equity': f.debt_to_equity,
            'eps': getattr(f, 'eps', None),
            'revenue_growth': getattr(f, 'revenue_growth', None),
            'profit_margin': getattr(f, 'profit_margin', None),
            'beta': getattr(f, 'beta', None),
        }
        
        render_key_metrics_compact(metrics)
        
        st.markdown("---")
        
        # === 3. SENTIMENT & NEWS ===
        sent = st.session_state.sentiment_analyzer.analyze(ticker)
        render_sentiment_news_card(sent)
        
        st.markdown("---")
        
        # === 4. FINANCIAL STATEMENTS (Colapsable) ===
        render_financial_statements_collapsible(ticker, st.session_state.openbb)
        
        st.markdown("---")
        
        # === 5. PRICE CHART ===
        render_price_chart(ticker, st.session_state.chart_service)
        
        # === 6. QUICK ACTIONS ===
        render_quick_actions(ticker)
        
    else:
        st.error(f"❌ No se pudieron cargar datos para {ticker}")
        st.info("💡 Verifica que el ticker sea correcto y que tengas conexión a internet.")

# ============================================================================
# TAB 2: OPENBB DEEP DIVE
# ============================================================================

with tabs[1]:
    st.header(f"🧠 {ticker} - Deep Dive Institucional")
    st.caption("Datos profesionales via OpenBB Platform")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📥 Cargar Datos Completos", use_container_width=True):
            with st.spinner("Consultando OpenBB Platform..."):
                # Key Metrics
                metrics = st.session_state.openbb.get_key_metrics(ticker)
                
                if metrics:
                    st.subheader("📊 Métricas Clave")
                    
                    # Valuation
                    st.write("**Valoración**")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("P/E", f"{metrics.pe_ratio:.1f}")
                    c2.metric("P/B", f"{metrics.pb_ratio:.1f}")
                    c3.metric("P/S", f"{metrics.ps_ratio:.1f}")
                    c4.metric("EV/EBITDA", f"{metrics.ev_ebitda:.1f}")
                    
                    # Profitability
                    st.write("**Rentabilidad**")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Gross Margin", f"{metrics.gross_margin*100:.1f}%")
                    c2.metric("Op. Margin", f"{metrics.operating_margin*100:.1f}%")
                    c3.metric("Net Margin", f"{metrics.net_margin*100:.1f}%")
                    c4.metric("ROE", f"{metrics.roe*100:.1f}%")
                    
                    # Liquidity
                    st.write("**Liquidez y Solvencia**")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Current Ratio", f"{metrics.current_ratio:.2f}")
                    c2.metric("Quick Ratio", f"{metrics.quick_ratio:.2f}")
                    c3.metric("Cash Ratio", f"{metrics.cash_ratio:.2f}")
                    c4.metric("D/E", f"{metrics.debt_to_equity:.1f}")
                    
                    # Raw data expander
                    with st.expander("📋 Ver Datos Completos (JSON)"):
                        st.json(metrics.raw_data)
                else:
                    st.error("No se pudieron obtener métricas")
                
                # Financial Statements
                st.markdown("---")
                statements = st.session_state.openbb.get_financial_statements(ticker)
                
                if statements:
                    st.subheader("📑 Estados Financieros")
                    
                    fin_tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
                    
                    with fin_tabs[0]:
                        if statements.income_statement is not None:
                            st.dataframe(statements.income_statement, use_container_width=True)
                        else:
                            st.info("No disponible")
                    
                    with fin_tabs[1]:
                        if statements.balance_sheet is not None:
                            st.dataframe(statements.balance_sheet, use_container_width=True)
                        else:
                            st.info("No disponible")
                    
                    with fin_tabs[2]:
                        if statements.cash_flow is not None:
                            st.dataframe(statements.cash_flow, use_container_width=True)
                        else:
                            st.info("No disponible")
    
    with col2:
        st.subheader("📈 Analyst Estimates")
        estimates = st.session_state.openbb.get_estimates(ticker)
        if estimates:
            st.metric("Recommendation", estimates.recommendation.upper())
            st.metric("Target Price", f"${estimates.target_price:.2f}")
            st.write(f"**Range:** ${estimates.target_low:.0f} - ${estimates.target_high:.0f}")
            st.metric("# Analysts", estimates.num_analysts)
        
        st.markdown("---")
        
        st.subheader("🏢 Company Profile")
        profile = st.session_state.openbb.get_company_profile(ticker)
        if profile:
            st.write(f"**Sector:** {profile.get('sector', 'N/A')}")
            st.write(f"**Industry:** {profile.get('industry', 'N/A')}")
            st.write(f"**Employees:** {profile.get('employees', 0):,}")
            st.write(f"**Country:** {profile.get('country', 'N/A')}")

# ============================================================================
# TAB 3: GRÁFICOS
# ============================================================================

# ============================================================================
# TAB 3: DESCUBRIR (SCREENER)
# ============================================================================

with tabs[2]:
    st.header(f"🕵️ Radar de Oportunidades: Sector {ticker}")
    
    st.info("""
    **¿Cómo funciona?**
    1. Busca empresas similares a tu ticker (mismo sector)
    2. Las analiza con criterios Alpha o Institucionales
    3. Te muestra cuál es la mejor alternativa según los datos
    """)
    
    col_mode, col_btn = st.columns([3, 1])
    with col_mode:
        mode_screen = st.radio(
            "Criterio de Búsqueda:", 
            ["Institucional (Blue Chips)", "Alpha (Small Cap)"], 
            horizontal=True,
            help="Institucional: Busca solidez. Alpha: Busca gemas con ownership y ROCE alto"
        )
        mode_key = "small_cap" if "Alpha" in mode_screen else "standard"
    
    with col_btn:
        st.write("")  # Espacio
        run_screen = st.button("🚀 Buscar Gemas", type="primary")

    if run_screen:
        st.info(f"Buscando empresas similares a {ticker} y aplicando filtro {mode_screen}...")
        
        # Ejecutar Screener
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
                use_container_width=True,
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

# ============================================================================
# TAB 4: GRÁFICOS
# ============================================================================

with tabs[3]:
    st.header(f"📈 {ticker} - Gráficos")
    
    period = st.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    # Candlestick
    candle = st.session_state.chart_service.create_candlestick_chart(ticker, period)
    if candle:
        st.plotly_chart(candle, use_container_width=True)
    
    # Performance
    perf = st.session_state.chart_service.create_performance_chart(ticker, period)
    if perf:
        st.plotly_chart(perf, use_container_width=True)

# ============================================================================
# TAB 5: COMPARAR
# ============================================================================

with tabs[4]:
    st.header("🔄 Comparativa de Tickers")
    
    tickers_input = st.text_input("Tickers (separados por coma)", "AAPL, MSFT, GOOGL, TSLA")
    tickers_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if len(tickers_list) >= 2 and st.button("🔍 Comparar Fundamentales"):
        with st.spinner("Comparando..."):
            result = st.session_state.comparator.compare(tickers_list)
            
            if result:
                st.success(f"🏆 Mejor: {result.winner} (Score: {result.scores[result.winner]})")
                
                st.dataframe(result.comparison_table, use_container_width=True)
                
                c1, c2 = st.columns(2)
                c1.plotly_chart(result.charts['radar'], use_container_width=True)
                c2.plotly_chart(result.charts['valuation'], use_container_width=True)
                
                st.plotly_chart(result.charts['bars'], use_container_width=True)
                
                # Multi comparison chart
                multi = st.session_state.chart_service.create_multi_comparison(tickers_list)
                if multi:
                    st.plotly_chart(multi, use_container_width=True)
    
    # OpenBB Comparison Table
    st.markdown("---")
    st.subheader("📊 Tabla de Comparación (Estilo OpenBB)")
    
    if len(tickers_list) >= 2:
        comp_df = st.session_state.openbb.compare_tickers(tickers_list)
        if comp_df is not None:
            st.dataframe(
                comp_df.style.format({
                    'Price': '${:.2f}',
                    'Market Cap (B)': '${:.1f}B',
                    'P/E': '{:.1f}',
                    'P/S': '{:.1f}',
                    'P/B': '{:.1f}',
                    'EV/EBITDA': '{:.1f}',
                    'Dividend Yield': '{:.2f}%',
                    'Gross Margin': '{:.1f}%',
                    'Net Margin': '{:.1f}%',
                    'ROE': '{:.1f}%',
                    'Debt/Equity': '{:.1f}',
                }),
                use_container_width=True
            )

# ============================================================================
# TAB 6: OPTIMIZER
# ============================================================================

with tabs[5]:
    st.header("⚖️ Portfolio Optimizer (Markowitz)")
    st.caption("Optimización científica usando Modern Portfolio Theory")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        opt_tickers = st.text_input("Activos a optimizar (comma sep)", "AAPL, MSFT, GOOGL, AMZN, NVDA")
        opt_list = [t.strip().upper() for t in opt_tickers.split(",") if t.strip()]
        
        capital = st.number_input("Capital a invertir (€)", min_value=100, value=10000, step=500)
        
        strategy = st.selectbox(
            "Estrategia de Optimización",
            ["max_sharpe", "min_volatility", "efficient_return"],
            format_func=lambda x: {
                "max_sharpe": "🎯 Maximizar Sharpe Ratio (Retorno/Riesgo)",
                "min_volatility": "🛡️ Minimizar Volatilidad",
                "efficient_return": "📈 Retorno Objetivo"
            }[x]
        )
    
    with col2:
        st.info("""
        **Estrategias:**
        - **Max Sharpe**: Mejor ratio retorno/riesgo
        - **Min Vol**: Portfolio más conservador
        - **Efficient**: Target de retorno específico
        """)
    
    if len(opt_list) >= 2 and st.button("🧮 OPTIMIZAR PORTFOLIO", use_container_width=True):
        with st.spinner("Calculando Frontera Eficiente..."):
            result, msg = st.session_state.optimizer.optimize(
                opt_list, 
                total_capital=capital,
                strategy=strategy
            )
            
            if result:
                st.session_state.optimization_result = result
                st.success(msg)
                
                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Retorno Esperado", f"{result.expected_return*100:.1f}%")
                c2.metric("Volatilidad", f"{result.volatility*100:.1f}%")
                c3.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}")
                
                # Allocation
                st.subheader("💶 Asignación Óptima")
                
                col_pie, col_table = st.columns([1, 1])
                
                with col_pie:
                    fig = create_portfolio_pie_chart(result.allocation)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_table:
                    alloc_df = pd.DataFrame([
                        {'Ticker': k, 'Capital (€)': v, 'Peso (%)': f"{result.weights[k]*100:.1f}%"}
                        for k, v in result.allocation.items()
                    ])
                    st.dataframe(alloc_df, use_container_width=True)
                
                # Efficient Frontier
                st.subheader("📈 Frontera Eficiente")
                frontier = st.session_state.optimizer.get_efficient_frontier_points(opt_list)
                if frontier is not None:
                    fig = create_efficient_frontier_chart(
                        frontier, 
                        (result.expected_return, result.volatility)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Correlation Matrix
                if result.correlation_matrix is not None:
                    st.subheader("🔗 Matriz de Correlación")
                    fig = px.imshow(
                        result.correlation_matrix,
                        text_auto='.2f',
                        color_continuous_scale='RdYlGn_r',
                        title='Correlación entre activos'
                    )
                    fig.update_layout(template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(msg)

# ============================================================================
# TAB 6: COMITÉ
# ============================================================================

with tabs[6]:  # Actualizado de tabs[5] a tabs[6]
    st.header("🦈 Auditoría Institucional")
    st.caption(f"Macro: {macro.brief}")
    
    # === SELECTOR DE MODO (NUEVO) ===
    col_info, col_mode = st.columns([3, 1])
    with col_info:
        st.info("📚 Sube el Annual Report (PDF) en la pestaña DOCS para análisis completo")
    with col_mode:
        modo_analisis = st.radio(
            "Perfil del Analista:",
            ["Institucional", "Alpha (Small Cap)"],
            index=0,
            help="Institucional: Análisis macro y preservación de capital. Alpha: Skin in the game y ROCE"
        )
    
    # Mapear la elección al código
    mode_key = "small_cap" if "Alpha" in modo_analisis else "standard"
    # ================================
    
    # Enrich with library wisdom
    library_context = ""
    if st.session_state.library.is_loaded:
        st.success("📚 La biblioteca de sabiduría enriquecerá el análisis")
        library_context = st.session_state.library.get_wisdom_for_topic("valuation")
    
    if not st.session_state.oraculo.is_loaded:
        st.warning("⚠️ Para Small Caps es CRÍTICO que subas el 10-K en DOCS")
    
    if st.button("🔥 AUDITAR", use_container_width=True, type="primary"):
        with st.spinner(f"Auditando con perfil {modo_analisis}... (60-90s)"):
            ctx = st.session_state.oraculo.get_financial_context() if st.session_state.oraculo.is_loaded else {}
            
            # Enrich context with library wisdom
            if library_context:
                ctx['wisdom'] = library_context
            
            # Ejecutar con el modo seleccionado
            result = st.session_state.committee.run_audit(
                ticker, 
                macro.brief, 
                ctx,
                mode=mode_key  # <--- Pasamos el modo aquí
            )
            
            st.session_state.debate_value = result.value_audit
            st.session_state.debate_growth = result.growth_audit
            st.session_state.debate_risk = result.risk_audit
            st.session_state.debate_raw = result.raw_debate
            st.success(f"✅ Auditoría completada con perfil {modo_analisis}")
    
    if st.session_state.debate_raw:
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("<div class='audit-value'>", unsafe_allow_html=True)
            st.subheader("💰 VALUE AUDIT")
            st.write(st.session_state.debate_value)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with c2:
            st.markdown("<div class='audit-growth'>", unsafe_allow_html=True)
            st.subheader("🚀 GROWTH AUDIT")
            st.write(st.session_state.debate_growth)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with c3:
            st.markdown("<div class='audit-risk'>", unsafe_allow_html=True)
            st.subheader("💀 RISK AUDIT")
            st.write(st.session_state.debate_risk)
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 8: VEREDICTO
# ============================================================================

with tabs[7]:
    st.header("⚖️ Veredicto Final")
    
    if not st.session_state.debate_raw:
        st.info("Ejecuta la auditoría primero en la pestaña COMITÉ")
    else:
        if st.button("⚖️ EMITIR SENTENCIA (10.000€)", use_container_width=True):
            with st.spinner("El CIO está deliberando..."):
                result = st.session_state.committee.run_verdict(ticker, st.session_state.debate_raw)
                st.session_state.veredicto_final = result.cio_verdict
                st.session_state.allocation_final = result.pm_allocation
                
                # Save to history
                data = {
                    'ticker': ticker, 
                    'timestamp': datetime.now().isoformat(),
                    'macro': macro.brief,
                    'value_audit': st.session_state.debate_value,
                    'growth_audit': st.session_state.debate_growth,
                    'risk_audit': st.session_state.debate_risk,
                    'cio_verdict': result.cio_verdict,
                    'pm_allocation': result.pm_allocation
                }
                st.session_state.session_manager.save_debate(ticker, data)
        
        if st.session_state.veredicto_final:
            st.subheader("🏛️ VEREDICTO DEL CIO")
            st.write(st.session_state.veredicto_final)
            
            st.markdown("<div class='allocation-box'>", unsafe_allow_html=True)
            st.subheader("💶 ALLOCATION")
            st.write(st.session_state.allocation_final)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # === EXPORT SECTION ===
            st.markdown("---")
            st.subheader("🖨️ Exportar Reporte")
            
            col_pdf, col_html = st.columns(2)
            
            with col_pdf:
                # PDF Download
                pdf = st.session_state.pdf_generator.create_investment_memo(
                    ticker, st.session_state.veredicto_final, st.session_state.allocation_final,
                    macro.brief, st.session_state.debate_value, st.session_state.debate_growth,
                    st.session_state.debate_risk
                )
                st.download_button("📄 Descargar PDF", pdf, f"Memo_{ticker}.pdf", "application/pdf", use_container_width=True)
            
            with col_html:
                # HTML Report (FinRobot Style)
                f = st.session_state.market_service.get_fundamentals(ticker)
                sent = st.session_state.sentiment_analyzer.analyze(ticker)
                
                if f:
                    html_report = st.session_state.renderer.render(
                        ticker=ticker,
                        price=f.price,
                        veredicto=st.session_state.veredicto_final,
                        debate=st.session_state.debate_raw,
                        fundamentals=f.__dict__,
                        sentiment=sent.overall_sentiment,
                        value_audit=st.session_state.debate_value,
                        growth_audit=st.session_state.debate_growth,
                        risk_audit=st.session_state.debate_risk,
                        macro_context=macro.brief,
                        allocation=st.session_state.allocation_final
                    )
                    
                    st.markdown(
                        st.session_state.renderer.get_download_link(html_report, f"{ticker}_Research_Report"),
                        unsafe_allow_html=True
                    )
            
            # Tip for PDF
            st.markdown(st.session_state.renderer.get_pdf_download_link("", ticker), unsafe_allow_html=True)

# ============================================================================
# TAB 9: BIBLIOTECA
# ============================================================================

with tabs[8]:
    st.header("📚 Biblioteca de Sabiduría")
    st.caption("Sube libros de inversión para enriquecer el análisis de la IA")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Añadir Libro")
        book_file = st.file_uploader("Subir libro (PDF, EPUB, MOBI, TXT)", type=['pdf', 'txt', 'md', 'epub', 'mobi'])
        book_title = st.text_input("Título del libro", "")
        book_author = st.text_input("Autor", "")
        book_topics = st.text_input("Temas (comma sep)", "value investing, analysis")
        
        if book_file and book_title and book_author:
            if st.button("📚 Indexar Libro"):
                with st.spinner("Indexando..."):
                    topics = [t.strip() for t in book_topics.split(",")]
                    n, msg = st.session_state.library.add_book(
                        book_file, book_title, book_author, topics
                    )
                    if n > 0:
                        st.success(msg)
                    else:
                        st.error(msg)
    
    with col2:
        st.subheader("📖 Libros Indexados")
        books = st.session_state.library.books
        
        if books:
            for book in books:
                with st.expander(f"📕 {book.title} - {book.author}"):
                    st.write(f"**Chunks:** {book.num_chunks}")
                    st.write(f"**Temas:** {', '.join(book.topics)}")
                    st.write(f"**Indexado:** {book.indexed_at[:10]}")
        else:
            st.info("No hay libros indexados aún")
            if st.button("🧠 Cargar Sabiduría Básica"):
                with st.spinner("Cargando Buffett, Munger, Graham..."):
                    n = add_essential_wisdom(st.session_state.library)
                    st.success(f"✅ {n} fuentes añadidas")
                    st.rerun()
    
    st.markdown("---")
    st.subheader("🔍 Buscar en la Biblioteca")
    
    search_query = st.text_input("¿Qué quieres saber de los grandes inversores?")
    if search_query:
        results = st.session_state.library.search(search_query, k=3)
        
        if results:
            for r in results:
                st.markdown(f"""
                **📖 {r.source}** ({r.author})
                
                > "{r.content[:400]}..."
                
                ---
                """)
        else:
            st.info("No se encontraron resultados. Añade más libros.")

# ============================================================================
# TAB 10: MENTOR
# ============================================================================

with tabs[9]:
    st.header("👨🏫 Learning Oracle")
    
    st.subheader("💡 Preguntas Sugeridas")
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS['general'][:3]):
        if cols[i % 3].button(q[:40] + "...", key=f"q_{i}"):
            st.session_state['mq'] = q
    
    question = st.text_input("Tu pregunta:", st.session_state.get('mq', ''))
    
    if question and st.button("🎓 Consultar"):
        with st.spinner("El mentor está pensando..."):
            # Get context from doc if available
            doc_ctx = ""
            if st.session_state.oraculo.is_loaded:
                doc_ctx = st.session_state.oraculo.search(question)
            
            # Get context from library
            lib_ctx = st.session_state.library.search_with_context(question, k=2)
            
            # Combine contexts
            full_ctx = f"""
            === DOCUMENTO CARGADO ===
            {doc_ctx if doc_ctx else 'No hay documento cargado'}
            
            === BIBLIOTECA DE SABIDURÍA ===
            {lib_ctx if lib_ctx else 'Biblioteca vacía'}
            """
            
            resp = st.session_state.mentor.explain(question, full_ctx)
            st.markdown(
                f"<div style='background:#001a33;padding:20px;border-radius:8px'>{resp}</div>", 
                unsafe_allow_html=True
            )

# ============================================================================
# TAB 11: DOCS
# ============================================================================

with tabs[10]:
    st.header("📂 Documentos 10-K/10-Q")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📤 Subir Documento")
        up = st.file_uploader("10-K/10-Q (HTML, PDF, TXT)", type=['html', 'htm', 'pdf', 'txt'])
        
        if up and st.button("⚙️ Procesar Documento"):
            with st.spinner("Indexando documento..."):
                n, s = st.session_state.oraculo.ingest(up)
                st.session_state.active_doc_name = up.name
                st.session_state.doc_structure = s
                st.success(f"✅ {n} chunks indexados")
    
    with c2:
        st.subheader("🔍 Búsqueda Rápida por Sección")
        
        sections = ['balance', 'income', 'cashflow', 'risks', 'mda', 'rnd', 'guidance']
        cols = st.columns(4)
        
        for i, section in enumerate(sections):
            if cols[i % 4].button(section.upper(), key=f"sec_{section}"):
                result = st.session_state.oraculo.search_section(section)
                st.write(result)
    
    # History
    st.markdown("---")
    st.subheader("📜 Historial de Análisis")
    
    debates = st.session_state.session_manager.load_debates(limit=5)
    if debates:
        for d in debates:
            with st.expander(f"{d.get('ticker')} - {d.get('timestamp','')[:10]}"):
                st.write(d.get('cio_verdict', '')[:300] + "...")
                if st.button("Cargar", key=d['_filename']):
                    st.session_state.debate_raw = "loaded"
                    st.session_state.veredicto_final = d.get('cio_verdict')
                    st.session_state.allocation_final = d.get('pm_allocation')
                    st.rerun()
    else:
        st.info("Sin historial de análisis")

# ============================================================================
# TAB 12: SEC FILINGS ANALYZER (FinRobot-inspired)
# ============================================================================

with tabs[11]:
    st.header("📄 SEC Filings Analyzer")
    st.caption("Análisis automático de 10-K, 10-Q y otros documentos SEC • Inspirado en FinRobot")
    
    sec = st.session_state.sec_analyzer
    
    # Búsqueda de filings
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_ticker = st.text_input("🔍 Buscar filings por ticker", ticker, key="sec_ticker")
    
    with col2:
        form_types = st.multiselect(
            "Tipo de filing",
            ["10-K", "10-Q", "8-K", "DEF 14A"],
            default=["10-K", "10-Q"]
        )
    
    if st.button("🔍 Buscar Filings", key="search_sec"):
        with st.spinner("Buscando en SEC EDGAR..."):
            filings = sec.get_recent_filings(search_ticker, form_types)
            st.session_state['sec_filings_list'] = filings
    
    # Mostrar filings encontrados
    if 'sec_filings_list' in st.session_state and st.session_state['sec_filings_list']:
        filings = st.session_state['sec_filings_list']
        
        st.subheader(f"📋 Filings de {search_ticker} ({len(filings)} encontrados)")
        
        # Tabla de filings
        for i, f in enumerate(filings[:8]):
            icon = get_filing_icon(f['form_type'])
            date_fmt = format_filing_date(f['filing_date'])
            
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"{icon} **{f['form_type']}** - {date_fmt}")
            col2.write(f"📄 {f['primary_document'][:30]}...")
            
            if col3.button("📥 Analizar", key=f"analyze_{i}"):
                st.session_state['selected_filing'] = f
                st.session_state['filing_analyzed'] = None
    
    # Análisis del filing seleccionado
    if 'selected_filing' in st.session_state and st.session_state['selected_filing']:
        selected = st.session_state['selected_filing']
        
        st.markdown("---")
        st.subheader(f"📊 Analizando: {selected['form_type']} ({format_filing_date(selected['filing_date'])})")
        
        # Descargar y analizar
        if 'filing_analyzed' not in st.session_state or st.session_state['filing_analyzed'] is None:
            with st.spinner("🔄 Descargando y analizando filing (puede tardar 30-60 segundos)..."):
                filing = sec.download_filing(selected)
                
                if filing:
                    # Análisis con LLM
                    analyzed = sec.analyze_filing(filing)
                    st.session_state['filing_analyzed'] = analyzed
                    st.rerun()
                else:
                    st.error("❌ Error descargando el filing")
        
        # Mostrar análisis
        if 'filing_analyzed' in st.session_state and st.session_state['filing_analyzed']:
            analyzed = st.session_state['filing_analyzed']
            
            # Layout en columnas
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Resumen Ejecutivo
                st.markdown("### 📋 Resumen Ejecutivo")
                if analyzed.executive_summary:
                    st.info(analyzed.executive_summary)
                else:
                    st.warning("No se pudo generar resumen")
                
                # Análisis completo
                if analyzed.metrics.get('full_analysis'):
                    with st.expander("📖 Ver Análisis Completo", expanded=False):
                        st.markdown(analyzed.metrics['full_analysis'])
            
            with col2:
                # Red Flags
                st.markdown("### 🔴 Red Flags")
                if analyzed.red_flags:
                    for flag in analyzed.red_flags[:5]:
                        st.warning(f"⚠️ {flag}")
                else:
                    st.success("✅ Sin red flags significativos")
                
                # Key Insights
                st.markdown("### 💡 Key Insights")
                if analyzed.key_insights:
                    for insight in analyzed.key_insights[:5]:
                        st.write(f"• {insight}")
            
            # Bull vs Bear
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🐂 Bull Case")
                bull = analyzed.metrics.get('bull_case', 'No disponible')
                st.success(bull if bull else "No disponible")
            
            with col2:
                st.markdown("### 🐻 Bear Case")
                bear = analyzed.metrics.get('bear_case', 'No disponible')
                st.error(bear if bear else "No disponible")
            
            # Secciones del documento
            st.markdown("---")
            st.markdown("### 📑 Secciones del Documento")
            
            sec_tabs = st.tabs(["Business", "Risk Factors", "MD&A", "Financials"])
            
            with sec_tabs[0]:
                if analyzed.business_description:
                    st.text_area("Business Description", analyzed.business_description[:5000], height=300)
                else:
                    st.info("Sección no encontrada")
            
            with sec_tabs[1]:
                if analyzed.risk_factors:
                    st.text_area("Risk Factors", analyzed.risk_factors[:5000], height=300)
                else:
                    st.info("Sección no encontrada")
            
            with sec_tabs[2]:
                if analyzed.md_and_a:
                    st.text_area("Management Discussion & Analysis", analyzed.md_and_a[:5000], height=300)
                else:
                    st.info("Sección no encontrada")
            
            with sec_tabs[3]:
                if analyzed.financial_statements:
                    st.text_area("Financial Statements", analyzed.financial_statements[:5000], height=300)
                else:
                    st.info("Sección no encontrada")
            
            # Botón para indexar en Oráculo
            st.markdown("---")
            if st.button("🧠 Indexar en Base de Conocimiento", key="index_sec"):
                with st.spinner("Indexando filing..."):
                    # Crear contenido para indexar
                    content = f"""
                    {analyzed.form_type} - {analyzed.ticker} ({analyzed.filing_date})
                    
                    RESUMEN: {analyzed.executive_summary}
                    
                    BUSINESS: {analyzed.business_description[:3000] if analyzed.business_description else ''}
                    
                    RISKS: {analyzed.risk_factors[:3000] if analyzed.risk_factors else ''}
                    
                    MD&A: {analyzed.md_and_a[:3000] if analyzed.md_and_a else ''}
                    """
                    # Aquí se podría añadir al OraculoV8
                    st.success(f"✅ Filing indexado. Ahora puedes hacer preguntas sobre este documento.")
    
    else:
        # Instrucciones iniciales
        st.markdown("""
        ### 📚 ¿Cómo usar el SEC Analyzer?
        
        1. **Busca** por ticker (ej: AAPL, TSLA, MSFT)
        2. **Selecciona** el tipo de filing (10-K anual, 10-Q trimestral)
        3. **Analiza** el documento automáticamente con IA
        4. **Aprende** de los insights, red flags y recomendaciones
        
        ---
        
        #### 📖 ¿Qué es cada tipo de filing?
        
        | Filing | Descripción |
        |--------|-------------|
        | **10-K** | Informe anual completo (estados financieros, riesgos, estrategia) |
        | **10-Q** | Informe trimestral (actualización financiera) |
        | **8-K** | Eventos importantes (adquisiciones, cambios ejecutivos) |
        | **DEF 14A** | Proxy statement (compensación ejecutivos, votaciones) |
        
        ---
        
        💡 **Tip:** Los 10-K son los más completos y útiles para análisis fundamental profundo.
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🏛️ **Sindicato V8 ELITE** | Chain of Thought • Markowitz Optimizer • Knowledge Library • SEC Analyzer | Capital Preservation First")
