"""
📚 KNOWLEDGE LIBRARY - Biblioteca de Sabiduría
Sistema RAG ampliado para integrar libros de inversión y conocimiento permanente.
Permite que la IA cruce información del 10-K con principios de los grandes inversores.

Características:
- Vectorstore persistente separado del documento activo
- Búsqueda híbrida: documento + biblioteca
- Citas de fuentes (Buffett, Graham, etc.)
"""

import os
import logging
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import streamlit as st

logger = logging.getLogger(__name__)


@dataclass
class BookInfo:
    """Información de un libro indexado."""
    title: str
    author: str
    filename: str
    num_chunks: int
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    topics: List[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Resultado de búsqueda en la biblioteca."""
    content: str
    source: str  # Título del libro
    author: str
    relevance_score: float


class KnowledgeLibrary:
    """
    Biblioteca de conocimiento permanente para inversores.
    
    Gestiona un vectorstore separado del documento activo que contiene:
    - Libros de inversión (Intelligent Investor, Security Analysis, etc.)
    - Cartas de Warren Buffett
    - Artículos y papers académicos
    - Notas personales
    
    La IA puede consultar esta biblioteca para enriquecer el análisis.
    """
    
    def __init__(self, library_path: str = None):
        """
        Args:
            library_path: Ruta donde persistir la biblioteca
        """
        from config import PATHS
        self.library_path = library_path or os.path.join(PATHS.base, 'knowledge_library')
        self.vectorstore_path = os.path.join(self.library_path, 'vectorstore')
        self.metadata_path = os.path.join(self.library_path, 'metadata.json')
        
        os.makedirs(self.library_path, exist_ok=True)
        os.makedirs(self.vectorstore_path, exist_ok=True)
        
        self._vectorstore = None
        self._embeddings = None
        self._books: Dict[str, BookInfo] = {}
        
        self._load_metadata()
    
    @property
    def embeddings(self):
        """Lazy loading de embeddings."""
        if self._embeddings is None:
            try:
                from langchain_openai import OpenAIEmbeddings
                from config import MODELS
                self._embeddings = OpenAIEmbeddings(model=MODELS.embedding_model)
            except Exception as e:
                logger.error(f"Error cargando embeddings: {e}")
        return self._embeddings
    
    @property
    def is_loaded(self) -> bool:
        """Verifica si hay libros en la biblioteca."""
        return len(self._books) > 0 and self._vectorstore is not None
    
    @property
    def book_count(self) -> int:
        """Número de libros indexados."""
        return len(self._books)
    
    @property
    def books(self) -> List[BookInfo]:
        """Lista de libros indexados."""
        return list(self._books.values())
    
    def _load_metadata(self):
        """Carga metadata de libros indexados."""
        import json
        
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for filename, info in data.items():
                        self._books[filename] = BookInfo(**info)
                logger.info(f"Cargados {len(self._books)} libros de metadata")
            except Exception as e:
                logger.error(f"Error cargando metadata: {e}")
        
        # Cargar vectorstore si existe
        self._load_vectorstore()
    
    def _save_metadata(self):
        """Guarda metadata de libros."""
        import json
        
        data = {
            filename: {
                'title': info.title,
                'author': info.author,
                'filename': info.filename,
                'num_chunks': info.num_chunks,
                'indexed_at': info.indexed_at,
                'topics': info.topics
            }
            for filename, info in self._books.items()
        }
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_vectorstore(self):
        """Carga el vectorstore desde disco."""
        if not os.path.exists(os.path.join(self.vectorstore_path, 'index.faiss')):
            return
        
        try:
            from langchain_community.vectorstores import FAISS
            self._vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Vectorstore de biblioteca cargado")
        except Exception as e:
            logger.error(f"Error cargando vectorstore: {e}")
    
    def add_book(
        self,
        file,
        title: str,
        author: str,
        topics: List[str] = None
    ) -> Tuple[int, str]:
        """
        Añade un libro a la biblioteca.
        
        Args:
            file: Archivo subido (PDF, TXT, EPUB)
            title: Título del libro
            author: Autor
            topics: Lista de temas (ej: ['value investing', 'moat'])
            
        Returns:
            Tuple (num_chunks, message)
        """
        import tempfile
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        from langchain.schema import Document
        
        filename = file.name
        topics = topics or []
        
        try:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            
            # Extraer texto
            text = self._extract_text(tmp_path, filename)
            
            if not text or len(text) < 100:
                return 0, "❌ No se pudo extraer texto del archivo."
            
            # Crear chunks con metadata
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " "]
            )
            
            chunks = splitter.split_text(text)
            
            # Crear documentos con metadata rica
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        'source': title,
                        'author': author,
                        'filename': filename,
                        'chunk_index': i,
                        'topics': topics
                    }
                )
                documents.append(doc)
            
            # Añadir a vectorstore
            if self._vectorstore is None:
                self._vectorstore = FAISS.from_documents(
                    documents,
                    self.embeddings
                )
            else:
                self._vectorstore.add_documents(documents)
            
            # Persistir
            self._vectorstore.save_local(self.vectorstore_path)
            
            # Guardar metadata
            self._books[filename] = BookInfo(
                title=title,
                author=author,
                filename=filename,
                num_chunks=len(chunks),
                topics=topics
            )
            self._save_metadata()
            
            # Limpiar temporal
            os.unlink(tmp_path)
            
            logger.info(f"Libro '{title}' añadido con {len(chunks)} chunks")
            return len(chunks), f"✅ '{title}' añadido con {len(chunks)} fragmentos."
            
        except Exception as e:
            logger.error(f"Error añadiendo libro: {e}")
            return 0, f"❌ Error: {str(e)}"
    
    def _extract_text(self, file_path: str, filename: str) -> str:
        """Extrae texto de diferentes formatos."""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext in ['.txt', '.md']:
            return self._extract_txt(file_path)
        elif ext in ['.html', '.htm']:
            return self._extract_html(file_path)
        elif ext == '.epub':
            return self._extract_epub(file_path)
        elif ext == '.mobi':
            return self._extract_mobi(file_path)
        else:
            return self._extract_txt(file_path)
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extrae texto de PDF."""
        try:
            import pdfplumber
            text_parts = []
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extrayendo PDF: {e}")
            return ""
    
    def _extract_txt(self, file_path: str) -> str:
        """Extrae texto de archivo de texto."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error leyendo txt: {e}")
                return ""
    
    def _extract_html(self, file_path: str) -> str:
        """Extrae texto de HTML."""
        try:
            from bs4 import BeautifulSoup
            
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                
                # Eliminar scripts y estilos
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            logger.error(f"Error extrayendo HTML: {e}")
            return ""
    
    def _extract_epub(self, file_path: str) -> str:
        """Extrae texto de EPUB."""
        try:
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            book = epub.read_epub(file_path)
            text_parts = []
            
            for item in book.get_items():
                if item.get_type() == 9:  # ITEM_DOCUMENT (HTML content)
                    content = item.get_content().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text(separator='\n', strip=True)
                    if text:
                        text_parts.append(text)
            
            logger.info(f"EPUB extraído: {len(text_parts)} secciones")
            return "\n\n".join(text_parts)
            
        except ImportError:
            logger.warning("ebooklib no instalado. Instala con: pip install ebooklib")
            return ""
        except Exception as e:
            logger.error(f"Error extrayendo EPUB: {e}")
            return ""
    
    def _extract_mobi(self, file_path: str) -> str:
        """
        Extrae texto de MOBI.
        MOBI es más complejo - intenta convertir a EPUB primero o usar mobi-python.
        """
        try:
            # Intento 1: Usar mobi-python si está disponible
            try:
                import mobi
                tempdir, filepath = mobi.extract(file_path)
                
                # El archivo extraído suele ser HTML
                for root, dirs, files in os.walk(tempdir):
                    for f in files:
                        if f.endswith('.html') or f.endswith('.htm'):
                            html_path = os.path.join(root, f)
                            return self._extract_html(html_path)
                
            except ImportError:
                logger.warning("mobi no instalado. Usando fallback...")
            
            # Intento 2: Leer como binario y extraer texto visible
            with open(file_path, 'rb') as f:
                content = f.read()
                # Buscar texto ASCII/UTF-8 en el binario
                text = content.decode('utf-8', errors='ignore')
                # Limpiar caracteres no imprimibles
                clean_text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')
                return clean_text
                
        except Exception as e:
            logger.error(f"Error extrayendo MOBI: {e}")
            return ""
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_author: str = None,
        filter_topics: List[str] = None
    ) -> List[SearchResult]:
        """
        Busca en la biblioteca de conocimiento.
        
        Args:
            query: Consulta de búsqueda
            k: Número de resultados
            filter_author: Filtrar por autor (opcional)
            filter_topics: Filtrar por temas (opcional)
            
        Returns:
            Lista de SearchResult
        """
        if self._vectorstore is None:
            return []
        
        try:
            # Búsqueda con scores
            results = self._vectorstore.similarity_search_with_score(query, k=k*2)
            
            search_results = []
            for doc, score in results:
                # Aplicar filtros
                if filter_author and doc.metadata.get('author') != filter_author:
                    continue
                
                if filter_topics:
                    doc_topics = doc.metadata.get('topics', [])
                    if not any(t in doc_topics for t in filter_topics):
                        continue
                
                result = SearchResult(
                    content=doc.page_content,
                    source=doc.metadata.get('source', 'Unknown'),
                    author=doc.metadata.get('author', 'Unknown'),
                    relevance_score=1 - score  # Convertir distancia en relevancia
                )
                search_results.append(result)
                
                if len(search_results) >= k:
                    break
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error buscando en biblioteca: {e}")
            return []
    
    def search_with_context(
        self,
        query: str,
        k: int = 3
    ) -> str:
        """
        Busca y formatea resultados para usar como contexto en prompts.
        
        Returns:
            Texto formateado con citas
        """
        results = self.search(query, k=k)
        
        if not results:
            return ""
        
        formatted_parts = []
        for r in results:
            formatted_parts.append(
                f"📖 **{r.source}** ({r.author}):\n\"{r.content[:500]}...\""
            )
        
        return "\n\n---\n\n".join(formatted_parts)
    
    def get_wisdom_for_topic(self, topic: str) -> str:
        """
        Obtiene sabiduría relevante de la biblioteca sobre un tema.
        
        Útil para enriquecer el análisis con perspectivas de grandes inversores.
        
        Args:
            topic: Tema a buscar (ej: 'debt analysis', 'competitive moat')
            
        Returns:
            Contexto formateado
        """
        # Mapeo de temas a queries específicas
        topic_queries = {
            'debt': "análisis de deuda apalancamiento leverage debt",
            'moat': "ventaja competitiva moat economic moat competitive advantage",
            'valuation': "valoración intrinsic value margin of safety",
            'management': "calidad directiva management integrity capital allocation",
            'risk': "riesgo risk management downside protection",
            'growth': "crecimiento growth sustainable profitable growth",
            'dividends': "dividendos dividend policy capital return",
            'cycles': "ciclos económicos economic cycles timing",
        }
        
        query = topic_queries.get(topic.lower(), topic)
        return self.search_with_context(query, k=3)
    
    def remove_book(self, filename: str) -> bool:
        """Elimina un libro de la biblioteca."""
        if filename not in self._books:
            return False
        
        # Por ahora, solo eliminamos de metadata
        # Reconstruir vectorstore sería costoso
        del self._books[filename]
        self._save_metadata()
        
        logger.info(f"Libro {filename} eliminado de metadata")
        return True
    
    def clear_library(self):
        """Limpia toda la biblioteca."""
        import shutil
        
        self._books = {}
        self._vectorstore = None
        
        if os.path.exists(self.vectorstore_path):
            shutil.rmtree(self.vectorstore_path)
            os.makedirs(self.vectorstore_path)
        
        self._save_metadata()
        logger.info("Biblioteca limpiada")


# ============================================================================
# LIBROS PRE-DEFINIDOS (Contenido esencial)
# ============================================================================

BUFFETT_WISDOM = """
## Principios de Warren Buffett

### Sobre Inversión
- "Regla #1: Nunca pierdas dinero. Regla #2: Nunca olvides la regla #1."
- "El riesgo viene de no saber lo que estás haciendo."
- "Precio es lo que pagas, valor es lo que recibes."
- "Es mejor comprar una empresa maravillosa a un precio justo que una empresa justa a un precio maravilloso."

### Sobre Valoración
- "Solo compra algo que estarías feliz de tener si el mercado cerrara 10 años."
- "Si no estás dispuesto a poseer una acción 10 años, no pienses en poseerla 10 minutos."
- "Tiempo es amigo del negocio maravilloso, enemigo del mediocre."

### Sobre Deuda
- "Una empresa realmente buena no necesita pedir prestado."
- "No puedes hacer un buen trato con una mala persona."

### Sobre Moats
- "En negocios, busco castillos económicos protegidos por fosos impenetrables."
- "Una empresa con una fortaleza económica impenetrable, liderada por guerreros capaces y honrados."

### Sobre Timing
- "El mercado de valores es un dispositivo para transferir dinero del impaciente al paciente."
- "Sé temeroso cuando otros sean codiciosos, y codicioso cuando otros sean temerosos."
"""

MUNGER_WISDOM = """
## Principios de Charlie Munger

### Sobre Inversión
- "Invierte en un negocio que cualquier idiota pueda dirigir, porque algún día un idiota lo dirigirá."
- "Todo lo que quiero saber es dónde voy a morir, para no ir nunca ahí."
- "La inversión no se trata de vencer a otros. Se trata de controlarte a ti mismo."

### Sobre Análisis
- "Invierta el problema, siempre invierta."
- "Nunca confíes en un modelo."
- "Consigue la información contable de cualquier empresa que analices."

### Sobre Errores
- "Un coeficiente intelectual de 160 no te sirve si actúas con el temperamento de uno de 100."
- "No envidies lo que otros hacen. Encuentra lo que funciona para ti."

### Sobre Paciencia
- "El dinero grande no está en el comprar o el vender, sino en el esperar."
- "No tenemos sistema de 20 ideas de inversión. Buena suerte si alguna vez tenemos 3."
"""

GRAHAM_WISDOM = """
## Principios de Benjamin Graham

### Sobre Margen de Seguridad
- "El margen de seguridad siempre depende del precio pagado."
- "Las operaciones de inversión son aquellas que, tras análisis completo, prometen seguridad del principal y un retorno adecuado."
- "La esencia de la inversión en valor es comprar con descuento significativo sobre el valor intrínseco."

### Sobre Mr. Market
- "El mercado es un péndulo que oscila constantemente entre optimismo insostenible y pesimismo injustificado."
- "El inversor inteligente es realista que vende a optimistas y compra a pesimistas."

### Sobre Análisis
- "No seas un especulador disfrazado de inversor."
- "La función de un análisis de seguridad es descubrir si el precio es satisfactorio."

### Sobre Diversificación
- "La mejor protección contra la ignorancia es la diversificación."
"""


def add_essential_wisdom(library: KnowledgeLibrary):
    """Añade sabiduría esencial pre-definida a la biblioteca."""
    import tempfile
    
    wisdom_books = [
        ("Warren Buffett - Principios", "Warren Buffett", BUFFETT_WISDOM, ['value investing', 'moat', 'patience']),
        ("Charlie Munger - Principios", "Charlie Munger", MUNGER_WISDOM, ['mental models', 'analysis', 'patience']),
        ("Benjamin Graham - Principios", "Benjamin Graham", GRAHAM_WISDOM, ['value investing', 'margin of safety', 'analysis']),
    ]
    
    for title, author, content, topics in wisdom_books:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            tmp_path = f.name
        
        # Simular file upload
        class FakeFile:
            def __init__(self, path, name):
                self._path = path
                self.name = name
            def read(self):
                with open(self._path, 'rb') as f:
                    return f.read()
        
        fake_file = FakeFile(tmp_path, f"{title}.txt")
        library.add_book(fake_file, title, author, topics)
        
        os.unlink(tmp_path)
    
    return len(wisdom_books)
