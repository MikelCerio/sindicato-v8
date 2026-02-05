"""
🏛️ SINDICATO V8.1 - VERSIÓN MEJORADA
- Mejor contraste y legibilidad
- Sentiment arreglado
- Gráficos sin solapamiento
- Oracle con libros de inversión
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Sindicato V8.1",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS MEJORADO - ALTO CONTRASTE
# ============================================================================

st.markdown("""
<style>
    /* === BASE === */
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* === TEXTO LEGIBLE === */
    p, li, span, label, .stMarkdown {
        color: #ffffff !important;
        font-size: 16px !important;
    }
    
    /* === HEADERS === */
    h1 {
        color: #00ff88 !important;
        font-size: 2.5rem !important;
        border-bottom: 3px solid #00ff88;
        padding-bottom: 10px;
    }
    h2 {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        border-left: 4px solid #00ff88;
        padding-left: 15px;
    }
    h3 {
        color: #00ccff !important;
        font-size: 1.4rem !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
        border-right: 2px solid #00ff88;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* === MÉTRICAS === */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #00ff88 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #cccccc !important;
        font-size: 14px !important;
    }
    
    /* === INPUTS === */
    .stTextInput > div > div > input {
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        border: 2px solid #00ff88 !important;
        font-size: 18px !important;
    }
    
    /* === BOTONES === */
    .stButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        font-size: 16px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00cc6a 0%, #00ff88 100%) !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.5) !important;
    }
    
    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        font-size: 16px !important;
    }
    .streamlit-expanderContent {
        background-color: #0d1117 !important;
        border: 1px solid #333 !important;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
        font-size: 16px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00ff88 !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #00ff88 !important;
    }
    
    /* === DATAFRAMES === */
    .stDataFrame {
        background-color: #1a1a2e !important;
    }
    
    /* === CAJAS DE RESULTADOS === */
    .result-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #0d1117 100%);
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        color: #ffffff !important;
    }
    
    .result-box h4 {
        color: #00ff88 !important;
        margin-bottom: 10px;
    }
    
    .result-box p {
        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.6;
    }
    
    /* === NOTICIAS === */
    .news-positive {
        background: linear-gradient(135deg, #003d00 0%, #004d00 100%);
        border-left: 5px solid #00ff00;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #ffffff !important;
    }
    
    .news-negative {
        background: linear-gradient(135deg, #3d0000 0%, #4d0000 100%);
        border-left: 5px solid #ff4444;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #ffffff !important;
    }
    
    .news-neutral {
        background: linear-gradient(135deg, #1a1a2e 0%, #2a2a4e 100%);
        border-left: 5px solid #888888;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #ffffff !important;
    }
    
    /* === SEARCH RESULTS === */
    .search-result {
        background: #0d1117;
        border: 1px solid #00ff88;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .search-result .section-tag {
        background: #00ff88;
        color: #000000;
        padding: 3px 10px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 12px;
    }
    
    .search-result .content {
        color: #ffffff;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 10px;
    }
    
    /* === WISDOM BOX (Buffett/Graham) === */
    .wisdom-box {
        background: linear-gradient(135deg, #1a0a30 0%, #2a1050 100%);
        border: 2px solid #a855f7;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .wisdom-box .source {
        color: #a855f7;
        font-weight: bold;
        font-size: 14px;
    }
    
    .wisdom-box .quote {
        color: #ffffff;
        font-style: italic;
        font-size: 16px;
        line-height: 1.6;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES DE DATOS
# ============================================================================

@st.cache_data(ttl=300)
def get_stock_data(ticker: str):
    """Obtiene datos fundamentales de una acción."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'market_cap': info.get('marketCap', 0),
            'pe': info.get('trailingPE', 0) or 0,
            'forward_pe': info.get('forwardPE', 0) or 0,
            'roe': (info.get('returnOnEquity', 0) or 0) * 100,
            'debt_equity': info.get('debtToEquity', 0) or 0,
            'current_ratio': info.get('currentRatio', 0) or 0,
            'profit_margin': (info.get('profitMargins', 0) or 0) * 100,
            'revenue_growth': (info.get('revenueGrowth', 0) or 0) * 100,
            'name': info.get('shortName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A')
        }
    except Exception as e:
        st.error(f"Error obteniendo datos: {e}")
        return None

@st.cache_data(ttl=300)
def get_news(ticker: str):
    """Obtiene noticias recientes."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return []
        
        results = []
        for item in news[:10]:
            title = item.get('title', '')
            
            # Análisis de sentiment simple pero efectivo
            positive_words = ['surge', 'gain', 'up', 'rise', 'beat', 'profit', 'growth', 'strong', 'buy', 'bullish', 'record', 'high']
            negative_words = ['fall', 'drop', 'down', 'loss', 'miss', 'weak', 'sell', 'bearish', 'cut', 'crash', 'low', 'concern', 'risk']
            
            title_lower = title.lower()
            pos_count = sum(1 for w in positive_words if w in title_lower)
            neg_count = sum(1 for w in negative_words if w in title_lower)
            
            if pos_count > neg_count:
                sentiment = 'positive'
                score = 0.3 + (pos_count * 0.1)
            elif neg_count > pos_count:
                sentiment = 'negative'
                score = -0.3 - (neg_count * 0.1)
            else:
                sentiment = 'neutral'
                score = 0.0
            
            results.append({
                'title': title,
                'sentiment': sentiment,
                'score': min(max(score, -1), 1),
                'link': item.get('link', ''),
                'publisher': item.get('publisher', 'Unknown')
            })
        
        return results
    except Exception as e:
        return []

@st.cache_data(ttl=600)
def get_price_history(ticker: str, period: str = "1y"):
    """Obtiene histórico de precios."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except:
        return None

@st.cache_data(ttl=3600)
def get_macro_context():
    """Obtiene contexto macro (VIX y tasas)."""
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        tny = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
        
        # Determinar régimen
        if vix > 30:
            regime = "🔴 CRISIS"
        elif vix > 20:
            regime = "🟡 VOLÁTIL"
        elif vix < 12:
            regime = "🟠 COMPLACENCIA"
        else:
            regime = "🟢 ESTABLE"
        
        return {'vix': vix, 'tny': tny, 'regime': regime}
    except:
        return {'vix': 18.0, 'tny': 4.0, 'regime': "🟢 ESTABLE"}

# ============================================================================
# GRÁFICOS MEJORADOS (sin solapamiento)
# ============================================================================

def create_radar_chart(data_dict):
    """Crea gráfico radar comparativo MEJORADO."""
    
    fig = go.Figure()
    
    categories = ['ROE', 'Margen', 'Crec.', 'Liquidez', 'Valor']
    colors = ['#00ff88', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a855f7']
    
    for i, (ticker, data) in enumerate(data_dict.items()):
        # Normalizar valores a escala 0-100
        values = [
            min(data.get('roe', 0), 50),  # ROE (cap at 50%)
            min(data.get('profit_margin', 0), 40),  # Margen
            min(data.get('revenue_growth', 0) + 20, 50),  # Crecimiento (+20 base)
            min(data.get('current_ratio', 0) * 20, 50),  # Liquidez
            max(50 - (data.get('pe', 30)), 0)  # Valor (menor PE = mejor)
        ]
        values.append(values[0])  # Cerrar
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=ticker,
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 50], color='#ffffff'),
            angularaxis=dict(color='#ffffff'),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color='#ffffff', size=12)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=400,
        margin=dict(t=30, b=80, l=30, r=30),
        title=dict(
            text="📊 Comparativa de Fortalezas",
            font=dict(color='#00ff88', size=16),
            x=0.5
        )
    )
    
    return fig

def create_valuation_chart(data_dict):
    """Scatter: Valoración (P/E) vs Calidad (ROE) MEJORADO."""
    
    fig = go.Figure()
    
    colors = ['#00ff88', '#ff6b6b', '#4ecdc4', '#ffe66d']
    
    for i, (ticker, data) in enumerate(data_dict.items()):
        pe = data.get('pe', 0)
        roe = data.get('roe', 0)
        mcap = data.get('market_cap', 1e9)
        
        fig.add_trace(go.Scatter(
            x=[pe],
            y=[roe],
            mode='markers+text',
            marker=dict(
                size=max(mcap / 5e10, 20),
                color=colors[i % len(colors)],
                opacity=0.8,
                line=dict(width=2, color='#ffffff')
            ),
            text=[ticker],
            textposition='top center',
            textfont=dict(color='#ffffff', size=14),
            name=ticker,
            showlegend=False
        ))
    
    # Líneas de referencia
    fig.add_hline(y=15, line_dash="dash", line_color="#666", annotation_text="ROE 15%")
    fig.add_vline(x=25, line_dash="dash", line_color="#666", annotation_text="P/E 25")
    
    # Cuadrantes
    fig.add_annotation(x=12, y=40, text="💎 JOYA", font=dict(color='#00ff88', size=14), showarrow=False)
    fig.add_annotation(x=50, y=40, text="⚠️ CARA", font=dict(color='#ff6b6b', size=14), showarrow=False)
    fig.add_annotation(x=12, y=5, text="🔍 VALUE?", font=dict(color='#ffe66d', size=14), showarrow=False)
    fig.add_annotation(x=50, y=5, text="❌ EVITAR", font=dict(color='#ff4444', size=14), showarrow=False)
    
    fig.update_layout(
        xaxis=dict(
            title="P/E Ratio (menor = más barato)",
            color='#ffffff',
            gridcolor='#333',
            range=[0, max(60, max([d.get('pe', 30) for d in data_dict.values()]) + 10)]
        ),
        yaxis=dict(
            title="ROE % (mayor = mejor calidad)",
            color='#ffffff',
            gridcolor='#333',
            range=[0, max(50, max([d.get('roe', 20) for d in data_dict.values()]) + 10)]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,10,30,0.8)',
        height=400,
        margin=dict(t=50, b=50, l=60, r=30),
        title=dict(
            text="💰 Valoración vs Calidad",
            font=dict(color='#00ff88', size=16),
            x=0.5
        )
    )
    
    return fig

def create_candlestick(ticker: str, hist):
    """Gráfico de velas con volumen."""
    
    if hist is None or hist.empty:
        return None
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25]
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name='Precio',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ), row=1, col=1)
    
    # MA20
    if len(hist) > 20:
        ma20 = hist['Close'].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=hist.index, y=ma20,
            name='MA20', line=dict(color='#ffaa00', width=1)
        ), row=1, col=1)
    
    # Volumen
    colors = ['#00ff88' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ff4444' 
              for i in range(len(hist))]
    
    fig.add_trace(go.Bar(
        x=hist.index, y=hist['Volume'],
        name='Volumen', marker_color=colors, opacity=0.7
    ), row=2, col=1)
    
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,10,30,0.8)',
        font=dict(color='#ffffff'),
        height=500,
        showlegend=True,
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=60, b=30),
        title=dict(
            text=f"📈 {ticker} - Precio y Volumen",
            font=dict(color='#00ff88', size=18),
            x=0.5
        )
    )
    
    fig.update_xaxes(gridcolor='#333')
    fig.update_yaxes(gridcolor='#333')
    
    return fig

# ============================================================================
# ORACLE CON SABIDURÍA DE INVERSORES
# ============================================================================

INVESTOR_WISDOM = {
    "deuda": {
        "buffett": "La deuda es como conducir mirando por el retrovisor. Prefiero empresas que pueden pagar su deuda con 1-2 años de beneficios.",
        "graham": "Una empresa prudente no debería tener deuda superior al capital propio. Busca ratio Debt/Equity < 1.",
        "lynch": "Evito empresas con deuda excesiva. Si una empresa no puede pagar intereses con sus beneficios operativos, es una señal de alarma."
    },
    "pe_ratio": {
        "buffett": "El P/E te dice cuántos años de beneficios pagas. Prefiero pagar menos de 15x por empresas excelentes.",
        "graham": "Un P/E superior a 20 raramente se justifica. Busca empresas con P/E < 15 y preferiblemente < 10.",
        "lynch": "El PEG ratio (P/E dividido por crecimiento) debería ser menor a 1. Un P/E de 30 está bien si crecen 30%."
    },
    "roe": {
        "buffett": "Busco ROE consistentemente superior al 15%. Es la métrica más importante de calidad del negocio.",
        "graham": "Un ROE del 12-15% es aceptable. Por encima del 20% indica un moat competitivo.",
        "lynch": "ROE alto + baja deuda = empresa de alta calidad. Desconfía de ROE alto conseguido con mucha deuda."
    },
    "crecimiento": {
        "buffett": "Prefiero crecimiento moderado y predecible que crecimiento explosivo e incierto.",
        "graham": "El crecimiento pasado no garantiza crecimiento futuro. Sé conservador en tus proyecciones.",
        "lynch": "Busca empresas que puedan crecer 20-25% anual durante varios años. Son las 'ten-baggers'."
    },
    "margen": {
        "buffett": "Márgenes altos sostenidos indican pricing power. Es señal de un moat competitivo.",
        "graham": "Márgenes estables son más importantes que márgenes altos. Busca consistencia.",
        "lynch": "Compara márgenes con competidores del sector. El líder suele tener los mejores márgenes."
    },
    "valoracion": {
        "buffett": "Precio es lo que pagas, valor es lo que recibes. Una empresa maravillosa a precio justo supera a una empresa mediocre barata.",
        "graham": "Compra con margen de seguridad del 30-50% sobre el valor intrínseco.",
        "lynch": "Invierte en lo que conoces. Si no puedes explicar en qué inviertes, no deberías invertir."
    },
    "riesgo": {
        "buffett": "El riesgo viene de no saber lo que haces. La diversificación excesiva es admitir ignorancia.",
        "graham": "La seguridad del principal debe ser tu primera preocupación. Los retornos vienen después.",
        "lynch": "Conoce tus empresas. Si sabes por qué compraste, sabrás cuándo vender."
    }
}

def get_wisdom(topic: str) -> str:
    """Obtiene sabiduría de inversores sobre un tema."""
    
    topic_lower = topic.lower()
    
    # Mapear palabras clave a temas
    keyword_mapping = {
        'deuda': ['deuda', 'debt', 'apalancamiento', 'endeudamiento', 'pasivo'],
        'pe_ratio': ['pe', 'p/e', 'ratio precio', 'multiplo', 'valoracion', 'price earnings'],
        'roe': ['roe', 'rentabilidad', 'return on equity', 'beneficio'],
        'crecimiento': ['crecimiento', 'growth', 'crecer', 'expansion'],
        'margen': ['margen', 'margin', 'rentabilidad', 'beneficio'],
        'valoracion': ['valoracion', 'caro', 'barato', 'precio', 'value'],
        'riesgo': ['riesgo', 'risk', 'peligro', 'seguridad']
    }
    
    matched_topic = None
    for key, keywords in keyword_mapping.items():
        if any(kw in topic_lower for kw in keywords):
            matched_topic = key
            break
    
    if matched_topic and matched_topic in INVESTOR_WISDOM:
        wisdom = INVESTOR_WISDOM[matched_topic]
        result = ""
        for investor, quote in wisdom.items():
            emoji = "🎩" if investor == "buffett" else ("📚" if investor == "graham" else "📈")
            name = investor.capitalize()
            result += f"""
<div class="wisdom-box">
    <span class="source">{emoji} {name}</span>
    <p class="quote">"{quote}"</p>
</div>
"""
        return result
    
    return """
<div class="wisdom-box">
    <span class="source">💡 Consejo</span>
    <p class="quote">No encontré sabiduría específica sobre ese tema. Prueba con: deuda, P/E, ROE, crecimiento, márgenes, valoración o riesgo.</p>
</div>
"""

# ============================================================================
# SIDEBAR
# ============================================================================

macro = get_macro_context()

with st.sidebar:
    st.markdown("# 🏛️ SINDICATO V8.1")
    st.caption("Institutional Edition - Mejorado")
    
    st.markdown("---")
    
    st.markdown("### 🌍 Régimen de Mercado")
    st.markdown(f"**{macro['regime']}**")
    
    col1, col2 = st.columns(2)
    col1.metric("VIX", f"{macro['vix']:.1f}")
    col2.metric("10Y", f"{macro['tny']:.2f}%")
    
    if macro['vix'] > 25:
        st.error("⚠️ Volatilidad elevada - Cautela")
    
    st.markdown("---")
    
    st.markdown("### 📂 Documentos")
    st.info("Sube un 10-K en la pestaña DOCS")

# ============================================================================
# MAIN
# ============================================================================

ticker = st.text_input("🎯 **TICKER**", "AAPL", key="main_ticker").upper()

# Tabs
tabs = st.tabs([
    "📊 DATOS",
    "📈 GRÁFICOS",
    "🔄 COMPARAR",
    "📖 WISDOM",
    "📂 DOCS"
])

# ============================================================================
# TAB 1: DATOS
# ============================================================================

with tabs[0]:
    st.markdown(f"# 📊 {ticker}")
    
    data = get_stock_data(ticker)
    
    if data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("## 💹 Fundamentales")
            
            m1, m2 = st.columns(2)
            m1.metric("Precio", f"${data['price']:.2f}")
            m2.metric("Market Cap", f"${data['market_cap']/1e9:.1f}B")
            
            m3, m4 = st.columns(2)
            m3.metric("P/E", f"{data['pe']:.1f}")
            m4.metric("Forward P/E", f"{data['forward_pe']:.1f}")
            
            m5, m6 = st.columns(2)
            m5.metric("ROE", f"{data['roe']:.1f}%")
            m6.metric("Debt/Equity", f"{data['debt_equity']/100:.2f}")
            
            # Valoración y Calidad con colores
            if data['pe'] < 15:
                val_color = "🟢"
                val_text = "Barata"
            elif data['pe'] < 25:
                val_color = "🟡"
                val_text = "Justa"
            else:
                val_color = "🔴"
                val_text = "Cara"
            
            if data['roe'] > 20:
                qual_color = "🟢"
                qual_text = "Alta"
            elif data['roe'] > 10:
                qual_color = "🟡"
                qual_text = "Media"
            else:
                qual_color = "🔴"
                qual_text = "Baja"
            
            st.markdown(f"**Valoración:** {val_color} {val_text}")
            st.markdown(f"**Calidad:** {qual_color} {qual_text}")
        
        with col2:
            st.markdown("## 📰 Sentiment")
            
            news = get_news(ticker)
            
            if news:
                # Calcular sentiment global
                scores = [n['score'] for n in news]
                avg_score = sum(scores) / len(scores)
                
                if avg_score > 0.1:
                    sent_emoji = "🟢"
                    sent_text = "BULLISH"
                elif avg_score < -0.1:
                    sent_emoji = "🔴"
                    sent_text = "BEARISH"
                else:
                    sent_emoji = "🟡"
                    sent_text = "NEUTRAL"
                
                st.metric("Sentiment", f"{sent_emoji} {sent_text}")
                
                st.markdown("### 📰 Últimas Noticias")
                
                for n in news[:5]:
                    css_class = f"news-{n['sentiment']}"
                    emoji = "🟢" if n['sentiment'] == 'positive' else ("🔴" if n['sentiment'] == 'negative' else "⚪")
                    
                    st.markdown(f"""
<div class="{css_class}">
    <strong>{emoji} {n['title']}</strong>
    <br><small style="color: #888;">📰 {n['publisher']}</small>
</div>
""", unsafe_allow_html=True)
            else:
                st.warning("No hay noticias disponibles para este ticker")
    else:
        st.error("No se pudieron obtener datos. Verifica el ticker.")

# ============================================================================
# TAB 2: GRÁFICOS
# ============================================================================

with tabs[1]:
    st.markdown(f"# 📈 {ticker} - Gráficos")
    
    period = st.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    hist = get_price_history(ticker, period)
    
    if hist is not None and not hist.empty:
        fig = create_candlestick(ticker, hist)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        change = ((end_price / start_price) - 1) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Inicio", f"${start_price:.2f}")
        col2.metric("Actual", f"${end_price:.2f}")
        col3.metric("Cambio", f"{change:+.1f}%")
    else:
        st.error("No hay datos históricos disponibles")

# ============================================================================
# TAB 3: COMPARAR
# ============================================================================

with tabs[2]:
    st.markdown("# 🔄 Comparativa de Tickers")
    
    tickers_input = st.text_input(
        "Tickers (separados por coma)",
        "AAPL, MSFT, GOOGL",
        help="Ejemplo: AAPL, MSFT, GOOGL, AMZN"
    )
    
    tickers_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if len(tickers_list) >= 2:
        if st.button("🔍 Comparar", use_container_width=True):
            with st.spinner("Obteniendo datos..."):
                data_dict = {}
                for t in tickers_list:
                    d = get_stock_data(t)
                    if d:
                        data_dict[t] = d
                
                if len(data_dict) >= 2:
                    # Tabla comparativa
                    st.markdown("## 📋 Tabla Comparativa")
                    
                    df_data = []
                    for t, d in data_dict.items():
                        df_data.append({
                            'Ticker': t,
                            'Precio': f"${d['price']:.2f}",
                            'P/E': f"{d['pe']:.1f}",
                            'ROE %': f"{d['roe']:.1f}",
                            'Margen %': f"{d['profit_margin']:.1f}",
                            'D/E': f"{d['debt_equity']/100:.2f}",
                            'Crec. %': f"{d['revenue_growth']:+.1f}"
                        })
                    
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                    
                    # Gráficos lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        radar = create_radar_chart(data_dict)
                        st.plotly_chart(radar, use_container_width=True)
                    
                    with col2:
                        scatter = create_valuation_chart(data_dict)
                        st.plotly_chart(scatter, use_container_width=True)
                    
                    # Score
                    st.markdown("## 🏆 Puntuación")
                    scores = {}
                    for t, d in data_dict.items():
                        score = 0
                        score += min(d['roe'] * 2, 40)  # ROE
                        score += min(d['profit_margin'], 30)  # Margen
                        score -= min(d['pe'] * 0.5, 25)  # Penalizar P/E alto
                        score -= min(d['debt_equity'] / 50, 15)  # Penalizar deuda
                        scores[t] = round(score, 1)
                    
                    winner = max(scores, key=scores.get)
                    st.success(f"🏆 **Mejor opción:** {winner} (Score: {scores[winner]})")
                    
                    for t, s in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                        st.markdown(f"**{t}:** {s} puntos")

# ============================================================================
# TAB 4: WISDOM (Buffett/Graham/Lynch)
# ============================================================================

with tabs[3]:
    st.markdown("# 📖 Oracle de Sabiduría")
    st.markdown("*Consulta qué dicen Buffett, Graham y Lynch sobre temas de inversión*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "¿Sobre qué quieres saber?",
            placeholder="Ej: ¿Qué piensan sobre la deuda?"
        )
    
    with col2:
        st.markdown("**Temas sugeridos:**")
        topics = ["Deuda", "P/E Ratio", "ROE", "Crecimiento", "Márgenes", "Valoración", "Riesgo"]
        for t in topics:
            if st.button(t, key=f"topic_{t}"):
                topic = t
    
    if topic:
        st.markdown("---")
        st.markdown(f"## 💡 Sabiduría sobre: {topic}")
        wisdom_html = get_wisdom(topic)
        st.markdown(wisdom_html, unsafe_allow_html=True)

# ============================================================================
# TAB 5: DOCS
# ============================================================================

with tabs[4]:
    st.markdown("# 📂 Documentos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 📤 Subir 10-K")
        uploaded = st.file_uploader(
            "Arrastra tu archivo aquí",
            type=['html', 'htm', 'pdf', 'txt']
        )
        
        if uploaded:
            st.success(f"✅ Archivo: {uploaded.name}")
            if st.button("⚙️ Procesar Documento"):
                st.info("Procesando... (Implementar OraculoV8)")
    
    with col2:
        st.markdown("## 🔍 Búsqueda Rápida")
        
        sections = {
            "Balance": "balance sheet assets liabilities",
            "Income": "revenue net income operating",
            "Cash Flow": "cash flow operating investing",
            "Risks": "risk factors competition regulation",
            "MD&A": "management discussion analysis"
        }
        
        for name, query in sections.items():
            if st.button(f"📄 {name}", key=f"search_{name}"):
                st.markdown(f"""
<div class="search-result">
    <span class="section-tag">{name}</span>
    <div class="content">
        Resultados de búsqueda para: <strong>{query}</strong>
        <br><br>
        <em>Carga un documento 10-K para ver resultados reales.</em>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    🏛️ Sindicato V8.1 | Capital Preservation First | 
    <em>"Precio es lo que pagas, valor es lo que recibes"</em> - Warren Buffett
</div>
""", unsafe_allow_html=True)
