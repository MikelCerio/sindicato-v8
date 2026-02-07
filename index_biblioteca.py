"""
📚 INDEXADOR STANDALONE - Sin dependencias de Streamlit
Ejecuta directamente con Python
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Configurar paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_PATH = os.path.join(BASE_DIR, 'knowledge_library')
VECTORSTORE_PATH = os.path.join(LIBRARY_PATH, 'vectorstore')
METADATA_PATH = os.path.join(LIBRARY_PATH, 'metadata.json')

# Crear directorios
os.makedirs(LIBRARY_PATH, exist_ok=True)
os.makedirs(VECTORSTORE_PATH, exist_ok=True)

print("="*70)
print("📚 INDEXADOR DE BIBLIOTECA - Sindicato V8")
print("="*70)
print()

# Importar dependencias necesarias
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    import pdfplumber
    from bs4 import BeautifulSoup
    print("✅ Dependencias cargadas correctamente")
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("\nInstala las dependencias:")
    print("  pip install langchain langchain-openai langchain-community faiss-cpu pdfplumber beautifulsoup4")
    sys.exit(1)

# Verificar API Key
if not os.getenv('OPENAI_API_KEY'):
    print("❌ OPENAI_API_KEY no configurada")
    print("\nConfigura tu API key:")
    print("  set OPENAI_API_KEY=tu-api-key")
    sys.exit(1)

print("✅ OPENAI_API_KEY configurada")
print()

# Buscar archivos
folder = "1_BIBLIOTECA"
if not os.path.exists(folder):
    print(f"❌ No existe la carpeta: {folder}")
    sys.exit(1)

supported = ['.pdf', '.epub', '.mobi', '.txt', '.md', '.html', '.htm']
books = []

for root, dirs, files in os.walk(folder):
    for file in files:
        if any(file.lower().endswith(ext) for ext in supported):
            books.append(os.path.join(root, file))

print(f"📁 Carpeta: {folder}")
print(f"📚 Archivos encontrados: {len(books)}")
print()

if not books:
    print("⚠️ No se encontraron archivos")
    sys.exit(0)

# Funciones de extracción
def extract_pdf(file_path):
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"   ⚠️ Error PDF: {e}")
        return ""

def extract_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"   ⚠️ Error HTML: {e}")
        return ""

def extract_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"   ⚠️ Error TXT: {e}")
            return ""

def extract_epub(file_path):
    try:
        from ebooklib import epub
        book = epub.read_epub(file_path)
        text_parts = []
        for item in book.get_items():
            if item.get_type() == 9:
                content = item.get_content().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                if text:
                    text_parts.append(text)
        return "\n\n".join(text_parts)
    except ImportError:
        print("   ⚠️ ebooklib no instalado (pip install ebooklib)")
        return ""
    except Exception as e:
        print(f"   ⚠️ Error EPUB: {e}")
        return ""

def extract_text(file_path, filename):
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.pdf':
        return extract_pdf(file_path)
    elif ext in ['.html', '.htm']:
        return extract_html(file_path)
    elif ext == '.epub':
        return extract_epub(file_path)
    elif ext in ['.txt', '.md']:
        return extract_txt(file_path)
    else:
        return extract_txt(file_path)

# Inicializar embeddings y vectorstore
print("🔧 Inicializando embeddings...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Cargar vectorstore existente si existe
vectorstore = None
if os.path.exists(os.path.join(VECTORSTORE_PATH, 'index.faiss')):
    try:
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Vectorstore existente cargado")
    except:
        print("⚠️ No se pudo cargar vectorstore existente, creando uno nuevo")

# Cargar metadata existente
metadata_dict = {}
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata_dict = json.load(f)
    print(f"✅ Metadata cargada ({len(metadata_dict)} libros previos)")

print()
print("="*70)
print("🚀 INICIANDO INDEXACIÓN")
print("="*70)
print()

# Indexar
indexed = 0
errors = 0
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " "]
)

for i, path in enumerate(books, 1):
    filename = os.path.basename(path)
    print(f"[{i}/{len(books)}] {filename[:60]}")
    
    # Extraer título/autor
    name = os.path.splitext(filename)[0]
    
    if "Carta_Buffett" in filename:
        year = filename.split("_")[-1].split(".")[0]
        author = "Warren Buffett"
        title = f"Carta a los Accionistas {year}"
        topics = ['value investing', 'buffett', 'annual letters']
    
    elif "Z-Library" in filename:
        parts = name.replace(" (Z-Library)", "").split(" (")
        title = parts[0].strip()
        author = parts[1].strip("_)") if len(parts) > 1 else "Unknown"
        topics = ['value investing', 'investment books']
    
    elif any(x in filename.lower() for x in ['tsla', 'intc', 'pypl', '10-k', 'f-2024']):
        ticker = filename.split("-")[0].upper()
        author = f"{ticker} Inc."
        title = f"10-K Filing {ticker}"
        topics = ['sec filings', '10-k']
    
    else:
        author = "Unknown"
        title = name
        topics = ['general']
    
    try:
        # Extraer texto
        text = extract_text(path, filename)
        
        if not text or len(text) < 100:
            print(f"   ⚠️ Texto insuficiente")
            errors += 1
            continue
        
        # Crear chunks
        chunks = splitter.split_text(text)
        
        # Crear documentos
        documents = []
        for idx, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    'source': title,
                    'author': author,
                    'filename': filename,
                    'chunk_index': idx,
                    'topics': topics
                }
            )
            documents.append(doc)
        
        # Añadir a vectorstore
        if vectorstore is None:
            vectorstore = FAISS.from_documents(documents, embeddings)
        else:
            vectorstore.add_documents(documents)
        
        # Guardar metadata
        metadata_dict[filename] = {
            'title': title,
            'author': author,
            'filename': filename,
            'num_chunks': len(chunks),
            'indexed_at': datetime.now().isoformat(),
            'topics': topics
        }
        
        print(f"   ✅ {len(chunks)} chunks")
        indexed += 1
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:80]}")
        errors += 1

print()
print("="*70)
print("💾 GUARDANDO DATOS...")
print("="*70)

# Guardar vectorstore
if vectorstore:
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"✅ Vectorstore guardado en: {VECTORSTORE_PATH}")

# Guardar metadata
with open(METADATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
print(f"✅ Metadata guardada en: {METADATA_PATH}")

print()
print("="*70)
print("🎉 INDEXACIÓN COMPLETADA")
print("="*70)
print(f"✅ Indexados: {indexed}/{len(books)}")
print(f"❌ Errores: {errors}")
print(f"📊 Total en biblioteca: {len(metadata_dict)}")
print()
print("💡 Los libros están listos para usar en la app")
print("="*70)
