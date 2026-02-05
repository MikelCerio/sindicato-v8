"""
📈 MARKET DATA SERVICE V8
Features:
- Caché inteligente con TTL
- Manejo robusto de errores
- Datos enriquecidos de fundamentales
- Contexto macro integrado
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

import streamlit as st
import yfinance as yf
import pandas as pd

from config import MACRO

logger = logging.getLogger(__name__)


@dataclass
class MacroContext:
    """Contexto macroeconómico actual"""
    vix: float
    treasury_10y: float
    regime: str
    regime_emoji: str
    brief: str
    timestamp: datetime
    
    @property
    def is_crisis(self) -> bool:
        return self.vix > MACRO.vix_crisis
    
    @property
    def is_elevated(self) -> bool:
        return self.vix > MACRO.vix_elevated
    
    @property
    def rates_restrictive(self) -> bool:
        return self.treasury_10y > MACRO.rates_restrictive


@dataclass
class StockFundamentals:
    """Datos fundamentales de una acción"""
    ticker: str
    name: str
    price: float
    market_cap: float
    pe_ratio: float
    forward_pe: float
    peg_ratio: float
    price_to_book: float
    roe: float
    roa: float
    debt_to_equity: float
    current_ratio: float
    quick_ratio: float
    revenue_growth: float
    earnings_growth: float
    profit_margin: float
    operating_margin: float
    free_cash_flow: float
    dividend_yield: float
    beta: float
    avg_volume: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    
    @property
    def distance_from_high(self) -> float:
        """Distancia porcentual desde el máximo 52w"""
        if self.fifty_two_week_high and self.price:
            return ((self.fifty_two_week_high - self.price) / self.fifty_two_week_high) * 100
        return 0
    
    @property
    def valuation_score(self) -> str:
        """Score simple de valoración"""
        if self.pe_ratio < 15 and self.peg_ratio < 1:
            return "🟢 Atractiva"
        elif self.pe_ratio > 30 or self.peg_ratio > 2:
            return "🔴 Cara"
        return "🟡 Neutral"
    
    @property
    def quality_score(self) -> str:
        """Score de calidad del negocio"""
        roe_ok = self.roe > 0.15
        margin_ok = self.profit_margin > 0.10
        debt_ok = self.debt_to_equity < 1.5
        
        score = sum([roe_ok, margin_ok, debt_ok])
        
        if score >= 3:
            return "🟢 Alta Calidad"
        elif score >= 2:
            return "🟡 Calidad Media"
        return "🔴 Baja Calidad"


class MarketDataService:
    """
    Servicio de datos de mercado con caché y error handling.
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)
    
    def _is_cache_valid(self, key: str) -> bool:
        """Verifica si el caché es válido"""
        if key not in self._cache_timestamps:
            return False
        return datetime.now() - self._cache_timestamps[key] < self._cache_ttl
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché si es válido"""
        if self._is_cache_valid(key):
            return self._cache.get(key)
        return None
    
    def _set_cached(self, key: str, value: Any) -> None:
        """Guarda valor en caché"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_fundamentals(_self, ticker: str) -> Optional[StockFundamentals]:
        """
        Obtiene datos fundamentales de una acción.
        
        Args:
            ticker: Símbolo de la acción
            
        Returns:
            StockFundamentals o None si hay error
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'currentPrice' not in info:
                logger.warning(f"No se encontraron datos para {ticker}")
                return None
            
            return StockFundamentals(
                ticker=ticker,
                name=info.get('longName', ticker),
                price=info.get('currentPrice', 0),
                market_cap=info.get('marketCap', 0),
                pe_ratio=info.get('trailingPE', 0) or 0,
                forward_pe=info.get('forwardPE', 0) or 0,
                peg_ratio=info.get('pegRatio', 0) or 0,
                price_to_book=info.get('priceToBook', 0) or 0,
                roe=info.get('returnOnEquity', 0) or 0,
                roa=info.get('returnOnAssets', 0) or 0,
                debt_to_equity=info.get('debtToEquity', 0) or 0,
                current_ratio=info.get('currentRatio', 0) or 0,
                quick_ratio=info.get('quickRatio', 0) or 0,
                revenue_growth=info.get('revenueGrowth', 0) or 0,
                earnings_growth=info.get('earningsGrowth', 0) or 0,
                profit_margin=info.get('profitMargins', 0) or 0,
                operating_margin=info.get('operatingMargins', 0) or 0,
                free_cash_flow=info.get('freeCashflow', 0) or 0,
                dividend_yield=info.get('dividendYield', 0) or 0,
                beta=info.get('beta', 1) or 1,
                avg_volume=info.get('averageVolume', 0) or 0,
                fifty_two_week_high=info.get('fiftyTwoWeekHigh', 0) or 0,
                fifty_two_week_low=info.get('fiftyTwoWeekLow', 0) or 0
            )
        except Exception as e:
            logger.error(f"Error obteniendo fundamentales de {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_price_history(_self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Obtiene histórico de precios.
        
        Args:
            ticker: Símbolo
            period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            
        Returns:
            DataFrame con OHLCV o None
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return None
            
            return hist
        except Exception as e:
            logger.error(f"Error obteniendo histórico de {ticker}: {e}")
            return None
    
    def get_news(self, ticker: str, limit: int = 10) -> List[Dict]:
        """
        Obtiene noticias recientes.
        
        Args:
            ticker: Símbolo
            limit: Número máximo de noticias
            
        Returns:
            Lista de diccionarios con noticias
        """
        cache_key = f"news_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached[:limit]
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news or []
            
            processed = []
            for n in news[:limit]:
                processed.append({
                    'title': n.get('title', ''),
                    'link': n.get('link', '#'),
                    'publisher': n.get('publisher', 'Unknown'),
                    'timestamp': datetime.fromtimestamp(
                        n.get('providerPublishTime', 0)
                    )
                })
            
            self._set_cached(cache_key, processed)
            return processed
        except Exception as e:
            logger.error(f"Error obteniendo noticias de {ticker}: {e}")
            return []


@st.cache_data(ttl=60, show_spinner=False)
def get_macro_context() -> MacroContext:
    """
    Obtiene contexto macroeconómico actual.
    
    Returns:
        MacroContext con VIX, tasas y régimen
    """
    try:
        # VIX
        vix_data = yf.Ticker("^VIX").history(period="1d")
        vix = vix_data['Close'].iloc[-1] if not vix_data.empty else 0
        
        # 10Y Treasury
        tnx_data = yf.Ticker("^TNX").history(period="1d")
        tnx = tnx_data['Close'].iloc[-1] if not tnx_data.empty else 0
        
        # Determinar régimen
        if vix > MACRO.vix_crisis:
            regime = "CRISIS"
            emoji = "🔴"
        elif vix > MACRO.vix_elevated:
            regime = "VOLATILIDAD ELEVADA"
            emoji = "🟡"
        elif vix < MACRO.vix_low:
            regime = "COMPLACENCIA"
            emoji = "🟠"
        else:
            regime = "ESTABLE"
            emoji = "🟢"
        
        brief = f"{emoji} {regime} | VIX: {vix:.1f} | 10Y: {tnx:.2f}%"
        
        return MacroContext(
            vix=vix,
            treasury_10y=tnx,
            regime=regime,
            regime_emoji=emoji,
            brief=brief,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error obteniendo macro: {e}")
        return MacroContext(
            vix=0,
            treasury_10y=0,
            regime="OFFLINE",
            regime_emoji="⚪",
            brief="⚪ MACRO DATA OFFLINE",
            timestamp=datetime.now()
        )
