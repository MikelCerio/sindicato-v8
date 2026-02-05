"""
📄 SEC FILINGS ANALYZER - Análisis de 10-K y 10-Q
Inspirado en FinRobot: Extracción automática de insights de SEC filings.

Features:
- Descarga directa desde SEC EDGAR
- Extracción de secciones clave (MD&A, Risk Factors, Financials)
- Resumen ejecutivo con LLM
- Detector de Red Flags
- Comparación YoY
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as st

logger = logging.getLogger(__name__)

# SEC EDGAR Base URLs
SEC_EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
SEC_EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_EDGAR_FILING = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filename}"

# Headers requeridos por SEC
SEC_HEADERS = {
    "User-Agent": "SindicatoV8 Educational Research Bot contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}


@dataclass
class SECFiling:
    """Representa un filing de SEC."""
    ticker: str
    cik: str
    form_type: str  # 10-K, 10-Q, 8-K
    filing_date: str
    accession_number: str
    primary_document: str
    
    # Contenido extraído
    raw_html: str = ""
    
    # Secciones parseadas
    business_description: str = ""
    risk_factors: str = ""
    md_and_a: str = ""  # Management Discussion & Analysis
    financial_statements: str = ""
    
    # Métricas extraídas
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Análisis LLM
    executive_summary: str = ""
    red_flags: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)


class SECAnalyzer:
    """
    Analizador de SEC Filings.
    
    Funcionalidades:
    - Buscar y descargar 10-K/10-Q
    - Parsear secciones relevantes
    - Generar resúmenes con LLM
    - Detectar red flags
    """
    
    def __init__(self):
        self._cik_cache: Dict[str, str] = {}
        self._session = requests.Session()
        self._session.headers.update(SEC_HEADERS)
    
    # =========================================================================
    # BÚSQUEDA Y DESCARGA
    # =========================================================================
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """Obtiene el CIK (Central Index Key) de un ticker."""
        if ticker in self._cik_cache:
            return self._cik_cache[ticker]
        
        try:
            # Usar el mapping oficial de SEC
            mapping_url = "https://www.sec.gov/files/company_tickers.json"
            response = self._session.get(mapping_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for entry in data.values():
                    if entry.get("ticker", "").upper() == ticker.upper():
                        cik = str(entry.get("cik_str", "")).zfill(10)
                        self._cik_cache[ticker] = cik
                        return cik
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo CIK para {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_recent_filings(_self, ticker: str, form_types: List[str] = None) -> List[Dict]:
        """
        Obtiene los filings recientes de una empresa.
        
        Args:
            ticker: Símbolo de la empresa
            form_types: Lista de tipos (ej: ['10-K', '10-Q', '8-K'])
        
        Returns:
            Lista de filings con metadatos
        """
        if form_types is None:
            form_types = ["10-K", "10-Q"]
        
        cik = _self.get_cik(ticker)
        if not cik:
            logger.error(f"No se encontró CIK para {ticker}")
            return []
        
        try:
            # Obtener submissions
            url = SEC_EDGAR_SUBMISSIONS.format(cik=cik.lstrip('0'))
            response = _self._session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            filings = []
            
            # Parsear filings recientes
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])
            documents = recent.get("primaryDocument", [])
            
            for i, form in enumerate(forms):
                if form in form_types:
                    filings.append({
                        "form_type": form,
                        "filing_date": dates[i] if i < len(dates) else "",
                        "accession_number": accessions[i].replace("-", "") if i < len(accessions) else "",
                        "primary_document": documents[i] if i < len(documents) else "",
                        "ticker": ticker.upper(),
                        "cik": cik
                    })
                
                # Limitar a 10 filings
                if len(filings) >= 10:
                    break
            
            return filings
            
        except Exception as e:
            logger.error(f"Error obteniendo filings de {ticker}: {e}")
            return []
    
    def download_filing(self, filing_info: Dict) -> Optional[SECFiling]:
        """
        Descarga y parsea un filing completo.
        
        Args:
            filing_info: Dict con metadatos del filing
        
        Returns:
            SECFiling con contenido parseado
        """
        try:
            cik = filing_info["cik"].lstrip('0')
            accession = filing_info["accession_number"]
            document = filing_info["primary_document"]
            
            # Construir URL
            url = SEC_EDGAR_FILING.format(
                cik=cik,
                accession=accession,
                filename=document
            )
            
            logger.info(f"Descargando filing: {url}")
            response = self._session.get(url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Error descargando filing: {response.status_code}")
                return None
            
            # Crear objeto Filing
            filing = SECFiling(
                ticker=filing_info["ticker"],
                cik=filing_info["cik"],
                form_type=filing_info["form_type"],
                filing_date=filing_info["filing_date"],
                accession_number=accession,
                primary_document=document,
                raw_html=response.text
            )
            
            # Parsear secciones
            self._parse_sections(filing)
            
            return filing
            
        except Exception as e:
            logger.error(f"Error descargando filing: {e}")
            return None
    
    # =========================================================================
    # PARSING DE SECCIONES
    # =========================================================================
    
    def _parse_sections(self, filing: SECFiling) -> None:
        """Extrae las secciones principales del filing."""
        soup = BeautifulSoup(filing.raw_html, 'html.parser')
        
        # Limpiar scripts y styles
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        
        # Patrones para secciones de 10-K
        section_patterns = {
            'business_description': [
                r'ITEM\s*1[.\s]*BUSINESS(.*?)ITEM\s*1A',
                r'Item\s*1[.\s]*Business(.*?)Item\s*1A',
            ],
            'risk_factors': [
                r'ITEM\s*1A[.\s]*RISK\s*FACTORS?(.*?)ITEM\s*1B',
                r'Item\s*1A[.\s]*Risk\s*Factors?(.*?)Item\s*1B',
                r'ITEM\s*1A[.\s]*RISK\s*FACTORS?(.*?)ITEM\s*2',
            ],
            'md_and_a': [
                r'ITEM\s*7[.\s]*MANAGEMENT.{0,50}DISCUSSION(.*?)ITEM\s*7A',
                r'Item\s*7[.\s]*Management.{0,50}Discussion(.*?)Item\s*7A',
                r'ITEM\s*7[.\s]*MANAGEMENT.{0,50}DISCUSSION(.*?)ITEM\s*8',
            ],
            'financial_statements': [
                r'ITEM\s*8[.\s]*FINANCIAL\s*STATEMENTS(.*?)ITEM\s*9',
                r'Item\s*8[.\s]*Financial\s*Statements(.*?)Item\s*9',
            ]
        }
        
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    # Limitar tamaño para LLM
                    if len(content) > 50000:
                        content = content[:50000] + "...[truncated]"
                    setattr(filing, section_name, content)
                    break
    
    def _extract_text_clean(self, html: str, max_length: int = 50000) -> str:
        """Extrae texto limpio del HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Eliminar tags no deseados
        for tag in soup(['script', 'style', 'table']):
            tag.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    # =========================================================================
    # ANÁLISIS CON LLM
    # =========================================================================
    
    def analyze_filing(self, filing: SECFiling) -> SECFiling:
        """
        Analiza el filing con LLM para generar insights.
        
        Genera:
        - Resumen ejecutivo
        - Red flags detectados
        - Key insights
        """
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            
            # Preparar contexto
            context_parts = []
            
            if filing.business_description:
                context_parts.append(f"## Business Description:\n{filing.business_description[:5000]}")
            
            if filing.risk_factors:
                context_parts.append(f"## Risk Factors:\n{filing.risk_factors[:10000]}")
            
            if filing.md_and_a:
                context_parts.append(f"## Management Discussion & Analysis:\n{filing.md_and_a[:10000]}")
            
            context = "\n\n".join(context_parts)
            
            if not context:
                context = self._extract_text_clean(filing.raw_html, 20000)
            
            # Prompt de análisis
            system_prompt = """Eres un analista financiero senior especializado en análisis de SEC filings.
Tu trabajo es extraer los insights más importantes para un inversor que está considerando invertir en esta empresa.

REGLAS:
1. Sé ESPECÍFICO - cita números y datos concretos
2. Sé CRÍTICO - no repitas lo que dice la directiva, analízalo
3. Busca RED FLAGS activamente
4. Piensa como un inversor escéptico pero justo

FORMATO DE RESPUESTA (usa exactamente estos headers):

### 📋 RESUMEN EJECUTIVO
[3-5 frases con lo más importante]

### 🔴 RED FLAGS DETECTADOS
[Lista de señales de alarma, si las hay. Si no hay, indicar "Sin red flags significativos detectados"]

### 💡 INSIGHTS CLAVE
[5-7 puntos con los insights más valiosos para un inversor]

### 📊 MÉTRICAS MENCIONADAS
[Lista de números y métricas importantes mencionadas en el documento]

### ⚖️ BULL vs BEAR
**Bull Case:** [Por qué podría ser buena inversión]
**Bear Case:** [Por qué podría ser mala inversión]
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Analiza este {filing.form_type} de {filing.ticker} (fecha: {filing.filing_date}):\n\n{context}")
            ]
            
            response = llm.invoke(messages)
            analysis_text = response.content
            
            # Parsear respuesta
            filing.executive_summary = self._extract_section(analysis_text, "RESUMEN EJECUTIVO")
            filing.red_flags = self._extract_list(analysis_text, "RED FLAGS DETECTADOS")
            filing.key_insights = self._extract_list(analysis_text, "INSIGHTS CLAVE")
            
            # Guardar análisis completo en métricas
            filing.metrics["full_analysis"] = analysis_text
            filing.metrics["bull_case"] = self._extract_section(analysis_text, "Bull Case:")
            filing.metrics["bear_case"] = self._extract_section(analysis_text, "Bear Case:")
            
            return filing
            
        except Exception as e:
            logger.error(f"Error en análisis LLM: {e}")
            filing.executive_summary = f"Error en análisis: {str(e)}"
            return filing
    
    def _extract_section(self, text: str, header: str) -> str:
        """Extrae una sección del texto por su header."""
        pattern = rf'{re.escape(header)}[:\s]*(.*?)(?=###|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_list(self, text: str, header: str) -> List[str]:
        """Extrae una lista de items de una sección."""
        section = self._extract_section(text, header)
        if not section:
            return []
        
        # Buscar items con bullets o números
        items = re.findall(r'[-•*\d.]\s*(.+?)(?=\n[-•*\d.]|\Z)', section, re.DOTALL)
        return [item.strip() for item in items if item.strip()]
    
    # =========================================================================
    # COMPARACIÓN YoY
    # =========================================================================
    
    def compare_filings(self, current: SECFiling, previous: SECFiling) -> Dict[str, Any]:
        """
        Compara dos filings (típicamente YoY) para detectar cambios.
        
        Returns:
            Dict con cambios detectados
        """
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            
            # Comparar Risk Factors
            current_risks = current.risk_factors[:5000] if current.risk_factors else "No disponible"
            previous_risks = previous.risk_factors[:5000] if previous.risk_factors else "No disponible"
            
            prompt = f"""Compara los Risk Factors de estos dos {current.form_type}:

## {current.filing_date} (ACTUAL):
{current_risks}

## {previous.filing_date} (ANTERIOR):
{previous_risks}

IDENTIFICA:
1. NUEVOS riesgos añadidos (que no estaban antes)
2. Riesgos ELIMINADOS (que ya no mencionan)
3. Riesgos que han CAMBIADO en severidad o descripción

Responde en formato estructurado y sé específico."""

            response = llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "risk_comparison": response.content,
                "current_date": current.filing_date,
                "previous_date": previous.filing_date,
            }
            
        except Exception as e:
            logger.error(f"Error comparando filings: {e}")
            return {"error": str(e)}


# =============================================================================
# UTILIDADES PARA UI
# =============================================================================

def format_filing_date(date_str: str) -> str:
    """Formatea la fecha del filing."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%d %b %Y")
    except:
        return date_str


def get_filing_icon(form_type: str) -> str:
    """Devuelve icono según tipo de filing."""
    icons = {
        "10-K": "📊",
        "10-Q": "📈",
        "8-K": "⚡",
        "DEF 14A": "📋",
    }
    return icons.get(form_type, "📄")
