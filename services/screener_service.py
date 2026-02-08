"""
🕵️ SCREENER SERVICE
Motor de descubrimiento de oportunidades comparables
"""

import logging
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional
import yfinance as yf

logger = logging.getLogger(__name__)


class ScreenerService:
    """Servicio para encontrar y comparar empresas similares."""
    
    def __init__(self):
        self._cache = {}
    
    def get_similar_companies(self, ticker: str) -> List[str]:
        """
        Busca empresas del MISMO SECTOR e INDUSTRIA.
        
        Args:
            ticker: Símbolo de la empresa base
        
        Returns:
            Lista de tickers del mismo sector
        """
        try:
            logger.info(f"Buscando competidores de {ticker}")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            logger.info(f"{ticker} - Sector: {sector}, Industry: {industry}")
            
            # Mapa expandido de competidores por sector/industria
            # Clave: (sector, industry parcial) -> lista de competidores
            industry_map = {
                # Autos / EV
                ('Consumer Cyclical', 'Auto'): ['TSLA', 'F', 'GM', 'TM', 'RIVN', 'LCID', 'HMC', 'STLA'],
                ('Consumer Cyclical', 'Electric'): ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI'],
                
                # Tech - Software
                ('Technology', 'Software'): ['MSFT', 'ORCL', 'CRM', 'ADBE', 'NOW', 'INTU', 'SAP'],
                ('Technology', 'Hardware'): ['AAPL', 'HPE', 'DELL', 'LOGI'],
                ('Technology', 'Semiconduct'): ['NVDA', 'AMD', 'INTC', 'AVGO', 'QCOM', 'TSM', 'ASML'],
                ('Technology', 'Internet'): ['GOOGL', 'META', 'SNAP', 'PINS', 'TWTR'],
                ('Technology', ''): ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC'],
                
                # Finance
                ('Financial Services', 'Bank'): ['JPM', 'BAC', 'WFC', 'C', 'USB', 'PNC'],
                ('Financial Services', 'Capital'): ['GS', 'MS', 'BLK', 'SCHW', 'HOOD'],
                ('Financial Services', 'Insurance'): ['BRK-B', 'MET', 'AIG', 'PRU', 'ALL'],
                ('Financial Services', ''): ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK'],
                
                # Healthcare
                ('Healthcare', 'Pharma'): ['JNJ', 'PFE', 'MRK', 'ABBV', 'LLY', 'NVO'],
                ('Healthcare', 'Biotech'): ['AMGN', 'GILD', 'BIIB', 'MRNA', 'VRTX'],
                ('Healthcare', 'Device'): ['MDT', 'ABT', 'SYK', 'ISRG', 'BSX'],
                ('Healthcare', ''): ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO'],
                
                # Consumer
                ('Consumer Cyclical', 'Retail'): ['AMZN', 'WMT', 'TGT', 'COST', 'HD', 'LOW'],
                ('Consumer Cyclical', 'Restaurant'): ['MCD', 'SBUX', 'CMG', 'YUM', 'DRI'],
                ('Consumer Cyclical', 'Apparel'): ['NKE', 'LULU', 'UA', 'VFC', 'RL'],
                ('Consumer Cyclical', ''): ['AMZN', 'HD', 'NKE', 'SBUX', 'MCD'],
                
                ('Consumer Defensive', ''): ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL'],
                
                # Energy
                ('Energy', ''): ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'OXY', 'BP'],
                
                # Communication
                ('Communication Services', ''): ['GOOGL', 'META', 'DIS', 'NFLX', 'CMCSA', 'T', 'VZ'],
                
                # Industrial
                ('Industrials', ''): ['CAT', 'DE', 'BA', 'HON', 'UPS', 'GE', 'RTX'],
                
                # Real Estate
                ('Real Estate', ''): ['AMT', 'PLD', 'EQIX', 'SPG', 'O'],
            }
            
            # Buscar coincidencia exacta primero (sector + industria parcial)
            candidates = []
            for (map_sector, map_industry), tickers_list in industry_map.items():
                if sector == map_sector:
                    if map_industry == '' or (industry and map_industry.lower() in industry.lower()):
                        candidates = tickers_list
                        break
            
            # Fallback: Solo por sector
            if not candidates:
                for (map_sector, map_industry), tickers_list in industry_map.items():
                    if sector == map_sector and map_industry == '':
                        candidates = tickers_list
                        break
            
            # Filtrar el ticker original y limitar
            candidates = [t for t in candidates if t.upper() != ticker.upper()]
            
            logger.info(f"Competidores encontrados para {ticker}: {candidates[:8]}")
            return candidates[:8]
            
        except Exception as e:
            logger.error(f"Error buscando competidores: {e}")
            return []
    
    def get_stock_metrics(self, ticker: str) -> Optional[Dict]:
        """
        Obtiene métricas clave de una acción.
        
        Args:
            ticker: Símbolo de la acción
        
        Returns:
            Dict con métricas o None si falla
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extraer métricas clave
            metrics = {
                'ticker': ticker,
                'name': info.get('shortName', ticker),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'roe': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'current_price': info.get('currentPrice', 0),
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de {ticker}: {e}")
            return None
    
    def score_stock(self, metrics: Dict, mode: str = "standard") -> tuple[int, str]:
        """
        Puntúa una acción según criterios.
        
        Args:
            metrics: Dict con métricas de la acción
            mode: 'standard' o 'small_cap'
        
        Returns:
            (score, tag) - Puntuación y etiqueta
        """
        score = 0
        reasons = []
        
        pe = metrics.get('pe_ratio', 0) or 0
        debt_eq = metrics.get('debt_to_equity', 0) or 0
        roe = metrics.get('roe', 0) or 0
        pb = metrics.get('price_to_book', 0) or 0
        margin = metrics.get('profit_margin', 0) or 0
        
        if mode == "small_cap":
            # Criterios Alpha
            # 1. Deuda baja
            if debt_eq < 50:  # Menos de 0.5x
                score += 2
                reasons.append("Deuda baja")
            elif debt_eq > 150:  # Más de 1.5x
                score -= 2
                reasons.append("Deuda alta")
            
            # 2. ROE alto (calidad)
            if roe > 0.15:
                score += 3
                reasons.append("ROE >15%")
            elif roe < 0.05:
                score -= 1
            
            # 3. Valoración razonable
            if 0 < pe < 25:
                score += 1
                reasons.append("P/E razonable")
            
            # 4. Márgenes
            if margin > 0.10:
                score += 1
                reasons.append("Margen >10%")
            
            # Tag
            if score >= 4:
                tag = "💎 Posible Gema"
            elif score >= 2:
                tag = "⚠️ Revisar"
            else:
                tag = "❌ Evitar"
                
        else:
            # Criterios Standard (institucional)
            # 1. ROE decente
            if roe > 0.10:
                score += 1
                reasons.append("ROE >10%")
            
            # 2. Valoración
            if 0 < pe < 30:
                score += 1
                reasons.append("P/E <30")
            
            # 3. Deuda manejable
            if debt_eq < 100:
                score += 1
                reasons.append("Deuda baja")
            
            # 4. Márgenes
            if margin > 0.08:
                score += 1
            
            # Tag
            if score >= 3:
                tag = "🏢 Sólida"
            elif score >= 2:
                tag = "📊 Neutral"
            else:
                tag = "📉 Débil"
        
        return score, tag
    
    def run_screen(self, ticker: str, mode: str = "standard") -> pd.DataFrame:
        """
        Ejecuta el screener completo.
        
        Args:
            ticker: Ticker base para buscar similares
            mode: 'standard' o 'small_cap'
        
        Returns:
            DataFrame con resultados ordenados por score
        """
        logger.info(f"Ejecutando screener para {ticker} en modo {mode}")
        
        # 1. Obtener candidatos
        candidates = self.get_similar_companies(ticker)
        
        # Añadir el ticker original para comparar
        all_tickers = [ticker] + candidates
        
        if not all_tickers:
            logger.warning("No se encontraron candidatos")
            return pd.DataFrame()
        
        # 2. Analizar cada candidato
        results = []
        progress_text = "Analizando competidores..."
        my_bar = st.progress(0, text=progress_text)
        
        total = len(all_tickers)
        
        for i, symbol in enumerate(all_tickers):
            try:
                my_bar.progress((i + 1) / total, text=f"Escaneando {symbol}...")
                
                # Obtener métricas
                metrics = self.get_stock_metrics(symbol)
                
                if metrics:
                    # Calcular score
                    score, tag = self.score_stock(metrics, mode)
                    
                    # Formatear para tabla
                    results.append({
                        "Ticker": symbol,
                        "Nombre": metrics.get('name', symbol)[:30],
                        "Score": score,
                        "Tag": tag,
                        "P/E": round(metrics.get('pe_ratio', 0), 1) if metrics.get('pe_ratio') else '-',
                        "ROE": f"{metrics.get('roe', 0)*100:.1f}%" if metrics.get('roe') else '-',
                        "Deuda/Eq": round(metrics.get('debt_to_equity', 0)/100, 2) if metrics.get('debt_to_equity') else '-',
                        "Margen": f"{metrics.get('profit_margin', 0)*100:.1f}%" if metrics.get('profit_margin') else '-',
                    })
                    
            except Exception as e:
                logger.error(f"Error analizando {symbol}: {e}")
                continue
        
        my_bar.empty()
        
        # 3. Convertir a DataFrame y ordenar
        if results:
            df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
            logger.info(f"Screener completado: {len(df)} empresas analizadas")
            return df
        
        return pd.DataFrame()
