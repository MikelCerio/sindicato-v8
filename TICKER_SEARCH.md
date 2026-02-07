# 🔍 Búsqueda Inteligente de Empresas

## ✨ Características

La app ahora incluye un **buscador inteligente** que facilita encontrar empresas:

### 🎯 Búsqueda por Nombre o Ticker

Puedes buscar empresas de 3 formas:

1. **Por nombre**: Escribe "Apple" → Encuentra AAPL
2. **Por ticker**: Escribe "AAPL" → Encuentra Apple Inc.
3. **Manual**: Para empresas no listadas

---

## 📊 Empresas Incluidas

### 🇺🇸 Tech Giants (20+)
- Apple (AAPL), Microsoft (MSFT), Google (GOOGL)
- Amazon (AMZN), Meta (META), NVIDIA (NVDA)
- Tesla (TSLA), Netflix (NFLX), PayPal (PYPL)
- Y más...

### 💰 Finanzas (15+)
- JPMorgan (JPM), Bank of America (BAC)
- Goldman Sachs (GS), Visa (V), Mastercard (MA)
- Berkshire Hathaway (BRK.B)
- Y más...

### 🏥 Healthcare (10+)
- Johnson & Johnson (JNJ), Pfizer (PFE)
- UnitedHealth (UNH), Abbott (ABT)
- Y más...

### 🛒 Consumer (15+)
- Walmart (WMT), Coca-Cola (KO), Nike (NKE)
- McDonald's (MCD), Starbucks (SBUX), Disney (DIS)
- Y más...

### 🇪🇸 Empresas Españolas
- BBVA, Santander (SAN), Telefónica (TEF)
- Iberdrola (IBE), Inditex/Zara (ITX), Repsol (REP)

### 🌍 Internacionales
- ASML, SAP, Nestlé, Alibaba (BABA)
- Taiwan Semiconductor (TSM), Sony, NIO
- Y más...

### 📈 ETFs Populares
- SPY, QQQ, VOO, VTI, IWM

**Total: 150+ empresas**

---

## 🎨 Cómo Usar

### En la Pantalla Principal

1. **Busca en el selectbox:**
   ```
   Escribe "Tesla" o "TSLA"
   → Selecciona "TSLA - Tesla Inc."
   ```

2. **O escribe manualmente:**
   ```
   Para empresas no listadas (ej: pequeñas caps)
   Escribe el ticker directamente
   ```

3. **La app muestra:**
   ```
   📊 TSLA - Tesla Inc.
   ```

---

## 🔧 Para Desarrolladores

### Añadir Más Empresas

Edita `utils/ticker_search.py`:

```python
POPULAR_STOCKS = {
    # ... empresas existentes ...
    
    # Añade las tuyas
    "NVDA": "NVIDIA Corporation",
    "AMD": "Advanced Micro Devices",
}
```

### Usar el Componente en Otras Páginas

```python
from components import ticker_selector

# Selector simple
ticker = ticker_selector(
    key="my_ticker",
    default_ticker="AAPL",
    label="Selecciona una empresa"
)

# Selector múltiple
from components import multi_ticker_selector

tickers = multi_ticker_selector(
    key="portfolio",
    default_tickers=["AAPL", "MSFT", "GOOGL"],
    label="Selecciona tu portfolio",
    max_selections=10
)
```

---

## 💡 Tips

1. **Búsqueda rápida**: Empieza a escribir y el selectbox filtra automáticamente
2. **Empresas no listadas**: Usa el input manual de la derecha
3. **Autocomplete**: Streamlit autocompleta mientras escribes

---

## 🚀 Próximas Mejoras

- [ ] Integración con API de Yahoo Finance para validar tickers
- [ ] Búsqueda por sector/industria
- [ ] Favoritos del usuario
- [ ] Historial de búsquedas recientes
- [ ] Sugerencias basadas en análisis previos

---

¿Quieres añadir más empresas? Abre un issue o PR en GitHub.
