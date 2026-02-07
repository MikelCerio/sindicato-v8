"""
🔍 TICKER SEARCH - Búsqueda inteligente de empresas
Permite buscar por nombre o ticker
"""

import pandas as pd
from typing import Optional, List, Tuple

# Lista de empresas populares (Top 500 S&P 500 + otras importantes)
POPULAR_STOCKS = {
    # Tech Giants
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc. (Google)",
    "GOOG": "Alphabet Inc. Class C",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc. (Facebook)",
    "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla Inc.",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel Corporation",
    "CRM": "Salesforce Inc.",
    "ORCL": "Oracle Corporation",
    "ADBE": "Adobe Inc.",
    "NFLX": "Netflix Inc.",
    "PYPL": "PayPal Holdings Inc.",
    "SHOP": "Shopify Inc.",
    "SQ": "Block Inc. (Square)",
    "UBER": "Uber Technologies Inc.",
    "ABNB": "Airbnb Inc.",
    "SNOW": "Snowflake Inc.",
    
    # Finance
    "JPM": "JPMorgan Chase & Co.",
    "BAC": "Bank of America Corp.",
    "WFC": "Wells Fargo & Company",
    "GS": "Goldman Sachs Group Inc.",
    "MS": "Morgan Stanley",
    "C": "Citigroup Inc.",
    "BLK": "BlackRock Inc.",
    "SCHW": "Charles Schwab Corp.",
    "AXP": "American Express Company",
    "V": "Visa Inc.",
    "MA": "Mastercard Inc.",
    "BRK.B": "Berkshire Hathaway Inc. Class B",
    "BRK.A": "Berkshire Hathaway Inc. Class A",
    
    # Healthcare
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth Group Inc.",
    "PFE": "Pfizer Inc.",
    "ABBV": "AbbVie Inc.",
    "TMO": "Thermo Fisher Scientific",
    "ABT": "Abbott Laboratories",
    "MRK": "Merck & Co. Inc.",
    "LLY": "Eli Lilly and Company",
    "AMGN": "Amgen Inc.",
    "GILD": "Gilead Sciences Inc.",
    
    # Consumer
    "WMT": "Walmart Inc.",
    "HD": "Home Depot Inc.",
    "PG": "Procter & Gamble Co.",
    "KO": "Coca-Cola Company",
    "PEP": "PepsiCo Inc.",
    "COST": "Costco Wholesale Corp.",
    "NKE": "Nike Inc.",
    "MCD": "McDonald's Corporation",
    "SBUX": "Starbucks Corporation",
    "DIS": "Walt Disney Company",
    "CMCSA": "Comcast Corporation",
    
    # Energy
    "XOM": "Exxon Mobil Corporation",
    "CVX": "Chevron Corporation",
    "COP": "ConocoPhillips",
    "SLB": "Schlumberger Limited",
    
    # Industrial
    "BA": "Boeing Company",
    "CAT": "Caterpillar Inc.",
    "GE": "General Electric Company",
    "MMM": "3M Company",
    "HON": "Honeywell International",
    
    # Telecom
    "T": "AT&T Inc.",
    "VZ": "Verizon Communications",
    "TMUS": "T-Mobile US Inc.",
    
    # Retail
    "TGT": "Target Corporation",
    "LOW": "Lowe's Companies Inc.",
    "TJX": "TJX Companies Inc.",
    
    # Semiconductors
    "TSM": "Taiwan Semiconductor",
    "ASML": "ASML Holding NV",
    "QCOM": "Qualcomm Inc.",
    "AVGO": "Broadcom Inc.",
    "TXN": "Texas Instruments",
    "MU": "Micron Technology",
    
    # Automotive
    "F": "Ford Motor Company",
    "GM": "General Motors Company",
    "RIVN": "Rivian Automotive Inc.",
    "LCID": "Lucid Group Inc.",
    
    # Aerospace
    "LMT": "Lockheed Martin Corp.",
    "RTX": "Raytheon Technologies",
    "NOC": "Northrop Grumman Corp.",
    
    # Crypto/Fintech
    "COIN": "Coinbase Global Inc.",
    "HOOD": "Robinhood Markets Inc.",
    
    # Spanish Companies
    "BBVA": "Banco Bilbao Vizcaya Argentaria",
    "SAN": "Banco Santander SA",
    "TEF": "Telefónica SA",
    "IBE": "Iberdrola SA",
    "ITX": "Inditex SA (Zara)",
    "REP": "Repsol SA",
    
    # European
    "ASML": "ASML Holding NV",
    "SAP": "SAP SE",
    "NVO": "Novo Nordisk A/S",
    "NESN": "Nestlé SA",
    
    # Asian
    "BABA": "Alibaba Group Holding",
    "TSM": "Taiwan Semiconductor",
    "SONY": "Sony Group Corporation",
    "NIO": "NIO Inc.",
    "BIDU": "Baidu Inc.",
    
    # ETFs
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust",
    "VOO": "Vanguard S&P 500 ETF",
    "VTI": "Vanguard Total Stock Market ETF",
    "IWM": "iShares Russell 2000 ETF",
}


def search_ticker(query: str) -> List[Tuple[str, str]]:
    """
    Busca tickers que coincidan con la query.
    
    Args:
        query: Texto a buscar (ticker o nombre)
    
    Returns:
        Lista de tuplas (ticker, nombre)
    """
    if not query:
        return []
    
    query = query.upper().strip()
    results = []
    
    for ticker, name in POPULAR_STOCKS.items():
        # Buscar en ticker
        if query in ticker.upper():
            results.append((ticker, name))
        # Buscar en nombre
        elif query.lower() in name.lower():
            results.append((ticker, name))
    
    return results[:20]  # Limitar a 20 resultados


def get_ticker_name(ticker: str) -> Optional[str]:
    """Obtiene el nombre de una empresa dado su ticker"""
    return POPULAR_STOCKS.get(ticker.upper())


def format_ticker_option(ticker: str, name: str) -> str:
    """Formatea una opción para mostrar en selectbox"""
    return f"{ticker} - {name}"


def parse_ticker_option(option: str) -> str:
    """Extrae el ticker de una opción formateada"""
    return option.split(" - ")[0].strip()


def get_all_tickers_formatted() -> List[str]:
    """Obtiene todas las empresas formateadas para selectbox"""
    return [
        format_ticker_option(ticker, name)
        for ticker, name in sorted(POPULAR_STOCKS.items(), key=lambda x: x[1])
    ]


def get_popular_tickers() -> List[str]:
    """Obtiene lista de tickers populares (sin formatear)"""
    return list(POPULAR_STOCKS.keys())
