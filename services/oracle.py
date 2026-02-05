"""
🧠 ORÁCULO V8 - Sistema RAG Mejorado
Features:
- Caché de búsquedas
- Logging estructurado
- Detección de estructura de documentos
- Extracción inteligente de tablas
"""

import os
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document
import pdfplumber
from bs4 import BeautifulSoup

from config import PATHS, MODELS, SECTION_QUERIES

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentStructure:
    """Estructura detectada de un documento 10-K/10-Q"""
    filename: str
    processed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    has_balance_sheet: bool = False
    has_income_statement: bool = False
    has_cash_flow: bool = False
    has_risk_factors: bool = False
    has_mda: bool = False
    has_segments: bool = False
    num_tables: int = 0
    num_chunks: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'filename': self.filename,
            'processed_at': self.processed_at,
            'sections': {
                'balance_sheet': self.has_balance_sheet,
                'income_statement': self.has_income_statement,
                'cash_flow': self.has_cash_flow,
                'risk_factors': self.has_risk_factors,
                'mda': self.has_mda,
                'segments': self.has_segments
            },
            'stats': {
                'tables': self.num_tables,
                'chunks': self.num_chunks
            }
        }


class OraculoV8:
    """
    Sistema RAG institucional para análisis de documentos financieros.
    
    Mejoras sobre V7:
    - Caché de embeddings y búsquedas
    - Logging estructurado
    - Mejor extracción de tablas
    - Detección automática de secciones
    - Type hints completos
    """
    
    def __init__(self):
        """Inicializa el Oráculo con configuración desde config.py"""
        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._vectorstore: Optional[FAISS] = None
        self._search_cache: Dict[str, str] = {}
        self._current_structure: Optional[DocumentStructure] = None
        
        # Asegurar directorios
        PATHS.ensure_directories()
        
        # Cargar vectorstore existente
        self._load_vectorstore()
        
        logger.info("OraculoV8 inicializado correctamente")
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """Lazy loading de embeddings"""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=MODELS.embedding_model
            )
        return self._embeddings
    
    @property
    def is_loaded(self) -> bool:
        """Verifica si hay datos cargados"""
        return self._vectorstore is not None
    
    @property
    def structure(self) -> Optional[DocumentStructure]:
        """Retorna la estructura del documento actual"""
        return self._current_structure
    
    def _load_vectorstore(self) -> None:
        """Carga el vectorstore desde disco si existe"""
        index_path = os.path.join(PATHS.vectordb, "index.faiss")
        
        if os.path.exists(index_path):
            try:
                self._vectorstore = FAISS.load_local(
                    PATHS.vectordb,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Vectorstore cargado desde {PATHS.vectordb}")
            except Exception as e:
                logger.error(f"Error cargando vectorstore: {e}")
                self._vectorstore = None
    
    def ingest(self, uploaded_file) -> Tuple[int, DocumentStructure]:
        """
        Ingesta un documento y lo indexa en el vectorstore.
        
        Args:
            uploaded_file: Archivo subido via Streamlit
            
        Returns:
            Tuple con (número de chunks, estructura del documento)
        """
        filename = uploaded_file.name
        file_path = os.path.join(PATHS.biblioteca, filename)
        
        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"Procesando documento: {filename}")
        
        # Extraer contenido según tipo
        text, tables_text, structure = self._extract_content(file_path)
        
        # Combinar texto
        full_text = text
        if tables_text:
            full_text += "\n\n=== FINANCIAL TABLES ===\n\n" + tables_text
        
        # Chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_text(full_text)
        
        # Crear documentos con metadata
        docs = [
            Document(
                page_content=chunk,
                metadata={
                    'source': filename,
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'indexed_at': datetime.now().isoformat()
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # Crear/actualizar vectorstore
        self._vectorstore = FAISS.from_documents(docs, self.embeddings)
        self._vectorstore.save_local(PATHS.vectordb)
        
        # Actualizar estructura
        structure.num_chunks = len(chunks)
        self._current_structure = structure
        
        # Limpiar caché de búsquedas
        self._search_cache.clear()
        
        logger.info(f"Documento indexado: {len(chunks)} chunks")
        
        return len(chunks), structure
    
    def _extract_content(self, file_path: str) -> Tuple[str, str, DocumentStructure]:
        """
        Extrae contenido de un archivo.
        
        Returns:
            Tuple con (texto principal, texto de tablas, estructura)
        """
        filename = os.path.basename(file_path)
        structure = DocumentStructure(filename=filename)
        text = ""
        tables_text = ""
        
        try:
            if file_path.endswith('.pdf'):
                text, tables_text, structure = self._extract_pdf(file_path, structure)
            elif file_path.endswith('.html') or file_path.endswith('.htm'):
                text, tables_text, structure = self._extract_html(file_path, structure)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
        except Exception as e:
            logger.error(f"Error extrayendo contenido: {e}")
            text = f"Error procesando archivo: {str(e)}"
        
        return text, tables_text, structure
    
    def _extract_pdf(self, file_path: str, structure: DocumentStructure) -> Tuple[str, str, DocumentStructure]:
        """Extrae contenido de PDF"""
        text_parts = []
        tables_text = ""
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Texto
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                
                # Tablas
                tables = page.extract_tables()
                for table in tables:
                    structure.num_tables += 1
                    tables_text += f"\n--- Table ---\n"
                    for row in table:
                        if row:
                            tables_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
        
        text = "\n".join(text_parts)
        structure = self._detect_sections(text, structure)
        
        return text, tables_text, structure
    
    def _extract_html(self, file_path: str, structure: DocumentStructure) -> Tuple[str, str, DocumentStructure]:
        """Extrae contenido de HTML (típico 10-K de SEC)"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Extraer tablas primero
        tables_text = ""
        for idx, table in enumerate(soup.find_all('table')):
            structure.num_tables += 1
            tables_text += f"\n--- Table {idx + 1} ---\n"
            
            for row in table.find_all('tr'):
                cols = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if any(cols):  # Solo filas con contenido
                    tables_text += " | ".join(cols) + "\n"
        
        # Texto principal
        text = soup.get_text(separator='\n')
        
        # Detectar secciones
        structure = self._detect_sections(text, structure)
        
        return text, tables_text, structure
    
    def _detect_sections(self, text: str, structure: DocumentStructure) -> DocumentStructure:
        """Detecta secciones comunes en documentos financieros"""
        text_lower = text.lower()
        
        section_patterns = {
            'has_balance_sheet': ['consolidated balance sheet', 'balance sheets'],
            'has_income_statement': ['statement of income', 'statements of operations', 'income statement'],
            'has_cash_flow': ['cash flow', 'statements of cash'],
            'has_risk_factors': ['risk factor', 'item 1a'],
            'has_mda': ["management's discussion", 'md&a', 'item 7'],
            'has_segments': ['segment information', 'reportable segment']
        }
        
        for attr, patterns in section_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                setattr(structure, attr, True)
        
        return structure
    
    @st.cache_data(ttl=300, show_spinner=False)
    def search(_self, query: str, k: int = 5) -> str:
        """
        Búsqueda semántica en el vectorstore.
        
        Args:
            query: Consulta de búsqueda
            k: Número de resultados
            
        Returns:
            Texto concatenado de los resultados
        """
        if not _self._vectorstore:
            return "⚠️ No hay documentos cargados en el Oráculo. Sube un 10-K primero."
        
        # Verificar caché
        cache_key = f"{query}_{k}"
        if cache_key in _self._search_cache:
            return _self._search_cache[cache_key]
        
        try:
            docs = _self._vectorstore.similarity_search(query, k=k)
            result = "\n\n---\n\n".join([doc.page_content for doc in docs])
            
            # Guardar en caché
            _self._search_cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return f"Error en búsqueda: {str(e)}"
    
    def search_section(self, section_type: str) -> str:
        """
        Búsqueda dirigida por tipo de sección.
        
        Args:
            section_type: Tipo de sección (balance, income, cashflow, etc.)
            
        Returns:
            Texto de la sección encontrada
        """
        query = SECTION_QUERIES.get(section_type, section_type)
        return self.search(query, k=5)
    
    def get_financial_context(self) -> Dict[str, str]:
        """
        Obtiene contexto financiero completo para el comité.
        
        Returns:
            Dict con contexto de value, growth y risk
        """
        return {
            'value': self.search_section('balance') + "\n\n" + self.search_section('debt'),
            'growth': self.search_section('rnd') + "\n\n" + self.search_section('mda'),
            'risk': self.search_section('risks')
        }
    
    def clear_cache(self) -> None:
        """Limpia el caché de búsquedas"""
        self._search_cache.clear()
        # También limpiar caché de Streamlit si existe
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
