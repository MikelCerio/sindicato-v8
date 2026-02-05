"""
⚖️ PORTFOLIO OPTIMIZER - Optimización Científica
Implementa Modern Portfolio Theory (Markowitz) para asignación óptima.
Usa PyPortfolioOpt para calcular la Frontera Eficiente.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Resultado de la optimización de portfolio."""
    
    # Allocation
    weights: Dict[str, float]  # Ticker -> Weight (0-1)
    allocation: Dict[str, float]  # Ticker -> Capital en €
    
    # Performance esperado
    expected_return: float  # Anualizado
    volatility: float  # Anualizado
    sharpe_ratio: float
    
    # Extras
    correlation_matrix: Optional[pd.DataFrame] = None
    covariance_matrix: Optional[pd.DataFrame] = None
    
    # Comparativa con equal weight
    equal_weight_return: float = 0.0
    equal_weight_volatility: float = 0.0
    improvement_pct: float = 0.0


class PortfolioOptimizer:
    """
    Optimizador de portafolios usando teoría de Markowitz.
    
    Estrategias disponibles:
    - max_sharpe: Maximiza ratio Sharpe (retorno/riesgo)
    - min_volatility: Minimiza volatilidad
    - efficient_return: Target de retorno específico
    - max_quadratic_utility: Considera aversión al riesgo
    """
    
    def __init__(self, risk_free_rate: float = 0.04):
        """
        Args:
            risk_free_rate: Tasa libre de riesgo (default 4% - bonos actuales)
        """
        self.risk_free_rate = risk_free_rate
        self._pypfopt_available = None
    
    def _check_pypfopt(self) -> bool:
        """Verifica si pypfopt está instalado."""
        if self._pypfopt_available is not None:
            return self._pypfopt_available
        
        try:
            from pypfopt import EfficientFrontier, risk_models, expected_returns
            self._pypfopt_available = True
        except ImportError:
            logger.warning("PyPortfolioOpt no instalado. Usando cálculo básico.")
            self._pypfopt_available = False
        
        return self._pypfopt_available
    
    @st.cache_data(ttl=1800, show_spinner=False)
    def optimize(
        _self,
        tickers: List[str],
        total_capital: float = 10000,
        strategy: str = "max_sharpe",
        period: str = "2y",
        constraints: Optional[Dict] = None
    ) -> Tuple[Optional[OptimizationResult], str]:
        """
        Optimiza el portfolio.
        
        Args:
            tickers: Lista de tickers a incluir
            total_capital: Capital total a invertir (€)
            strategy: 'max_sharpe', 'min_volatility', 'efficient_return'
            period: Período histórico ('1y', '2y', '5y')
            constraints: Dict con min/max por ticker opcional
            
        Returns:
            Tuple (OptimizationResult, message)
        """
        if len(tickers) < 2:
            return None, "❌ Se necesitan al menos 2 activos para optimizar."
        
        # Descargar datos
        try:
            import yfinance as yf
            data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
            
            # Manejar diferentes formatos de yfinance
            if isinstance(data.columns, pd.MultiIndex):
                # Multi-ticker download
                if 'Adj Close' in data.columns.get_level_values(0):
                    prices = data['Adj Close']
                elif 'Close' in data.columns.get_level_values(0):
                    prices = data['Close']
                else:
                    # Intentar con el primer nivel
                    prices = data.iloc[:, data.columns.get_level_values(0) == data.columns.get_level_values(0)[0]]
                    prices.columns = prices.columns.droplevel(0)
            else:
                # Single ticker o formato simple
                if 'Adj Close' in data.columns:
                    prices = data[['Adj Close']]
                    prices.columns = tickers if len(tickers) == 1 else prices.columns
                elif 'Close' in data.columns:
                    prices = data[['Close']]
                    prices.columns = tickers if len(tickers) == 1 else prices.columns
                else:
                    prices = data
            
            if prices.empty or len(prices) < 50:
                return None, "❌ Datos históricos insuficientes."
            
            # Limpiar NaN
            prices = prices.dropna()
            
            if len(prices) < 50:
                return None, "❌ Datos insuficientes después de limpiar valores faltantes."
            
        except Exception as e:
            logger.error(f"Error descargando datos para optimización: {e}")
            return None, f"❌ Error descargando datos: {str(e)}"
        
        # Si pypfopt está disponible, usar optimización avanzada
        if _self._check_pypfopt():
            return _self._optimize_pypfopt(
                prices, tickers, total_capital, strategy, constraints
            )
        else:
            return _self._optimize_basic(prices, tickers, total_capital)
    
    def _optimize_pypfopt(
        self,
        prices: pd.DataFrame,
        tickers: List[str],
        total_capital: float,
        strategy: str,
        constraints: Optional[Dict]
    ) -> Tuple[Optional[OptimizationResult], str]:
        """Optimización usando PyPortfolioOpt."""
        try:
            from pypfopt import EfficientFrontier, risk_models, expected_returns
            from pypfopt import objective_functions
            
            # Calcular retornos esperados y matriz de covarianza
            mu = expected_returns.mean_historical_return(prices)
            S = risk_models.sample_cov(prices)
            
            # Crear optimizador
            ef = EfficientFrontier(mu, S)
            
            # Aplicar constraints si existen
            if constraints:
                for ticker, bounds in constraints.items():
                    if ticker in tickers:
                        idx = tickers.index(ticker)
                        ef.add_constraint(
                            lambda w, i=idx, b=bounds: w[i] >= b.get('min', 0)
                        )
                        ef.add_constraint(
                            lambda w, i=idx, b=bounds: w[i] <= b.get('max', 1)
                        )
            
            # Seleccionar estrategia
            if strategy == "max_sharpe":
                weights = ef.max_sharpe(risk_free_rate=self.risk_free_rate)
            elif strategy == "min_volatility":
                weights = ef.min_volatility()
            elif strategy == "efficient_return":
                # Target: media de retornos + 1 std
                target = mu.mean() + mu.std()
                weights = ef.efficient_return(target_return=target)
            else:
                weights = ef.max_sharpe(risk_free_rate=self.risk_free_rate)
            
            # Limpiar pesos
            cleaned_weights = ef.clean_weights()
            
            # Performance
            perf = ef.portfolio_performance(
                verbose=False,
                risk_free_rate=self.risk_free_rate
            )
            expected_return, volatility, sharpe = perf
            
            # Calcular equal weight para comparar
            n = len(tickers)
            returns = prices.pct_change().dropna()
            equal_ret = returns.mean() @ np.ones(n) / n * 252
            equal_cov = returns.cov() * 252
            equal_vol = np.sqrt(np.ones(n) @ equal_cov.values @ np.ones(n)) / n
            
            # Allocation en €
            allocation = {
                t: round(w * total_capital, 2) 
                for t, w in cleaned_weights.items() 
                if w > 0.01  # Ignorar < 1%
            }
            
            # Improvement
            if equal_vol > 0:
                improvement = ((sharpe - (equal_ret - self.risk_free_rate) / equal_vol) 
                              / abs((equal_ret - self.risk_free_rate) / equal_vol)) * 100
            else:
                improvement = 0
            
            result = OptimizationResult(
                weights=cleaned_weights,
                allocation=allocation,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe,
                correlation_matrix=returns.corr(),
                covariance_matrix=S,
                equal_weight_return=equal_ret,
                equal_weight_volatility=equal_vol,
                improvement_pct=improvement
            )
            
            return result, "✅ Optimización completada con éxito."
            
        except Exception as e:
            logger.error(f"Error en optimización: {e}")
            return None, f"❌ Error en optimización: {str(e)}"
    
    def _optimize_basic(
        self,
        prices: pd.DataFrame,
        tickers: List[str],
        total_capital: float
    ) -> Tuple[Optional[OptimizationResult], str]:
        """Optimización básica sin pypfopt (inverse volatility)."""
        try:
            returns = prices.pct_change().dropna()
            
            # Volatilidad de cada activo
            vols = returns.std() * np.sqrt(252)
            
            # Pesos inversamente proporcionales a volatilidad
            inv_vol = 1 / vols
            weights = inv_vol / inv_vol.sum()
            
            # Performance
            mean_returns = returns.mean() * 252
            expected_return = (weights * mean_returns).sum()
            
            portfolio_returns = (returns * weights).sum(axis=1)
            volatility = portfolio_returns.std() * np.sqrt(252)
            
            sharpe = (expected_return - self.risk_free_rate) / volatility
            
            # Allocation
            allocation = {
                t: round(w * total_capital, 2)
                for t, w in weights.items()
                if w > 0.01
            }
            
            result = OptimizationResult(
                weights=weights.to_dict(),
                allocation=allocation,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe,
                correlation_matrix=returns.corr()
            )
            
            return result, "✅ Optimización básica (inverse volatility) completada."
            
        except Exception as e:
            return None, f"❌ Error: {str(e)}"
    
    def get_efficient_frontier_points(
        self,
        tickers: List[str],
        n_points: int = 20,
        period: str = "2y"
    ) -> Optional[pd.DataFrame]:
        """
        Genera puntos de la frontera eficiente para visualización.
        
        Returns:
            DataFrame con columnas ['Return', 'Volatility', 'Sharpe']
        """
        if not self._check_pypfopt():
            return None
        
        try:
            import yfinance as yf
            from pypfopt import EfficientFrontier, risk_models, expected_returns
            
            data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
            # Manejar diferentes formatos de yfinance
            if isinstance(data.columns, pd.MultiIndex):
                if 'Adj Close' in data.columns.get_level_values(0):
                    prices = data['Adj Close']
                elif 'Close' in data.columns.get_level_values(0):
                    prices = data['Close']
                else:
                    prices = data
            elif 'Adj Close' in data.columns:
                prices = data['Adj Close']
            elif 'Close' in data.columns:
                prices = data['Close']
            else:
                prices = data
            
            mu = expected_returns.mean_historical_return(prices)
            S = risk_models.sample_cov(prices)
            
            # Generar puntos
            points = []
            
            # Rango de retornos target
            min_ret = mu.min()
            max_ret = mu.max()
            target_returns = np.linspace(min_ret, max_ret, n_points)
            
            for target in target_returns:
                try:
                    ef = EfficientFrontier(mu, S)
                    ef.efficient_return(target_return=target)
                    perf = ef.portfolio_performance(
                        verbose=False,
                        risk_free_rate=self.risk_free_rate
                    )
                    points.append({
                        'Return': perf[0],
                        'Volatility': perf[1],
                        'Sharpe': perf[2]
                    })
                except:
                    continue
            
            if not points:
                return None
            
            return pd.DataFrame(points)
            
        except Exception as e:
            logger.error(f"Error generando frontera eficiente: {e}")
            return None
    
    def get_risk_contribution(
        self,
        weights: Dict[str, float],
        tickers: List[str],
        period: str = "2y"
    ) -> Optional[pd.DataFrame]:
        """
        Calcula la contribución al riesgo de cada activo.
        
        Returns:
            DataFrame con risk contribution por ticker
        """
        try:
            import yfinance as yf
            
            data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
            # Manejar diferentes formatos de yfinance
            if isinstance(data.columns, pd.MultiIndex):
                if 'Adj Close' in data.columns.get_level_values(0):
                    prices = data['Adj Close']
                elif 'Close' in data.columns.get_level_values(0):
                    prices = data['Close']
                else:
                    prices = data
            elif 'Adj Close' in data.columns:
                prices = data['Adj Close']
            elif 'Close' in data.columns:
                prices = data['Close']
            else:
                prices = data
            returns = prices.pct_change().dropna()
            
            # Covarianza anualizada
            cov_matrix = returns.cov() * 252
            
            # Pesos como array
            w = np.array([weights.get(t, 0) for t in tickers])
            
            # Volatilidad del portfolio
            port_vol = np.sqrt(w.T @ cov_matrix.values @ w)
            
            # Contribución marginal al riesgo
            marginal_contrib = cov_matrix.values @ w
            
            # Contribución al riesgo de cada activo
            risk_contrib = w * marginal_contrib / port_vol
            
            # Porcentaje de contribución
            risk_contrib_pct = risk_contrib / risk_contrib.sum() * 100
            
            df = pd.DataFrame({
                'Ticker': tickers,
                'Weight': w,
                'Risk Contribution': risk_contrib,
                'Risk %': risk_contrib_pct
            })
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculando risk contribution: {e}")
            return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_portfolio_pie_chart(allocation: Dict[str, float]):
    """Crea gráfico de tarta para allocation."""
    import plotly.express as px
    
    df = pd.DataFrame([
        {'Ticker': k, 'Capital (€)': v} 
        for k, v in allocation.items()
    ])
    
    fig = px.pie(
        df,
        values='Capital (€)',
        names='Ticker',
        hole=0.4,
        title='Asignación de Capital Óptima'
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_efficient_frontier_chart(frontier_df: pd.DataFrame, current_point: Tuple[float, float] = None):
    """Crea gráfico de frontera eficiente."""
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Frontera
    fig.add_trace(go.Scatter(
        x=frontier_df['Volatility'] * 100,
        y=frontier_df['Return'] * 100,
        mode='lines',
        name='Frontera Eficiente',
        line=dict(color='#00ff88', width=3)
    ))
    
    # Punto actual si existe
    if current_point:
        fig.add_trace(go.Scatter(
            x=[current_point[1] * 100],
            y=[current_point[0] * 100],
            mode='markers',
            name='Portfolio Óptimo',
            marker=dict(size=15, color='#ff4444', symbol='star')
        ))
    
    fig.update_layout(
        title='Frontera Eficiente de Markowitz',
        xaxis_title='Volatilidad Anual (%)',
        yaxis_title='Retorno Esperado (%)',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig
