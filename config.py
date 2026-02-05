"""
🏛️ SINDICATO V8 - Configuración Central
Optimizado para Google Colab
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

# ============================================================================
# 🔧 DETECCIÓN DE ENTORNO
# ============================================================================

def is_colab() -> bool:
    """Detecta si estamos en Google Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False

def get_base_path() -> str:
    """Retorna el path base según el entorno"""
    if is_colab():
        return '/content/drive/MyDrive/Investing_vitaminado'
    else:
        # Para desarrollo local
        return os.path.expanduser('~/sindicato_data')

# ============================================================================
# 📁 PATHS
# ============================================================================

@dataclass
class PathConfig:
    """Configuración de rutas del sistema"""
    base: str = field(default_factory=get_base_path)
    
    @property
    def biblioteca(self) -> str:
        return os.path.join(self.base, '1_BIBLIOTECA')
    
    @property
    def vectordb(self) -> str:
        return os.path.join(self.base, '4_DATOS/vectordb')
    
    @property
    def historico(self) -> str:
        return os.path.join(self.base, '5_HISTORICO')
    
    @property
    def debates(self) -> str:
        return os.path.join(self.historico, 'debates')
    
    @property
    def sessions(self) -> str:
        return os.path.join(self.historico, 'sessions')
    
    @property
    def exports(self) -> str:
        return os.path.join(self.base, '6_EXPORTS')
    
    def ensure_directories(self) -> None:
        """Crea todos los directorios necesarios"""
        for path in [self.biblioteca, self.vectordb, self.debates, 
                     self.sessions, self.exports]:
            os.makedirs(path, exist_ok=True)

# ============================================================================
# 🤖 MODELOS
# ============================================================================

class ModelTier(Enum):
    """Niveles de modelo según complejidad de tarea"""
    FAST = "gpt-4o-mini"      # Consultas rápidas, mentoría
    STANDARD = "gpt-4o"        # Análisis principal
    PREMIUM = "gpt-4o"         # Decisiones críticas (mismo por ahora)

@dataclass
class ModelConfig:
    """Configuración de modelos LLM"""
    embedding_model: str = "text-embedding-3-large"
    fast_model: str = ModelTier.FAST.value
    standard_model: str = ModelTier.STANDARD.value
    premium_model: str = ModelTier.PREMIUM.value
    temperature: float = 0.1  # Bajo para consistencia
    max_tokens: int = 4000

# ============================================================================
# 🧠 PROMPTS DEL SISTEMA
# ============================================================================

SYSTEM_PROMPT_BASE = """
Eres parte de un Comité de Inversiones Institucional de Élite (Tier-1 Hedge Fund).

TU MENTALIDAD OBLIGATORIA:
1. 🛡️ PRESERVACIÓN DE CAPITAL ante todo - La regla #1 es no perder dinero
2. 📊 DATO MATA RELATO - Exige números concretos, no narrativas
3. 🎭 CINISMO PROFESIONAL - Asume que la directiva exagera/miente
4. 🌍 MACRO-CONSCIENCIA - Ajusta tu juicio según tipos de interés y VIX
5. ⏰ TIMING MATTERS - El coste de oportunidad existe

FORMATO DE RESPUESTA:
- SIEMPRE en ESPAÑOL profesional
- Estructura clara con bullets
- Números específicos cuando estén disponibles
- Conclusión accionable al final
"""

