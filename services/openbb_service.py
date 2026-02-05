"""
🧠 OPENBB SERVICE - Datos Institucionales
Integración con OpenBB Platform v4 para datos profesionales.
Replica las funcionalidades del OpenBB Terminal Pro:
- Financial Statements (Income, Balance, Cash Flow)
- Key Metrics & Ratios
- Estimates & Analyst Consensus
- Earnings Calendar & Transcripts
- Insider Activity
- Comparison Analysis
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


@dataclass
class FinancialStatements:
    """Estados financieros completos."""
    income_statement: Optional[pd.DataFrame] = None
    balance_sheet: Optional[pd.DataFrame] = None
    cash_flow: Optional[pd.DataFrame] = None


@dataclass
class KeyMetrics:
    """Métricas clave institucionales."""
    # Valuation
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    ps_ratio: float = 0.0
    peg_ratio: float = 0.0
    ev_ebitda: float = 0.0
    
    # Profitability
    gross_margin: float = 0.0
    operating_margin: float = 0.0
    net_margin: float = 0.0
    roe: float = 0.0
    roa: float = 0.0
    roic: float = 0.0
    
    # Liquidity
    current_ratio: float = 0.0
    quick_ratio: float = 0.0
    cash_ratio: float = 0.0
    
    # Leverage
    debt_to_equity: float = 0.0
    debt_to_assets: float = 0.0
    interest_coverage: float = 0.0
    
    # Efficiency
    asset_turnover: float = 0.0
    inventory_turnover: float = 0.0
    
    # Per Share
    eps: float = 0.0
    book_value_per_share: float = 0.0
    fcf_per_share: float = 0.0
    dividend_yield: float = 0.0
    
    raw_data: Dict = field(default_factory=dict)


@dataclass
class AnalystEstimates:
    """Estimaciones de analistas."""
    revenue_estimate: float = 0.0
    revenue_high: float = 0.0
    revenue_low: float = 0.0
    eps_estimate: float = 0.0
    eps_high: float = 0.0
    eps_low: float = 0.0
    num_analysts: int = 0
    recommendation: str = "N/A"
    target_price: float = 0.0
    target_high: float = 0.0
    target_low: float = 0.0


@dataclass
class EarningsEvent:
    """Evento de earnings."""
    date: str
    eps_actual: Optional[float] = None
    eps_estimate: Optional[float] = None
    revenue_actual: Optional[float] = None
    revenue_estimate: Optional[float] = None
    surprise_pct: Optional[float] = None


@dataclass 
class InsiderTrade:
    """Transacción de insider."""
    date: str
    insider_name: str
    position: str
    transaction_type: str  # Buy, Sell, Grant
    shares: int
    price: float
    value: float


class OpenBBService:
    """
    Servicio para acceder a datos institucionales via OpenBB Platform.
    
    Funcionalidades:
    - Financial Statements (Income, Balance, Cash Flow)
    - Key Ratios & Metrics
    - Analyst Estimates
    - Earnings Calendar
    - Insider Trading
    - Multi-ticker Comparison
    """
    
    def __init__(self):
        self._obb = None
        self._initialized = False
        
    def _ensure_init(self) -> bool:
        """Lazy initialization de OpenBB."""
        if self._initialized:
            return self._obb is not None
            
        try:
            from openbb import obb
            self._obb = obb
            self._initialized = True
            logger.info("OpenBB Platform inicializado correctamente")
            return True
        except ImportError:
            logger.warning("OpenBB no instalado. Usando yfinance como fallback.")
            self._initialized = True
            return False
        except Exception as e:
            logger.error(f"Error inicializando OpenBB: {e}")
            self._initialized = True
            return False
    
    # =========================================================================
    # FINANCIAL STATEMENTS
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_financial_statements(_self, ticker: str) -> Optional[FinancialStatements]:
        """
        Obtiene los 3 estados financieros principales.
        Similar a la pestaña "Financials" en OpenBB Terminal.
        """
        if not _self._ensure_init():
            return _self._get_financials_yfinance(ticker)
        
        try:
            result = FinancialStatements()
            
            # Income Statement
            try:
                income = _self._obb.equity.fundamental.income(
                    symbol=ticker, 
                    period="annual",
                    limit=5,
                    provider="yfinance"
                )
                result.income_statement = income.to_df() if income else None
            except:
                pass
            
            # Balance Sheet
            try:
                balance = _self._obb.equity.fundamental.balance(
                    symbol=ticker,
                    period="annual", 
                    limit=5,
                    provider="yfinance"
                )
                result.balance_sheet = balance.to_df() if balance else None
            except:
                pass
            
            # Cash Flow
            try:
                cashflow = _self._obb.equity.fundamental.cash(
                    symbol=ticker,
                    period="annual",
                    limit=5,
                    provider="yfinance"
                )
                result.cash_flow = cashflow.to_df() if cashflow else None
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo financials de {ticker}: {e}")
            return _self._get_financials_yfinance(ticker)
    
    def _get_financials_yfinance(self, ticker: str) -> Optional[FinancialStatements]:
        """Fallback usando yfinance directo."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            result = FinancialStatements()
            result.income_statement = stock.income_stmt
            result.balance_sheet = stock.balance_sheet
            result.cash_flow = stock.cashflow
            
            return result
        except Exception as e:
            logger.error(f"Error yfinance fallback: {e}")
            return None
    
    # =========================================================================
    # KEY METRICS & RATIOS
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_key_metrics(_self, ticker: str) -> Optional[KeyMetrics]:
        """
        Obtiene métricas clave institucionales.
        Similar al widget "Key Metrics" en OpenBB Terminal.
        """
        if not _self._ensure_init():
            return _self._get_metrics_yfinance(ticker)
        
        try:
            # Intentar obtener ratios de OpenBB
            ratios = _self._obb.equity.fundamental.ratios(
                symbol=ticker,
                provider="yfinance"
            )
            
            if ratios is None:
                return _self._get_metrics_yfinance(ticker)
            
            df = ratios.to_df()
            if df.empty:
                return _self._get_metrics_yfinance(ticker)
            
            # Tomar el período más reciente
            latest = df.iloc[0].to_dict() if len(df) > 0 else {}
            
            metrics = KeyMetrics(
                # Valuation
                pe_ratio=float(latest.get('pe_ratio', 0) or 0),
                pb_ratio=float(latest.get('price_to_book', 0) or 0),
                ps_ratio=float(latest.get('price_to_sales', 0) or 0),
                peg_ratio=float(latest.get('peg_ratio', 0) or 0),
                ev_ebitda=float(latest.get('ev_to_ebitda', 0) or 0),
                
                # Profitability
                gross_margin=float(latest.get('gross_profit_margin', 0) or 0),
                operating_margin=float(latest.get('operating_profit_margin', 0) or 0),
                net_margin=float(latest.get('net_profit_margin', 0) or 0),
                roe=float(latest.get('return_on_equity', 0) or 0),
                roa=float(latest.get('return_on_assets', 0) or 0),
                roic=float(latest.get('return_on_invested_capital', 0) or 0),
                
                # Liquidity
                current_ratio=float(latest.get('current_ratio', 0) or 0),
                quick_ratio=float(latest.get('quick_ratio', 0) or 0),
                cash_ratio=float(latest.get('cash_ratio', 0) or 0),
                
                # Leverage
                debt_to_equity=float(latest.get('debt_to_equity', 0) or 0),
                debt_to_assets=float(latest.get('debt_to_assets', 0) or 0),
                interest_coverage=float(latest.get('interest_coverage', 0) or 0),
                
                # Per Share
                eps=float(latest.get('earnings_per_share', 0) or 0),
                dividend_yield=float(latest.get('dividend_yield', 0) or 0),
                
                raw_data=latest
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de {ticker}: {e}")
            return _self._get_metrics_yfinance(ticker)
    
    def _get_metrics_yfinance(self, ticker: str) -> Optional[KeyMetrics]:
        """Fallback usando yfinance."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return KeyMetrics(
                pe_ratio=info.get('trailingPE', 0) or 0,
                pb_ratio=info.get('priceToBook', 0) or 0,
                ps_ratio=info.get('priceToSalesTrailing12Months', 0) or 0,
                peg_ratio=info.get('pegRatio', 0) or 0,
                ev_ebitda=info.get('enterpriseToEbitda', 0) or 0,
                gross_margin=info.get('grossMargins', 0) or 0,
                operating_margin=info.get('operatingMargins', 0) or 0,
                net_margin=info.get('profitMargins', 0) or 0,
                roe=info.get('returnOnEquity', 0) or 0,
                roa=info.get('returnOnAssets', 0) or 0,
                current_ratio=info.get('currentRatio', 0) or 0,
                quick_ratio=info.get('quickRatio', 0) or 0,
                debt_to_equity=info.get('debtToEquity', 0) or 0,
                eps=info.get('trailingEps', 0) or 0,
                dividend_yield=info.get('dividendYield', 0) or 0,
                raw_data=info
            )
        except Exception as e:
            logger.error(f"Error yfinance metrics: {e}")
            return None
    
    # =========================================================================
    # ANALYST ESTIMATES
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_estimates(_self, ticker: str) -> Optional[AnalystEstimates]:
        """Obtiene estimaciones de analistas."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return AnalystEstimates(
                revenue_estimate=info.get('revenueEstimate', 0) or 0,
                eps_estimate=info.get('epsCurrentYear', 0) or 0,
                num_analysts=info.get('numberOfAnalystOpinions', 0) or 0,
                recommendation=info.get('recommendationKey', 'N/A') or 'N/A',
                target_price=info.get('targetMeanPrice', 0) or 0,
                target_high=info.get('targetHighPrice', 0) or 0,
                target_low=info.get('targetLowPrice', 0) or 0
            )
        except Exception as e:
            logger.error(f"Error obteniendo estimates: {e}")
            return None
    
    # =========================================================================
    # EARNINGS HISTORY
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_earnings_history(_self, ticker: str, limit: int = 8) -> List[EarningsEvent]:
        """Obtiene historial de earnings."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            # Earnings history
            earnings = stock.earnings_history
            if earnings is None or earnings.empty:
                return []
            
            events = []
            for idx, row in earnings.head(limit).iterrows():
                event = EarningsEvent(
                    date=str(idx.date()) if hasattr(idx, 'date') else str(idx),
                    eps_actual=row.get('epsActual'),
                    eps_estimate=row.get('epsEstimate'),
                    surprise_pct=row.get('surprisePercent')
                )
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error obteniendo earnings history: {e}")
            return []
    
    # =========================================================================
    # INSIDER TRADING
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_insider_trades(_self, ticker: str, limit: int = 10) -> List[InsiderTrade]:
        """Obtiene transacciones de insiders."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            
            insider = stock.insider_transactions
            if insider is None or insider.empty:
                return []
            
            trades = []
            for _, row in insider.head(limit).iterrows():
                trade = InsiderTrade(
                    date=str(row.get('Start Date', '')),
                    insider_name=str(row.get('Insider Trading', 'Unknown')),
                    position=str(row.get('Position', '')),
                    transaction_type=str(row.get('Transaction', '')),
                    shares=int(row.get('Shares', 0) or 0),
                    price=float(row.get('Value', 0) or 0),
                    value=float(row.get('Value', 0) or 0)
                )
                trades.append(trade)
            
            return trades
        except Exception as e:
            logger.error(f"Error obteniendo insider trades: {e}")
            return []
    
    # =========================================================================
    # COMPARISON ANALYSIS
    # =========================================================================
    
    @st.cache_data(ttl=1800, show_spinner=False)
    def compare_tickers(_self, tickers: List[str]) -> Optional[pd.DataFrame]:
        """
        Compara múltiples tickers con métricas clave.
        Similar a "Comparison Analysis" en OpenBB Terminal.
        """
        if len(tickers) < 2:
            return None
        
        try:
            import yfinance as yf
            
            data = []
            for ticker in tickers:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                row = {
                    'Ticker': ticker,
                    'Name': info.get('shortName', ticker),
                    'Price': info.get('currentPrice', 0),
                    'Market Cap (B)': (info.get('marketCap', 0) or 0) / 1e9,
                    'P/E': info.get('trailingPE', 0),
                    'P/S': info.get('priceToSalesTrailing12Months', 0),
                    'P/B': info.get('priceToBook', 0),
                    'EV/EBITDA': info.get('enterpriseToEbitda', 0),
                    'Dividend Yield': (info.get('dividendYield', 0) or 0) * 100,
                    'Gross Margin': (info.get('grossMargins', 0) or 0) * 100,
                    'Net Margin': (info.get('profitMargins', 0) or 0) * 100,
                    'ROE': (info.get('returnOnEquity', 0) or 0) * 100,
                    'Debt/Equity': info.get('debtToEquity', 0),
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df = df.set_index('Ticker')
            
            return df
            
        except Exception as e:
            logger.error(f"Error en comparison: {e}")
            return None
    
    # =========================================================================
    # SECTOR/INDUSTRY INFO
    # =========================================================================
    
    @st.cache_data(ttl=7200, show_spinner=False)
    def get_company_profile(_self, ticker: str) -> Dict[str, Any]:
        """Obtiene perfil completo de la empresa."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'ceo': info.get('companyOfficers', [{}])[0].get('name', 'N/A') if info.get('companyOfficers') else 'N/A',
            }
        except Exception as e:
            logger.error(f"Error obteniendo profile: {e}")
            return {}
