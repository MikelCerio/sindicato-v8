"""
🎨 DASHBOARD COMPONENTS - Opción A (Dashboard Unificado)
Componentes modulares para el nuevo dashboard estilo Bloomberg Terminal
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional, Dict, Any


def render_ticker_header(ticker: str, company_name: str, price: float, change_pct: float, market_cap: float):
    """
    Render ticker header con información en tiempo real
    
    Args:
        ticker: Símbolo del ticker
        company_name: Nombre de la empresa
        price: Precio actual
        change_pct: Cambio porcentual
        market_cap: Capitalización de mercado
    """
    
    # Determinar color según cambio
    color = "🟢" if change_pct >= 0 else "🔴"
    change_symbol = "▲" if change_pct >= 0 else "▼"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
                padding: 1.5rem; 
                border-radius: 12px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='color: white; margin: 0; font-size: 2rem;'>
                    {ticker}
                </h1>
                <p style='color: #93c5fd; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                    {company_name}
                </p>
            </div>
            <div style='text-align: right;'>
                <h2 style='color: white; margin: 0; font-size: 2.5rem;'>
                    ${price:.2f}
                </h2>
                <p style='color: {"#10b981" if change_pct >= 0 else "#ef4444"}; 
                          margin: 0.5rem 0 0 0; 
                          font-size: 1.2rem;
                          font-weight: bold;'>
                    {color} {change_symbol} {abs(change_pct):.2f}%
                </p>
            </div>
        </div>
        <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);'>
            <span style='color: #93c5fd; font-size: 0.9rem;'>
                Market Cap: <strong style='color: white;'>${market_cap/1e9:.2f}B</strong>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_key_metrics_compact(metrics: Dict[str, Any]):
    """
    Render métricas clave en formato compacto (4 columnas)
    
    Args:
        metrics: Diccionario con métricas
    """
    
    st.subheader("💹 Key Metrics")
    
    cols = st.columns(4)
    
    metrics_list = [
        ("P/E Ratio", metrics.get('pe_ratio', 'N/A'), "📊"),
        ("Forward P/E", metrics.get('forward_pe', 'N/A'), "📈"),
        ("ROE", f"{metrics.get('roe', 0)*100:.1f}%" if metrics.get('roe') else 'N/A', "💰"),
        ("Debt/Equity", f"{metrics.get('debt_to_equity', 0):.2f}" if metrics.get('debt_to_equity') else 'N/A', "⚖️"),
        ("EPS", f"${metrics.get('eps', 0):.2f}" if metrics.get('eps') else 'N/A', "💵"),
        ("Revenue Growth", f"{metrics.get('revenue_growth', 0)*100:.1f}%" if metrics.get('revenue_growth') else 'N/A', "📊"),
        ("Profit Margin", f"{metrics.get('profit_margin', 0)*100:.1f}%" if metrics.get('profit_margin') else 'N/A', "💹"),
        ("Beta", f"{metrics.get('beta', 0):.2f}" if metrics.get('beta') else 'N/A', "📉"),
    ]
    
    for i, (label, value, icon) in enumerate(metrics_list):
        with cols[i % 4]:
            st.metric(
                label=f"{icon} {label}",
                value=value
            )


def render_sentiment_news_card(sentiment_data: Any):
    """
    Render card de sentiment + news
    
    Args:
        sentiment_data: Objeto con datos de sentiment
    """
    
    st.subheader("📰 News & Sentiment")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Sentiment gauge
        sentiment_score = getattr(sentiment_data, 'overall_score', 0.5)
        sentiment_emoji = getattr(sentiment_data, 'overall_emoji', '😐')
        sentiment_text = getattr(sentiment_data, 'overall_sentiment', 'Neutral')
        
        st.markdown(f"""
        <div style='text-align: center; 
                    padding: 2rem; 
                    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                    border-radius: 12px;'>
            <div style='font-size: 4rem; margin-bottom: 0.5rem;'>
                {sentiment_emoji}
            </div>
            <div style='font-size: 1.5rem; font-weight: bold; color: #1f2937;'>
                {sentiment_text}
            </div>
            <div style='font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;'>
                Score: {sentiment_score:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Timeline chart
        if hasattr(sentiment_data, 'timeline_chart') and sentiment_data.timeline_chart:
            st.plotly_chart(sentiment_data.timeline_chart, use_container_width=True, key="sentiment_timeline")
        
        # Latest news
        if hasattr(sentiment_data, 'news_items'):
            st.caption("**Latest News:**")
            for news in sentiment_data.news_items[:3]:
                st.markdown(
                    f"<div class='{news.css_class}'>{news.emoji} {news.title[:80]}...</div>",
                    unsafe_allow_html=True
                )


def render_financial_statements_collapsible(ticker: str, openbb_service):
    """
    Render estados financieros en expander colapsable
    
    Args:
        ticker: Símbolo del ticker
        openbb_service: Servicio de OpenBB
    """
    
    with st.expander("📊 Financial Statements", expanded=False):
        fin_tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        
        with fin_tabs[0]:
            st.caption("Income Statement (Annual)")
            try:
                income = openbb_service.get_income_statement(ticker, period="annual", limit=3)
                if income is not None and not income.empty:
                    st.dataframe(income, use_container_width=True)
                else:
                    st.info("No data available")
            except Exception as e:
                st.warning(f"Could not load income statement: {str(e)}")
        
        with fin_tabs[1]:
            st.caption("Balance Sheet (Annual)")
            try:
                balance = openbb_service.get_balance_sheet(ticker, period="annual", limit=3)
                if balance is not None and not balance.empty:
                    st.dataframe(balance, use_container_width=True)
                else:
                    st.info("No data available")
            except Exception as e:
                st.warning(f"Could not load balance sheet: {str(e)}")
        
        with fin_tabs[2]:
            st.caption("Cash Flow (Annual)")
            try:
                cashflow = openbb_service.get_cash_flow(ticker, period="annual", limit=3)
                if cashflow is not None and not cashflow.empty:
                    st.dataframe(cashflow, use_container_width=True)
                else:
                    st.info("No data available")
            except Exception as e:
                st.warning(f"Could not load cash flow: {str(e)}")


def render_price_chart(ticker: str, chart_service):
    """
    Render gráfico de precio interactivo
    
    Args:
        ticker: Símbolo del ticker
        chart_service: Servicio de gráficos
    """
    
    st.subheader("📈 Price Chart")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        period = st.selectbox(
            "Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            key="chart_period"
        )
    
    with col2:
        chart_type = st.selectbox(
            "Type",
            ["Candlestick", "Line", "Area"],
            key="chart_type"
        )
    
    with col3:
        show_volume = st.checkbox("Volume", value=True, key="show_volume")
    
    # Generar gráfico
    chart = chart_service.create_price_chart(
        ticker,
        period=period,
        chart_type=chart_type.lower(),
        show_volume=show_volume
    )
    
    if chart:
        st.plotly_chart(chart, use_container_width=True, key="main_price_chart")
    else:
        st.error("Could not load chart")


def render_quick_actions(ticker: str):
    """
    Render botones de acciones rápidas
    
    Args:
        ticker: Símbolo del ticker
    """
    
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("🦈 Run AI Analysis", use_container_width=True, type="primary"):
            st.session_state['switch_to_ai'] = True
            st.rerun()
    
    with cols[1]:
        if st.button("📄 View Filings", use_container_width=True):
            st.session_state['switch_to_filings'] = True
            st.rerun()
    
    with cols[2]:
        if st.button("⚖️ Add to Portfolio", use_container_width=True):
            st.session_state['switch_to_portfolio'] = True
            st.session_state['portfolio_ticker'] = ticker
            st.rerun()
    
    with cols[3]:
        if st.button("📊 Export Report", use_container_width=True):
            st.info("Export functionality coming soon")