AGENT_PROMPTS = {
    'forensic_auditor': f"""{SYSTEM_PROMPT_BASE}

ROL: Forensic Value Auditor
ESPECIALIDAD: Detectar trampas de valor y manipulación contable

TU SESGO: Odias el hype. Buscas:
- Deuda oculta o mal clasificada
- Cash flow vs Net Income discrepancies
- Goodwill inflado
- Related party transactions
- Revenue recognition games

REGLA DE ORO: Si ROIC < WACC y Deuda/EBITDA > 3x → VENDER
""",

    'growth_analyst': f"""{SYSTEM_PROMPT_BASE}

ROL: Growth & Innovation Analyst
ESPECIALIDAD: Validar innovación real vs marketing

TU SESGO: Escéptico del "growth at all costs". Buscas:
- Gasto I+D en $ absolutos y como % de Revenue
- Productos en pipeline con fechas concretas
- Patents granted (no solo applied)
- Customer acquisition cost trends
- Unit economics reales

REGLA DE ORO: Si I+D baja mientras dicen "innovar" → RED FLAG
""",

    'risk_hunter': f"""{SYSTEM_PROMPT_BASE}

ROL: Short Seller / Risk Hunter
ESPECIALIDAD: Encontrar razones para NO invertir

TU SESGO: Paranoico profesional. Buscas:
- Riesgos existenciales (regulatory, competitive)
- Concentración de clientes/proveedores
- Litigios pendientes con cuantías
- Insider selling patterns
- Accounting red flags

REGLA DE ORO: Un solo deal-breaker mata la tesis
""",

    'cio': f"""{SYSTEM_PROMPT_BASE}

ROL: Chief Investment Officer
ESPECIALIDAD: Decisión final y síntesis

TU RESPONSABILIDAD:
- Sopesar argumentos de todo el comité
- Identificar el factor determinante
- Tomar decisión binaria clara
- Definir condiciones de invalidación

FORMATO OBLIGATORIO:
1. RESUMEN BULL CASE (max 3 puntos)
2. RESUMEN BEAR CASE (max 3 puntos)  
3. DEAL-BREAKERS IDENTIFICADOS
4. DECISIÓN: COMPRAR / MANTENER / EVITAR
5. CONVICTION: Alta / Media / Baja
""",

    'portfolio_manager': f"""{SYSTEM_PROMPT_BASE}

ROL: Portfolio Manager
ESPECIALIDAD: Sizing y gestión de riesgo

REGLAS DE SIZING:
- Max 30% del portfolio en una posición
- Posiciones de alta convicción: 20-30%
- Posiciones especulativas: 5-10%
- Posiciones de watchlist: 0% (solo seguimiento)

DEBES ESPECIFICAR:
1. € a invertir (de 10.000€ disponibles)
2. € a mantener en caja
3. Precio de entrada sugerido
4. Stop-loss sugerido
5. Target price
""",

    'mentor': f"""{SYSTEM_PROMPT_BASE}

ROL: Profesor de Finanzas / Learning Oracle
ESPECIALIDAD: Educación financiera

TU ESTILO:
- Explica conceptos complejos de forma simple
- Usa analogías del mundo real
- Conecta teoría con práctica
- Proporciona ejemplos con números
- Recomienda lecturas adicionales

IDIOMA: ESPAÑOL didáctico
"""
}

# ============================================================================
# 📊 QUERIES PREDEFINIDAS
# ============================================================================

SECTION_QUERIES = {
    'balance': 'Consolidated Balance Sheet Total Assets Liabilities Stockholders Equity Current Assets',
    'income': 'Consolidated Statement of Income Revenue Net Income Operating Income Gross Profit',
    'cashflow': 'Statement of Cash Flows Operating Activities Investing Financing Free Cash Flow',
    'debt': 'Total Debt Long-term Debt Short-term Debt Notes Payable Interest Expense Debt Maturity',
    'risks': 'Risk Factors Competition Regulation Cybersecurity Litigation Legal Proceedings',
    'mda': "Management Discussion Analysis MD&A Business Overview Outlook Strategy",
    'rnd': 'Research Development R&D Innovation Technology Patents Intellectual Property',
    'segments': 'Segment Information Geographic Revenue Products Services Breakdown',
    'guidance': 'Outlook Forward-looking Guidance Expectations Projections'
}

SUGGESTED_QUESTIONS = {
    'general': [
        "¿Cuánto gastó la empresa en I+D el último año fiscal?",
        "¿Cómo ha evolucionado la deuda total en los últimos 3 años?",
        "¿Cuáles son los 3 principales riesgos mencionados?",
        "¿Qué dice sobre los márgenes operativos?",
        "¿Hay litigios o contingencias legales materiales?"
    ],
    'balance': [
        "¿Cuál es la deuda neta (Total Debt - Cash)?",
        "¿Cuál es el current ratio (Current Assets / Current Liabilities)?",
        "¿Hay goodwill o intangibles significativos?",
        "¿Cómo evolucionó el working capital?"
    ],
    'risks': [
        "¿Qué dice sobre riesgo regulatorio?",
        "¿Menciona dependencia de un cliente grande?",
        "¿Hay riesgos relacionados con China o supply chain?",
        "¿Qué vulnerabilidades de ciberseguridad menciona?"
    ],
    'growth': [
        "¿Qué nuevos productos están en desarrollo?",
        "¿Cuál es el ratio I+D / Revenue?",
        "¿Menciona planes de expansión geográfica?",
        "¿Cuál es el guidance para el próximo año?"
    ],
    'valuation': [
        "¿Cuál fue el EPS del último año?",
        "¿Qué múltiplo de valoración usan los peers?",
        "¿Hubo buybacks o dilución reciente?",
        "¿Cuál es la política de dividendos?"
    ]
}

