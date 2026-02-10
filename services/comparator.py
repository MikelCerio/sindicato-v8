"""
📊 COMPARATIVA DE TICKERS V8
Compara múltiples acciones lado a lado
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
from dataclasses import dataclass

from services.market_data import MarketDataService, StockFundamentals


@dataclass
class ComparisonResult:
    tickers: List[str]
    fundamentals: Dict[str, StockFundamentals]
    comparison_table: pd.DataFrame
    charts: Dict[str, go.Figure]
    winner: str
    scores: Dict[str, float]


class TickerComparator:
    """Compara múltiples tickers y genera análisis comparativo."""
    
    METRICS_WEIGHTS = {
        'pe_ratio': -0.15,      # Menor es mejor
        'forward_pe': -0.10,
        'roe': 0.20,            # Mayor es mejor
        'profit_margin': 0.15,
        'debt_to_equity': -0.15,
        'current_ratio': 0.10,
        'revenue_growth': 0.15
    }
    
    def __init__(self):
        self.market_service = MarketDataService()
    
    def compare(self, tickers: List[str]) -> Optional[ComparisonResult]:
        """Compara lista de tickers."""
        if len(tickers) < 2:
            return None
        
        # Obtener fundamentales
        fundamentals = {}
        for ticker in tickers:
            data = self.market_service.get_fundamentals(ticker)
            if data:
                fundamentals[ticker] = data
        
        if len(fundamentals) < 2:
            return None
        
        # Crear tabla comparativa
        table = self._create_comparison_table(fundamentals)
        
        # Calcular scores
        scores = self._calculate_scores(fundamentals)
        winner = max(scores, key=scores.get)
        
        # Crear gráficos
        charts = {
            'radar': self._create_radar_chart(fundamentals),
            'bars': self._create_bar_comparison(fundamentals),
            'valuation': self._create_valuation_chart(fundamentals)
        }
        
        return ComparisonResult(
            tickers=list(fundamentals.keys()),
            fundamentals=fundamentals,
            comparison_table=table,
            charts=charts,
            winner=winner,
            scores=scores
        )
    
    def _create_comparison_table(self, fundamentals: Dict[str, StockFundamentals]) -> pd.DataFrame:
        """Crea tabla de comparación."""
        data = []
        for ticker, f in fundamentals.items():
            data.append({
                'Ticker': ticker,
                'Precio': f"${f.price:.2f}",
                'Market Cap': f"${f.market_cap/1e9:.1f}B",
                'P/E': f"{f.pe_ratio:.1f}",
                'Forward P/E': f"{f.forward_pe:.1f}",
                'ROE': f"{f.roe*100:.1f}%",
                'Profit Margin': f"{f.profit_margin*100:.1f}%",
                'Debt/Equity': f"{f.debt_to_equity:.2f}",
                'Current Ratio': f"{f.current_ratio:.2f}",
                'Revenue Growth': f"{f.revenue_growth*100:.1f}%"
            })
        return pd.DataFrame(data)
    
    def _calculate_scores(self, fundamentals: Dict[str, StockFundamentals]) -> Dict[str, float]:
        """Calcula score compuesto para cada ticker."""
        scores = {}
        
        for ticker, f in fundamentals.items():
            score = 0
            metrics = {
                'pe_ratio': f.pe_ratio if f.pe_ratio > 0 else 50,
                'forward_pe': f.forward_pe if f.forward_pe > 0 else 50,
                'roe': f.roe,
                'profit_margin': f.profit_margin,
                'debt_to_equity': f.debt_to_equity,
                'current_ratio': f.current_ratio,
                'revenue_growth': f.revenue_growth
            }
            
            for metric, weight in self.METRICS_WEIGHTS.items():
                value = metrics.get(metric, 0)
                # Normalizar y aplicar peso
                normalized = min(max(value, -1), 2)  # Clip extremos
                score += normalized * weight * 100
            
            scores[ticker] = round(score, 2)
        
        return scores
    
    def _create_radar_chart(self, fundamentals: Dict[str, StockFundamentals]) -> go.Figure:
        """Crea gráfico radar comparativo."""
        categories = ['ROE', 'Margen', 'Crecimiento', 'Liquidez', 'Bajo P/E']
        
        fig = go.Figure()
        
        colors = ['#00ff88', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a855f7']
        
        for i, (ticker, f) in enumerate(fundamentals.items()):
            values = [
                min(f.roe * 100, 50),
                min(f.profit_margin * 100, 50),
                min(f.revenue_growth * 100 + 20, 50),
                min(f.current_ratio * 20, 50),
                max(50 - f.pe_ratio, 0)
            ]
            values.append(values[0])  # Cerrar el polígono
            
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
                radialaxis=dict(visible=True, range=[0, 50]),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            title='Comparativa Radar'
        )
        
        return fig
    
    def _create_bar_comparison(self, fundamentals: Dict[str, StockFundamentals]) -> go.Figure:
        """Crea gráfico de barras comparativo."""
        tickers = list(fundamentals.keys())
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=['ROE %', 'P/E Ratio', 'Profit Margin %', 'Debt/Equity'])
        
        colors = ['#00ff88', '#ff6b6b', '#4ecdc4', '#ffe66d'][:len(tickers)]
        
        # ROE
        fig.add_trace(go.Bar(x=tickers, y=[f.roe*100 for f in fundamentals.values()], marker_color=colors), row=1, col=1)
        
        # P/E
        fig.add_trace(go.Bar(x=tickers, y=[f.pe_ratio for f in fundamentals.values()], marker_color=colors), row=1, col=2)
        
        # Margin
        fig.add_trace(go.Bar(x=tickers, y=[f.profit_margin*100 for f in fundamentals.values()], marker_color=colors), row=2, col=1)
        
        # Debt
        fig.add_trace(go.Bar(x=tickers, y=[f.debt_to_equity for f in fundamentals.values()], marker_color=colors), row=2, col=2)
        
        fig.update_layout(
            showlegend=False,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        return fig
    
    def _create_valuation_chart(self, fundamentals: Dict[str, StockFundamentals]) -> go.Figure:
        """Scatter plot de valoración vs calidad."""
        fig = go.Figure()
        
        for ticker, f in fundamentals.items():
            fig.add_trace(go.Scatter(
                x=[f.pe_ratio],
                y=[f.roe * 100],
                mode='markers+text',
                marker=dict(size=f.market_cap/1e10 + 20, opacity=0.7),
                text=[ticker],
                textposition='top center',
                name=ticker
            ))
        
        fig.update_layout(
            title='Valoración vs Calidad',
            xaxis_title='P/E Ratio (menor = más barato)',
            yaxis_title='ROE % (mayor = mejor calidad)',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        return fig


def render_comparison_tab():
    """Renderiza la pestaña de comparación en Streamlit."""
    st.header("📊 Comparativa de Tickers")
    
    # Input de tickers
    tickers_input = st.text_input(
        "Ingresa tickers separados por coma",
        "AAPL, MSFT, GOOGL",
        help="Ejemplo: AAPL, MSFT, GOOGL, AMZN"
    )
    
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if len(tickers) >= 2 and st.button("🔍 Comparar", width="stretch"):
        with st.spinner("Obteniendo datos..."):
            comparator = TickerComparator()
            result = comparator.compare(tickers)
            
            if result:
                # Winner
                st.success(f"🏆 **Mejor opción según métricas:** {result.winner} (Score: {result.scores[result.winner]})")
                
                # Scores
                col1, col2, col3, col4 = st.columns(4)
                cols = [col1, col2, col3, col4]
                for i, (ticker, score) in enumerate(result.scores.items()):
                    if i < 4:
                        cols[i].metric(ticker, f"{score:.1f}")
                
                # Tabla
                st.subheader("📋 Tabla Comparativa")
                st.dataframe(result.comparison_table, width="stretch")
                
                # Gráficos
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(result.charts['radar'], width="stretch")
                with col2:
                    st.plotly_chart(result.charts['valuation'], width="stretch")
                
                st.plotly_chart(result.charts['bars'], width="stretch")
            else:
                st.error("No se pudieron obtener datos para los tickers")
    elif len(tickers) < 2:
        st.info("Ingresa al menos 2 tickers para comparar")
