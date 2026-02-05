"""
📈 PRICE CHARTS V8
Gráficos de precio histórico con Plotly
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

from services.market_data import MarketDataService


class PriceChartService:
    """Genera gráficos de precio interactivos."""
    
    def __init__(self):
        self.market_service = MarketDataService()
    
    def create_candlestick_chart(self, ticker: str, period: str = "1y") -> Optional[go.Figure]:
        """Crea gráfico de velas con volumen."""
        hist = self.market_service.get_price_history(ticker, period)
        
        if hist is None or hist.empty:
            return None
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=[f'{ticker} - Precio', 'Volumen']
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
        
        # Medias móviles
        if len(hist) > 20:
            hist['MA20'] = hist['Close'].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['MA20'],
                name='MA20', line=dict(color='#ffaa00', width=1)
            ), row=1, col=1)
        
        if len(hist) > 50:
            hist['MA50'] = hist['Close'].rolling(50).mean()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['MA50'],
                name='MA50', line=dict(color='#00aaff', width=1)
            ), row=1, col=1)
        
        # Volumen
        colors = ['#00ff88' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ff4444' 
                  for i in range(len(hist))]
        
        fig.add_trace(go.Bar(
            x=hist.index, y=hist['Volume'],
            name='Volumen', marker_color=colors, opacity=0.7
        ), row=2, col=1)
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,10,10,0.8)',
            height=600,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        return fig
    
    def create_performance_chart(self, ticker: str, period: str = "1y") -> Optional[go.Figure]:
        """Crea gráfico de rendimiento normalizado."""
        hist = self.market_service.get_price_history(ticker, period)
        
        if hist is None or hist.empty:
            return None
        
        # Normalizar a 100
        normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
        
        # Calcular cambio %
        pct_change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
        
        fig = go.Figure()
        
        color = '#00ff88' if pct_change >= 0 else '#ff4444'
        
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=normalized,
            mode='lines',
            fill='tozeroy',
            fillcolor=f'rgba({",".join(str(int(color[i:i+2], 16)) for i in (1,3,5))},0.1)',
            line=dict(color=color, width=2),
            name=ticker
        ))
        
        # Línea base 100
        fig.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.3)
        
        fig.update_layout(
            title=f'{ticker} - Rendimiento ({pct_change:+.1f}%)',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            yaxis_title='Rendimiento (Base 100)'
        )
        
        return fig
    
    def create_multi_comparison(self, tickers: list, period: str = "1y") -> Optional[go.Figure]:
        """Compara rendimiento de múltiples tickers."""
        fig = go.Figure()
        
        colors = ['#00ff88', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a855f7', '#00aaff']
        
        for i, ticker in enumerate(tickers):
            hist = self.market_service.get_price_history(ticker, period)
            if hist is not None and not hist.empty:
                normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=normalized,
                    mode='lines',
                    name=ticker,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        fig.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.3)
        
        fig.update_layout(
            title='Comparativa de Rendimiento',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            yaxis_title='Rendimiento (Base 100)',
            legend=dict(orientation="h")
        )
        
        return fig


def render_charts_section(ticker: str):
    """Renderiza sección de gráficos en Streamlit."""
    chart_service = PriceChartService()
    
    # Selector de período
    period = st.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Candlestick
        candle_chart = chart_service.create_candlestick_chart(ticker, period)
        if candle_chart:
            st.plotly_chart(candle_chart, use_container_width=True)
        else:
            st.error("No se pudo cargar el gráfico")
    
    with col2:
        # Rendimiento
        perf_chart = chart_service.create_performance_chart(ticker, period)
        if perf_chart:
            st.plotly_chart(perf_chart, use_container_width=True)
