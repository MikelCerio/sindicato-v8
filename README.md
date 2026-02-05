# 🏛️ Sindicato V8 ELITE - Institutional Investment Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Streamlit-1.30+-red?style=for-the-badge&logo=streamlit">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4-green?style=for-the-badge&logo=openai">
  <img src="https://img.shields.io/badge/OpenBB-v4-yellow?style=for-the-badge">
</p>

**Sindicato V8 ELITE** es una plataforma de análisis de inversiones de grado institucional que combina:

- 🧠 **Chain of Thought** - Agentes que razonan paso a paso como consultoras top
- 📊 **OpenBB Platform** - Datos financieros profesionales
- ⚖️ **Markowitz Optimizer** - Asignación óptima de capital
- 📚 **Knowledge Library** - Sabiduría de Buffett, Munger, Graham integrada
- 🦈 **Investment Committee** - Multi-agentes especializados con CrewAI

---

## ✨ Features

### 📊 Datos Institucionales (OpenBB)
- Financial Statements (Income, Balance, Cash Flow)
- Key Metrics & Ratios
- Analyst Estimates & Targets
- Insider Trading Activity
- Multi-ticker Comparison

### ⚖️ Portfolio Optimizer
- Modern Portfolio Theory (Markowitz)
- Maximización de Ratio Sharpe
- Frontera Eficiente interactiva
- Contribución al riesgo por activo

### 🦈 Investment Committee (AI Agents)
- **Forensic Auditor**: Detecta trampas contables
- **Growth Analyst**: Valida innovación real vs humo
- **Risk Hunter**: Encuentra deal-breakers
- **CIO**: Decisión final con Chain of Thought

### 📚 Knowledge Library
- Sube libros de inversión (PDF, TXT)
- Indexa con FAISS para búsqueda semántica
- La IA cruza el análisis con principios de los maestros
- Pre-cargado: Buffett, Munger, Graham

---

## 🚀 Quick Start

### Opción 1: Streamlit Cloud (Recomendado)

1. Fork este repositorio
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo
4. Configura secrets:
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
```
5. ¡Deploy!

### Opción 2: Local

```bash
# Clonar
git clone https://github.com/tu-usuario/sindicato-v8.git
cd sindicato-v8

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key
cp .env.example .env
# Editar .env y añadir tu OPENAI_API_KEY

# Ejecutar
streamlit run app.py
```

### Opción 3: Google Colab

```python
# Celda 1: Instalar
!pip install -q streamlit yfinance pandas crewai langchain langchain-openai openai faiss-cpu pdfplumber beautifulsoup4 textblob reportlab plotly python-dotenv openbb pypfopt pyngrok

# Celda 2: Subir archivos (desde este repo)
# Sube la carpeta sindicato_v8/ a /content/

# Celda 3: Ejecutar
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'

from pyngrok import ngrok
!streamlit run /content/sindicato_v8/app.py &
public_url = ngrok.connect(8501)
print(public_url)
```

---

## 📁 Estructura del Proyecto

```
sindicato_v8/
├── app.py                 # App principal ELITE
├── config.py              # Configuración centralizada
├── prompts.py             # Prompts con Chain of Thought
├── requirements.txt       # Dependencias
├── .env.example           # Template de variables
│
├── agents/
│   ├── __init__.py
│   ├── committee.py       # Investment Committee (CrewAI)
│   └── mentor.py          # Learning Oracle
│
├── services/
│   ├── __init__.py
│   ├── oracle.py          # RAG con FAISS
│   ├── market_data.py     # Datos de mercado
│   ├── sentiment.py       # Análisis de sentiment
│   ├── charts.py          # Gráficos Plotly
│   ├── comparator.py      # Comparador de tickers
│   ├── pdf_generator.py   # Generador de memos
│   ├── session_manager.py # Persistencia
│   │
│   │── # ELITE SERVICES
│   ├── openbb_service.py      # OpenBB Platform integration
│   ├── portfolio_optimizer.py # Markowitz optimizer
│   └── knowledge_library.py   # RAG para libros
│
└── .streamlit/
    └── secrets.toml       # Secrets para Streamlit Cloud
```

---

## 🔑 API Keys Necesarias

| Servicio | Variable | Requerido |
|----------|----------|-----------|
| OpenAI | `OPENAI_API_KEY` | ✅ Sí |
| OpenBB | - | ❌ No (usa providers gratuitos) |

---

## 📖 Guía de Uso

### 1️⃣ Análisis Rápido
1. Escribe un ticker (ej: `TSLA`)
2. Ve a pestaña **OPENBB** → Click "Cargar Datos"
3. Revisa métricas clave y estados financieros

### 2️⃣ Optimización de Portfolio
1. Ve a pestaña **OPTIMIZER**
2. Escribe 3-5 tickers (ej: `AAPL, MSFT, GOOGL, AMZN`)
3. Selecciona estrategia (Max Sharpe recomendado)
4. Click "OPTIMIZAR" → Ver asignación óptima

### 3️⃣ Análisis Profundo (10-K)
1. Ve a pestaña **DOCS** → Sube un 10-K (HTML de SEC)
2. Ve a **COMITÉ** → Click "AUDITAR"
3. Espera 60-90s mientras los agentes analizan
4. Ve a **VEREDICTO** → Click "EMITIR SENTENCIA"

### 4️⃣ Enriquecer con Sabiduría
1. Ve a pestaña **BIBLIOTECA**
2. Click "Cargar Sabiduría Básica" (Buffett, Munger, Graham)
3. O sube tus propios libros de inversión
4. Los agentes ahora cruzarán análisis con principios de los maestros

---

## 🧠 Chain of Thought

Los agentes siguen un protocolo de razonamiento obligatorio:

```
PASO 1: EXTRACCIÓN DE HECHOS
- Cita el número EXACTO del texto
- Identifica: Ingreso, Gasto, Deuda, Cash, Margen, ROE, FCF

PASO 2: CRUCE DE DATOS
- Compara con histórico de la empresa
- Compara con peers del sector
- Evalúa contexto macro (VIX/Bonos)

PASO 3: ABOGADO DEL DIABLO
- Busca por qué la tesis podría FALLAR
- ¿Qué ignora la directiva?
- ¿Cuál es el escenario catastrófico?

PASO 4: SÍNTESIS
- Conclusión CONSECUENCIA de los pasos anteriores
```

---

## 📄 License

MIT License - Uso libre para fines educativos y personales.

---

## 🤝 Contribuir

1. Fork el repo
2. Crea una rama (`git checkout -b feature/nueva-feature`)
3. Commit (`git commit -m 'Add nueva feature'`)
4. Push (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

---

## 📬 Contacto

¿Preguntas? Abre un Issue en GitHub.

---

<p align="center">
  <strong>🏛️ Capital Preservation First</strong><br>
  <em>"La regla #1 es no perder dinero. La regla #2 es no olvidar la regla #1."</em> - Warren Buffett
</p>
