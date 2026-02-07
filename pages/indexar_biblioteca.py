"""
🚀 INDEXADOR DE BIBLIOTECA - Ejecutar desde Streamlit
Página temporal para indexar la biblioteca
"""

import streamlit as st
import os
from services import KnowledgeLibrary

st.set_page_config(page_title="Indexador de Biblioteca", page_icon="📚")

st.title("📚 Indexador de Biblioteca")
st.caption("Indexa todos los libros de la carpeta 1_BIBLIOTECA")

folder = "1_BIBLIOTECA"

if not os.path.exists(folder):
    st.error(f"❌ No existe la carpeta: {folder}")
    st.stop()

# Contar archivos
supported = ['.pdf', '.epub', '.mobi', '.txt', '.md', '.html', '.htm']
books = []
for root, dirs, files in os.walk(folder):
    for file in files:
        if any(file.lower().endswith(ext) for ext in supported):
            books.append(os.path.join(root, file))

st.info(f"📁 Encontrados **{len(books)} archivos** en `{folder}`")

# Mostrar algunos ejemplos
with st.expander("👀 Ver archivos encontrados"):
    for book in books[:20]:
        st.text(f"- {os.path.basename(book)}")
    if len(books) > 20:
        st.text(f"... y {len(books) - 20} más")

st.markdown("---")

if st.button("🚀 INDEXAR TODOS LOS LIBROS", type="primary"):
    lib = KnowledgeLibrary()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    indexed = 0
    errors = 0
    
    for i, path in enumerate(books):
        filename = os.path.basename(path)
        status_text.text(f"[{i+1}/{len(books)}] {filename[:50]}...")
        progress_bar.progress((i + 1) / len(books))
        
        # Extraer título/autor
        name = os.path.splitext(filename)[0]
        
        # Casos especiales
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
        
        # Simular upload
        class FakeFile:
            def __init__(self, p):
                self._path = p
                self.name = os.path.basename(p)
            def read(self):
                with open(self._path, 'rb') as f:
                    return f.read()
        
        try:
            fake = FakeFile(path)
            n, msg = lib.add_book(fake, title, author, topics)
            
            if n > 0:
                indexed += 1
            else:
                errors += 1
        except Exception as e:
            st.warning(f"⚠️ Error en {filename}: {str(e)[:100]}")
            errors += 1
    
    progress_bar.progress(1.0)
    status_text.empty()
    
    st.success(f"🎉 **Indexación completada!**")
    st.metric("✅ Indexados", f"{indexed}/{len(books)}")
    st.metric("❌ Errores", errors)
    st.metric("📊 Total en biblioteca", lib.book_count)
    
    st.markdown("---")
    st.subheader("📚 Libros en la biblioteca:")
    
    for book in lib.books:
        st.text(f"- {book.title} ({book.author}) - {book.num_chunks} chunks")

st.markdown("---")
st.caption("💡 Después de indexar, puedes cerrar esta página y usar la app normalmente")
