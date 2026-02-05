# 📚 GUÍA PRÁCTICA: Sindicato V8
## Manual de Uso con Ejemplos Reales

---

## 🎯 Índice

1. [Configuración Inicial](#1-configuración-inicial)
2. [Análisis de una Acción (Ejemplo: NVDA)](#2-análisis-completo-ejemplo-nvda)
3. [Comparar Acciones (Ejemplo: Big Tech)](#3-comparar-acciones)
4. [Interpretar el Veredicto](#4-interpretar-el-veredicto)
5. [Usar el Mentor](#5-usar-el-mentor)
6. [Casos de Uso Avanzados](#6-casos-de-uso-avanzados)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Configuración Inicial

### 1.1 Primera vez en Colab

```python
# CELDA 1: Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

# CELDA 2: Ir al directorio del proyecto
import os
os.chdir('/content/drive/MyDrive/Investing_vitaminado/sindicato_v8')

# CELDA 3: Instalar dependencias
!pip install -q streamlit yfinance pandas plotly crewai langchain langchain-openai langchain-community faiss-cpu pdfplumber beautifulsoup4 textblob reportlab pyngrok

# CELDA 4: Configurar API Key (OBLIGATORIO)
import os
os.environ['OPENAI_API_KEY'] = 'sk-tu-api-key-aqui'  # ← Reemplaza con tu key

# CELDA 5: Ejecutar la aplicación
!streamlit run app.py &>/dev/null &

# CELDA 6: Crear túnel público
from pyngrok import ngrok
public_url = ngrok.connect(8501)
print(f"🚀 Tu aplicación está en: {public_url}")
```

### 1.2 Estructura de carpetas en Drive

```
📁 Investing_vitaminado/
├── 📁 1_BIBLIOTECA/          ← Aquí se guardan los 10-K que subas
├── 📁 4_DATOS/
│   └── 📁 vectordb/          ← Base de datos vectorial (automático)
├── 📁 5_HISTORICO/
│   └── 📁 debates/           ← Análisis guardados (JSON)
├── 📁 6_EXPORTS/             ← PDFs exportados
└── 📁 sindicato_v8/          ← El código de la aplicación
```

---

## 2. Análisis Completo (Ejemplo: NVDA)

### Paso 1: Obtener el 10-K

1. Ve a [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=nvidia&type=10-K)
2. Busca "NVIDIA" → Selecciona el 10-K más reciente
3. Descarga el archivo HTML (el documento completo)
4. Guárdalo como `NVDA_10K_2024.html`

### Paso 2: Subir el documento

1. En Sindicato V8, ve a la pestaña **📂 DOCS**
2. Click en "Browse files" → Selecciona tu 10-K
3. Click **⚙️ Procesar**
4. Espera a que diga "✅ X chunks indexados"

```
Ejemplo de output esperado:
✅ 847 chunks indexados
Secciones detectadas:
✅ Balance Sheet
✅ Income Statement
✅ Cash Flow
✅ Risk Factors
✅ MD&A
```

### Paso 3: Ver datos fundamentales

En la pestaña **📊 DATOS**:

```
💹 Fundamentales NVDA (Ejemplo)
┌─────────────────┬────────────┐
│ Precio          │ $875.50    │
│ Market Cap      │ $2.16T     │
│ P/E             │ 65.3       │
│ Forward P/E     │ 38.2       │
│ ROE             │ 91.5%      │
│ Debt/Equity     │ 0.41       │
│ Valoración      │ 🔴 Cara    │
│ Calidad         │ 🟢 Alta    │
└─────────────────┴────────────┘
```

**Interpretación:**
- P/E de 65 es alto → Valoración cara
- ROE de 91% es excepcional → Calidad altísima
- Debt/Equity de 0.41 es bajo → Balance sólido

### Paso 4: Revisar Sentiment de Noticias

```
📰 Sentiment NVDA
┌────────────────────────────────────────┬─────────┐
│ 🟢 NVIDIA beats Q4 estimates           │ +0.45   │
│ 🟢 AI demand surge continues           │ +0.38   │
│ 🟡 Competition from AMD intensifies    │ +0.05   │
│ 🟢 Data center revenue up 400%         │ +0.52   │
│ 🔴 China export restrictions concern   │ -0.22   │
└────────────────────────────────────────┴─────────┘
Sentiment Global: 🟢 BULLISH (Score: +0.24)
```

### Paso 5: Ejecutar Auditoría del Comité

En la pestaña **🦈 COMITÉ**, click en **🔥 AUDITAR**

Espera 60-90 segundos. Verás 3 columnas:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 💰 VALUE AUDIT              │ 🚀 GROWTH AUDIT           │ 💀 RISK AUDIT     │
├─────────────────────────────┼───────────────────────────┼───────────────────┤
│ Deuda Total: $9.7B          │ I+D: $7.3B (18% Revenue)  │ RIESGO 1:         │
│ Cash: $18.3B                │ Tendencia: +42% YoY       │ China representa  │
│ Deuda Neta: -$8.6B          │                           │ 22% de ventas.    │
│ (CAJA NETA POSITIVA ✅)     │ Pipeline:                 │ Restricciones     │
│                             │ - Blackwell (2024)        │ pueden impactar.  │
│ Debt/EBITDA: 0.3x           │ - Grace Hopper (2025)     │                   │
│ Interest Coverage: 58x      │ - AI Enterprise Suite     │ RIESGO 2:         │
│                             │                           │ Concentración en  │
│ Goodwill: $4.4B (3% assets) │ Patentes: 12,500+         │ data centers.     │
│ → Bajo, no preocupante      │                           │                   │
│                             │ VEREDICTO:                │ RIESGO 3:         │
│ VEREDICTO:                  │ 🟢 INNOVADOR REAL         │ Valoración alta   │
│ 🟢 BALANCE SÓLIDO           │                           │ puede corregir.   │
│                             │                           │                   │
│                             │                           │ DEAL-BREAKERS:    │
│                             │                           │ ❌ Ninguno        │
└─────────────────────────────┴───────────────────────────┴───────────────────┘
```

### Paso 6: Obtener Veredicto Final

En la pestaña **⚖️ VEREDICTO**, click en **⚖️ SENTENCIA (10.000€)**

```
🏛️ VEREDICTO DEL CIO

## 🐂 BULL CASE
1. Caja neta de $8.6B proporciona colchón de seguridad
2. I+D masivo ($7.3B) con pipeline de productos concretos
3. Moat competitivo en GPUs para IA (90%+ market share)

## 🐻 BEAR CASE
1. Valoración extrema (P/E 65x, Forward P/E 38x)
2. Concentración en data centers (dependencia de pocos clientes)
3. Riesgo geopolítico China (22% de ventas en riesgo)

## ⛔ DEAL-BREAKERS
Ninguno identificado. Los riesgos son manejables.

## 🎯 DECISIÓN FINAL
**MANTENER WATCHLIST** 
(Esperar corrección para entrar)

## 📊 NIVEL DE CONVICCIÓN
**Media** - El negocio es excepcional pero la valoración no da margen de seguridad.
```

```
💶 ASIGNACIÓN DE CAPITAL (10.000€)

| Destino    | Cantidad | Justificación                          |
|------------|----------|----------------------------------------|
| NVDA       | €0       | Esperar mejor punto de entrada         |
| Caja       | €10,000  | Valoración no ofrece margen seguridad  |

🎯 PARÁMETROS DE ENTRADA
- Precio Actual: $875
- Precio de Entrada Sugerido: $650-700 (esperar -20/25%)
- Stop-Loss: $550 (-15% desde entrada)
- Target 1: $900 (+35%)
- Target 2: $1,100 (+65%)

⚡ RATIO RIESGO/BENEFICIO
Si entra a $700: 2.5:1 ✅ Aceptable

📅 HORIZONTE TEMPORAL
Largo plazo (2-3 años)
```

### Paso 7: Descargar PDF

Click en **📄 PDF** para descargar el Investment Memo completo.

---

## 3. Comparar Acciones

### Ejemplo: Comparar Big Tech

En la pestaña **🔄 COMPARAR**:

```
Tickers: AAPL, MSFT, GOOGL, AMZN
```

Click **🔍 Comparar**

### Resultado:

```
🏆 Mejor opción: MSFT (Score: 42.3)

┌────────┬─────────┬────────┬────────┬───────────┬────────────┬───────────┐
│ Ticker │ Precio  │ P/E    │ ROE    │ Margin    │ Debt/Eq    │ Growth    │
├────────┼─────────┼────────┼────────┼───────────┼────────────┼───────────┤
│ AAPL   │ $185    │ 28.5   │ 147%   │ 25.3%     │ 1.8        │ +2.1%     │
│ MSFT   │ $415    │ 35.2   │ 38.5%  │ 35.1%     │ 0.3        │ +12.4%    │
│ GOOGL  │ $142    │ 24.8   │ 25.2%  │ 24.8%     │ 0.1        │ +8.7%     │
│ AMZN   │ $178    │ 58.3   │ 17.8%  │ 6.4%      │ 0.7        │ +11.8%    │
└────────┴─────────┴────────┴────────┴───────────┴────────────┴───────────┘
```

**¿Por qué MSFT gana?**
- Mejor margen de beneficio (35%)
- Menor deuda relativa (0.3)
- Crecimiento sólido (12%)
- P/E razonable para la calidad

---

## 4. Interpretar el Veredicto

### Decisiones posibles:

| Decisión | Significado | Acción sugerida |
|----------|-------------|-----------------|
| **COMPRAR** | Fundamentales + Valoración atractivos | Ejecutar allocation sugerida |
| **MANTENER WATCHLIST** | Buen negocio pero valoración cara | Esperar corrección |
| **EVITAR** | Deal-breakers o riesgos inaceptables | No invertir, buscar alternativas |

### Niveles de convicción:

| Nivel | Allocation típica |
|-------|-------------------|
| Alta | 25-30% del capital |
| Media | 10-20% del capital |
| Baja | 0-5% o solo watchlist |

### Red Flags a vigilar:

🚨 **Deal-Breakers (EVITAR siempre):**
- Deuda Neta / EBITDA > 4x
- Investigaciones SEC/DOJ activas
- CFO/Auditor cambiados recientemente
- Net Income >> Operating Cash Flow
- Insider selling masivo

---

## 5. Usar el Mentor

### Ejemplo 1: Entender un concepto

**Pregunta:** "¿Qué es el Free Cash Flow y por qué es importante?"

**Respuesta del Mentor:**
```
## ¿Qué es?
El Free Cash Flow (FCF) es el efectivo que genera una empresa 
después de pagar todos sus gastos operativos e inversiones en 
activos (CAPEX).

Fórmula: FCF = Operating Cash Flow - Capital Expenditures

## ¿Por qué importa?
Es el dinero "real" que queda para:
- Pagar dividendos
- Recomprar acciones
- Reducir deuda
- Hacer adquisiciones

## Ejemplo práctico
Apple 2023:
- Operating Cash Flow: $110B
- CAPEX: $11B
- Free Cash Flow: $99B

Con $99B, Apple puede:
- Pagar $15B en dividendos
- Recomprar $80B en acciones
- Aún le sobran $4B

## Cómo usarlo
- FCF Yield > 5% → Posiblemente infravalorada
- FCF creciente YoY → Negocio saludable
- FCF negativo → Problema (salvo startups)

## Trampa común
No confundir Net Income con FCF. Una empresa puede 
tener beneficios contables pero quemar caja.
```

### Ejemplo 2: Pregunta sobre el documento

**Pregunta:** "¿Cuánto gastó NVIDIA en I+D?"

**Respuesta del Mentor:**
```
Según el 10-K de NVIDIA:

📊 Gasto en I+D
- FY 2024: $7,339 millones
- FY 2023: $5,268 millones
- Crecimiento YoY: +39%

📈 Como % de Revenue
- FY 2024: 18.2% de $40.3B revenue
- FY 2023: 19.5% de $27.0B revenue

💡 Interpretación
El ratio I+D/Revenue es alto (típico en semiconductores).
Que mantenga ~18% mientras crece tanto indica 
compromiso real con innovación, no recortes para 
inflar márgenes artificialmente.
```

---

## 6. Casos de Uso Avanzados

### 6.1 Análisis de competidores

1. Analiza el líder del sector (ej: NVDA)
2. Compara con competidores (AMD, INTC, QCOM)
3. Busca el "mejor negocio a precio razonable"

### 6.2 Screening previo

Antes de analizar en profundidad:
1. Revisa fundamentales en Tab 1
2. Si P/E > 40 y ROE < 15% → Probablemente skip
3. Si Debt/Equity > 2 → Requiere análisis de deuda

### 6.3 Seguimiento de posiciones

1. Guarda análisis en el historial
2. Revisita cuando haya earnings
3. Compara nuevo 10-K vs anterior

### 6.4 Construir watchlist

```
Ejemplo de watchlist estructurada:

| Ticker | Última review | Decisión            | Precio target |
|--------|---------------|---------------------|---------------|
| NVDA   | 2024-02-04    | Watchlist @ $650    | Esperar -25%  |
| META   | 2024-01-15    | Comprar             | Ejecutado $470|
| GOOGL  | 2024-01-20    | Watchlist @ $130    | Esperar -8%   |
```

---

## 7. Troubleshooting

### Error: "No hay documentos cargados"
**Solución:** Ve a Tab 📂 DOCS y sube un 10-K primero.

### Error: "API Key inválida"  
**Solución:** Verifica que configuraste correctamente:
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'  # Sin espacios
```

### La app no carga
**Solución:** Reinicia el kernel de Colab y ejecuta todas las celdas de nuevo.

### Los datos de Yahoo Finance no cargan
**Solución:** El ticker puede ser incorrecto. Usa el símbolo exacto de Yahoo Finance (ej: BRK-B, no BRK.B).

### El análisis tarda demasiado
**Solución:** Normal. El comité con 5 agentes tarda 60-90s. Si pasa de 3 minutos, puede haber timeout de la API.

---

## 📝 Checklist Rápido

Antes de cada análisis:

- [ ] ¿Tengo el 10-K más reciente?
- [ ] ¿Está indexado correctamente?
- [ ] ¿Revisé el contexto macro (VIX, tasas)?
- [ ] ¿Comparé con competidores?
- [ ] ¿Guardé el análisis en historial?
- [ ] ¿Exporté el PDF si es importante?

---

## 🎓 Recursos Adicionales

- [SEC EDGAR](https://www.sec.gov/edgar) - 10-K y 10-Q oficiales
- [Yahoo Finance](https://finance.yahoo.com) - Datos de mercado
- [OpenBB](https://openbb.co) - Terminal de análisis alternativo
- [Dataroma](https://www.dataroma.com) - Posiciones de hedge funds

---

*"La inversión exitosa es gestión del riesgo, no su eliminación."*
— Benjamin Graham
