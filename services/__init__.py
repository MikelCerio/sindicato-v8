"""
🏛️ Servicios del Sindicato V8 ELITE
Incluye todos los servicios institucionales.
"""

from .oracle import OraculoV8
from .market_data import MarketDataService, get_macro_context
from .sentiment import SentimentAnalyzer
from .pdf_generator import PDFGenerator
from .session_manager import SessionManager
from .comparator import TickerComparator, render_comparison_tab
from .charts import PriceChartService, render_charts_section

# === NUEVOS SERVICIOS ELITE ===
from .openbb_service import OpenBBService, KeyMetrics, FinancialStatements
from .portfolio_optimizer import (
    PortfolioOptimizer, 
    OptimizationResult,
    create_portfolio_pie_chart,
    create_efficient_frontier_chart
)
from .knowledge_library import (
    KnowledgeLibrary,
    BookInfo,
    SearchResult,
    add_essential_wisdom
)
from .report_renderer import HTMLReportRenderer
from .sec_analyzer import SECAnalyzer, SECFiling, format_filing_date, get_filing_icon
from .screener_service import ScreenerService
from .macro_service import MacroService, MacroDashboard

__all__ = [
    # Core Services
    'OraculoV8',
    'MarketDataService', 
    'get_macro_context',
    'SentimentAnalyzer',
    'PDFGenerator',
    'SessionManager',
    'TickerComparator',
    'render_comparison_tab',
    'PriceChartService',
    'render_charts_section',
    
    # Elite Services
    'OpenBBService',
    'KeyMetrics',
    'FinancialStatements',
    'PortfolioOptimizer',
    'OptimizationResult',
    'create_portfolio_pie_chart',
    'create_efficient_frontier_chart',
    'KnowledgeLibrary',
    'BookInfo',
    'SearchResult',
    'add_essential_wisdom',
    'HTMLReportRenderer',
    
    # SEC Analyzer (FinRobot-inspired)
    'SECAnalyzer',
    'SECFiling',
    'format_filing_date',
    'get_filing_icon',
    
    # Screener (Discovery)
    'ScreenerService',
    
    # Macro Service (Pablo Gil)
    'MacroService',
    'MacroDashboard',
]