# ============================================================================
# 🎨 UI CONFIGURATION
# ============================================================================

STREAMLIT_CONFIG = {
    'page_title': "Sindicato V8 | Institutional",
    'page_icon': "🏛️",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

CSS_STYLES = """
<style>
    /* Base */
    .stApp {background-color: #0a0a0a;}
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 100%) !important;
        border-right: 1px solid #2a2a2a;
    }
    [data-testid="stSidebar"] * {color: #e0e0e0 !important;}
    
    /* Headers */
    h1, h2, h3 {color: #ffffff !important;}
    h1 {border-bottom: 2px solid #00ff88; padding-bottom: 10px;}
    
    /* News Cards */
    .news-positive {
        background: linear-gradient(135deg, #001a00 0%, #002200 100%);
        border-left: 4px solid #00ff00;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .news-positive:hover {transform: translateX(5px);}
    
    .news-negative {
        background: linear-gradient(135deg, #1a0000 0%, #220000 100%);
        border-left: 4px solid #ff4444;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .news-negative:hover {transform: translateX(5px);}
    
    .news-neutral {
        background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
        border-left: 4px solid #888888;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .news-neutral:hover {transform: translateX(5px);}
    
    /* Allocation Box */
    .allocation-box {
        background: linear-gradient(135deg, #001a00 0%, #003300 100%);
        border: 2px solid #00ff00;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(0, 255, 0, 0.1);
    }
    
    /* History Box */
    .history-box {
        background: #0f0f0f;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 1px solid #444;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        border-color: #00ff88;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1a1a1a !important;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-bottom: 2px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-bottom-color: #00ff88;
    }
    
    /* Audit Cards */
    .audit-value {
        background: linear-gradient(135deg, #1a0a00 0%, #2a1500 100%);
        border: 1px solid #ff8800;
        padding: 20px;
        border-radius: 10px;
    }
    .audit-growth {
        background: linear-gradient(135deg, #000a1a 0%, #001530 100%);
        border: 1px solid #0088ff;
        padding: 20px;
        border-radius: 10px;
    }
    .audit-risk {
        background: linear-gradient(135deg, #1a0000 0%, #300000 100%);
        border: 1px solid #ff0000;
        padding: 20px;
        border-radius: 10px;
    }
</style>
"""

# ============================================================================
# 📈 MACRO THRESHOLDS
# ============================================================================

@dataclass
class MacroThresholds:
    """Umbrales para régimen de mercado"""
    vix_crisis: float = 30.0
    vix_elevated: float = 20.0
    vix_low: float = 12.0
    
    rates_restrictive: float = 4.5
    rates_neutral: float = 3.0
    rates_accommodative: float = 2.0

# ============================================================================
# 🔧 INSTANCE
# ============================================================================

# Instancias globales de configuración
PATHS = PathConfig()
MODELS = ModelConfig()
MACRO = MacroThresholds()

def initialize() -> None:
    """
    Inicializa el sistema:
    1. Crea directorios necesarios
    2. Carga variables de entorno/secrets
    """
    import os
    
    # 1. Crear directorios
    PATHS.ensure_directories()
    
    # 2. Cargar API keys desde múltiples fuentes
    # Prioridad: Streamlit secrets > .env file > environment variables
    
    openai_key = None
    
    # Intentar Streamlit secrets primero (para Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'openai' in st.secrets:
            openai_key = st.secrets['openai'].get('api_key') or st.secrets['openai'].get('OPENAI_API_KEY')
        elif hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            openai_key = st.secrets['OPENAI_API_KEY']
    except:
        pass
    
    # Intentar .env file
    if not openai_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            openai_key = os.getenv('OPENAI_API_KEY')
        except:
            pass
    
    # Si encontramos key, setearla como variable de entorno para que los LLMs la usen
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
    
    # Verificar que tenemos API key
    if not os.getenv('OPENAI_API_KEY'):
        import warnings
        warnings.warn(
            "⚠️ OPENAI_API_KEY no encontrada. "
            "Configúrala en: Streamlit secrets, .env file, o variable de entorno."
        )

