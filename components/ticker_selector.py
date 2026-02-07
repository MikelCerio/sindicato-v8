"""
🔍 TICKER SELECTOR COMPONENT
Componente reutilizable para seleccionar tickers
"""

import streamlit as st
from utils import get_all_tickers_formatted, parse_ticker_option, POPULAR_STOCKS


def ticker_selector(
    key: str = "ticker_selector",
    default_ticker: str = "TSLA",
    label: str = "Busca por nombre o ticker",
    show_manual_input: bool = True,
    show_info: bool = True
) -> str:
    """
    Componente de selección de ticker con búsqueda inteligente.
    
    Args:
        key: Key única para el componente
        default_ticker: Ticker por defecto
        label: Label del selectbox
        show_manual_input: Mostrar input manual
        show_info: Mostrar info de la empresa seleccionada
    
    Returns:
        Ticker seleccionado (uppercase)
    """
    
    all_options = get_all_tickers_formatted()
    
    # Encontrar índice del ticker por defecto
    default_option = None
    for i, opt in enumerate(all_options):
        if opt.startswith(f"{default_ticker} -"):
            default_option = i
            break
    
    if default_option is None:
        default_option = 0
    
    if show_manual_input:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_option = st.selectbox(
                label,
                options=all_options,
                index=default_option,
                key=f"{key}_select",
                help="Escribe para buscar. Ejemplo: 'Apple', 'AAPL', 'Microsoft', etc."
            )
            ticker = parse_ticker_option(selected_option)
        
        with col2:
            manual_ticker = st.text_input(
                "O escribe uno",
                placeholder="AAPL",
                key=f"{key}_manual",
                help="Para empresas no listadas"
            )
            
            if manual_ticker:
                ticker = manual_ticker.upper().strip()
    else:
        selected_option = st.selectbox(
            label,
            options=all_options,
            index=default_option,
            key=f"{key}_select",
            help="Escribe para buscar. Ejemplo: 'Apple', 'AAPL', 'Microsoft', etc."
        )
        ticker = parse_ticker_option(selected_option)
    
    # Mostrar info
    if show_info:
        if ticker in POPULAR_STOCKS:
            st.info(f"📊 **{ticker}** - {POPULAR_STOCKS[ticker]}")
        else:
            st.info(f"📊 **{ticker}**")
    
    return ticker.upper()


def multi_ticker_selector(
    key: str = "multi_ticker_selector",
    default_tickers: list = None,
    label: str = "Selecciona empresas",
    max_selections: int = 10
) -> list:
    """
    Selector de múltiples tickers.
    
    Args:
        key: Key única
        default_tickers: Lista de tickers por defecto
        label: Label del multiselect
        max_selections: Máximo de selecciones
    
    Returns:
        Lista de tickers seleccionados
    """
    
    if default_tickers is None:
        default_tickers = ["AAPL", "MSFT", "GOOGL"]
    
    all_options = get_all_tickers_formatted()
    
    # Encontrar opciones por defecto
    default_options = []
    for ticker in default_tickers:
        for opt in all_options:
            if opt.startswith(f"{ticker} -"):
                default_options.append(opt)
                break
    
    selected_options = st.multiselect(
        label,
        options=all_options,
        default=default_options,
        key=f"{key}_multi",
        help=f"Selecciona hasta {max_selections} empresas. Escribe para buscar.",
        max_selections=max_selections
    )
    
    tickers = [parse_ticker_option(opt) for opt in selected_options]
    
    return tickers
