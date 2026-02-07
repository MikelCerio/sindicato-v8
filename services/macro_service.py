"""
🌍 MACRO SERVICE - Pablo Gil Edition
Análisis macro para inversores institucionales

Datos clave:
- Curva de tipos (10Y-2Y): Predictor de recesión
- VIX: Nivel de miedo
- DXY: Fortaleza del dólar
- Oro: Refugio seguro
- Calendario económico
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import streamlit as st
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MacroDashboard:
    """Dashboard macro estilo Pablo Gil"""
    # Curva de Tipos
    treasury_10y: float
    treasury_2y: float
    yield_curve_spread: float  # 10Y - 2Y
    curve_status: str
    
    # Mercados
    vix: float
    dxy: float  # Dollar Index
    gold_price: float
    oil_price: float
    sp500_price: float
    
    # Análisis
    macro_regime: str
    macro_emoji: str
    pablo_gil_says: str
    risk_on_off: str
    
    timestamp: datetime
    
    @property
    def is_inverted(self) -> bool:
        """Curva invertida = Recesión próxima"""
        return self.yield_curve_spread < 0
    
    @property
    def recession_probability(self) -> str:
        """Probabilidad de recesión basada en curva"""
        if self.yield_curve_spread < -0.5:
            return "🔴 ALTA (>70%)"
        elif self.yield_curve_spread < 0:
            return "🟠 MODERADA (40-70%)"
        elif self.yield_curve_spread < 0.3:
            return "🟡 BAJA (20-40%)"
        return "🟢 MUY BAJA (<20%)"


class MacroService:
    """
    Servicio de análisis macroeconómico.
    Inspirado en el enfoque de Pablo Gil.
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_time = None
        self._cache_ttl_minutes = 5
    
    def _is_cache_valid(self) -> bool:
        if not self._cache_time:
            return False
        elapsed = (datetime.now() - self._cache_time).total_seconds() / 60
        return elapsed < self._cache_ttl_minutes
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_dashboard(_self) -> MacroDashboard:
        """
        Obtiene el dashboard macro completo.
        Los 4 Jinetes de Pablo Gil:
        1. Curva de Tipos
        2. VIX
        3. Dólar (DXY)
        4. Oro
        """
        try:
            # 1. Treasuries (Curva de Tipos)
            tnx = yf.Ticker("^TNX")  # 10Y
            irx = yf.Ticker("^IRX")  # 13W (proxy 2Y)
            
            t10y_hist = tnx.history(period="1d")
            t2y_hist = irx.history(period="1d")
            
            treasury_10y = t10y_hist['Close'].iloc[-1] if not t10y_hist.empty else 4.0
            treasury_2y = t2y_hist['Close'].iloc[-1] / 100 if not t2y_hist.empty else 4.0  # IRX está en basis points
            
            # Alternativa: Usar TYX para 30Y y calcular spread
            yield_spread = treasury_10y - treasury_2y
            
            # Determinar estado de curva
            if yield_spread < -0.5:
                curve_status = "🔴 INVERTIDA (Recesión inminente)"
            elif yield_spread < 0:
                curve_status = "🟠 LIGERAMENTE INVERTIDA"
            elif yield_spread < 0.3:
                curve_status = "🟡 APLANADA"
            else:
                curve_status = "🟢 NORMAL"
            
            # 2. VIX
            vix_ticker = yf.Ticker("^VIX")
            vix_hist = vix_ticker.history(period="1d")
            vix = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 20.0
            
            # 3. DXY (Dollar Index)
            dxy_ticker = yf.Ticker("DX-Y.NYB")
            dxy_hist = dxy_ticker.history(period="1d")
            dxy = dxy_hist['Close'].iloc[-1] if not dxy_hist.empty else 100.0
            
            # 4. Oro y Petróleo
            gold_ticker = yf.Ticker("GC=F")
            oil_ticker = yf.Ticker("CL=F")
            sp500_ticker = yf.Ticker("^GSPC")
            
            gold_hist = gold_ticker.history(period="1d")
            oil_hist = oil_ticker.history(period="1d")
            sp500_hist = sp500_ticker.history(period="1d")
            
            gold = gold_hist['Close'].iloc[-1] if not gold_hist.empty else 2000.0
            oil = oil_hist['Close'].iloc[-1] if not oil_hist.empty else 80.0
            sp500 = sp500_hist['Close'].iloc[-1] if not sp500_hist.empty else 5000.0
            
            # Análisis de Régimen Macro
            regime, emoji, risk = _self._analyze_regime(vix, treasury_10y, yield_spread, dxy)
            pablo_says = _self._what_would_pablo_say(vix, yield_spread, dxy, gold)
            
            return MacroDashboard(
                treasury_10y=treasury_10y,
                treasury_2y=treasury_2y,
                yield_curve_spread=yield_spread,
                curve_status=curve_status,
                vix=vix,
                dxy=dxy,
                gold_price=gold,
                oil_price=oil,
                sp500_price=sp500,
                macro_regime=regime,
                macro_emoji=emoji,
                pablo_gil_says=pablo_says,
                risk_on_off=risk,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo dashboard macro: {e}")
            return MacroDashboard(
                treasury_10y=0, treasury_2y=0, yield_curve_spread=0,
                curve_status="❌ ERROR",
                vix=0, dxy=0, gold_price=0, oil_price=0, sp500_price=0,
                macro_regime="OFFLINE", macro_emoji="⚪",
                pablo_gil_says="Error obteniendo datos macro",
                risk_on_off="NEUTRAL",
                timestamp=datetime.now()
            )
    
    def _analyze_regime(self, vix: float, t10y: float, spread: float, dxy: float) -> tuple:
        """Determina el régimen macro actual"""
        
        # Score de riesgo
        risk_score = 0
        
        if vix > 30:
            risk_score += 3
        elif vix > 25:
            risk_score += 2
        elif vix > 20:
            risk_score += 1
        
        if spread < 0:
            risk_score += 2
        
        if t10y > 5.0:
            risk_score += 2
        elif t10y > 4.5:
            risk_score += 1
        
        if dxy > 105:
            risk_score += 1
        
        # Clasificación
        if risk_score >= 5:
            return "CRISIS / RISK OFF", "🔴", "RISK OFF"
        elif risk_score >= 3:
            return "PRECAUCIÓN", "🟠", "NEUTRAL/DEFENSIVO"
        elif risk_score >= 2:
            return "VIGILANCIA", "🟡", "SELECTIVO"
        else:
            return "EXPANSIÓN", "🟢", "RISK ON"
    
    def _what_would_pablo_say(self, vix: float, spread: float, dxy: float, gold: float) -> str:
        """Genera un análisis estilo Pablo Gil"""
        
        comments = []
        
        # Curva de tipos
        if spread < 0:
            comments.append(f"🚨 ALERTA: La curva está invertida ({spread:.2f}). Históricamente, esto precede una recesión en 12-18 meses. No te dejes engañar por el rally.")
        elif spread < 0.3:
            comments.append(f"⚠️ La curva se está aplanando ({spread:.2f}). El mercado de bonos huele problemas.")
        
        # VIX
        if vix < 15:
            comments.append(f"😬 VIX en {vix:.1f}: Complacencia extrema. Cuando nadie tiene miedo, es momento de tenerlo. Los accidentes ocurren siempre que nadie mira.")
        elif vix > 25:
            comments.append(f"📊 VIX en {vix:.1f}: El mercado está nervioso. Esto puede ser oportunidad para el paciente, pero cuidado con coger cuchillos cayendo.")
        elif vix > 30:
            comments.append(f"🔴 VIX en {vix:.1f}: Pánico en el mercado. Históricamente, comprar con VIX >30 da buenos retornos... si puedes aguantar la volatilidad.")
        
        # Dólar
        if dxy > 105:
            comments.append(f"💵 Dólar fuerte ({dxy:.1f}). Presión para emergentes y commodities. Las empresas con deuda en USD sufrirán.")
        elif dxy < 100:
            comments.append(f"💵 Dólar débil ({dxy:.1f}). Viento de cola para activos de riesgo y emergentes.")
        
        # Oro
        if gold > 2100:
            comments.append(f"🥇 Oro en máximos ({gold:.0f}$). El mercado busca refugio. ¿Por qué si todo va tan bien?")
        
        if not comments:
            comments.append("📊 Entorno macro relativamente estable. Mantén la disciplina y no persigas activos.")
        
        return " | ".join(comments[:2])  # Max 2 comentarios
    
    def get_economic_calendar(self) -> List[Dict]:
        """
        Obtiene próximos eventos económicos importantes.
        (Placeholder - necesitaría API de calendario económico)
        """
        # En producción: usar OpenBB, FRED, o API de calendario
        events = [
            {"date": "Próximo", "event": "FOMC Meeting", "impact": "🔴 Alto"},
            {"date": "Próximo", "event": "Non-Farm Payrolls", "impact": "🔴 Alto"},
            {"date": "Próximo", "event": "CPI Inflation", "impact": "🔴 Alto"},
        ]
        return events
    
    def check_recession_signal(self) -> Dict:
        """
        Evalúa señales de recesión.
        Basado en metodología de inversión de curva.
        """
        dash = self.get_dashboard()
        
        signal = {
            "status": "UNKNOWN",
            "probability": "0%",
            "explanation": "",
            "action": ""
        }
        
        if dash.yield_curve_spread < -0.5:
            signal = {
                "status": "🔴 ALERTA MÁXIMA",
                "probability": ">70%",
                "explanation": "Curva profundamente invertida. Históricamente, recesión en 6-18 meses.",
                "action": "Reducir exposición a cíclicas. Aumentar caja. Considerar bonos de calidad."
            }
        elif dash.yield_curve_spread < 0:
            signal = {
                "status": "🟠 PRECAUCIÓN",
                "probability": "40-70%",
                "explanation": "Curva invertida. El mercado de bonos anticipa problemas.",
                "action": "Rotar hacia defensivos. No perseguir rallies. Aumentar calidad."
            }
        elif dash.yield_curve_spread < 0.3:
            signal = {
                "status": "🟡 VIGILANCIA",
                "probability": "20-40%",
                "explanation": "Curva aplanándose. Monitorear deterioro.",
                "action": "Mantener exposición pero con stops más ajustados."
            }
        else:
            signal = {
                "status": "🟢 EXPANSIÓN",
                "probability": "<20%",
                "explanation": "Curva normal. Sin señales de recesión inminente.",
                "action": "Mantener exposición a riesgo. Favorecer cíclicas y growth."
            }
        
        return signal
