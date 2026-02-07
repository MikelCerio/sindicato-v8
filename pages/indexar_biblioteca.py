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
    error_details = []
    
    for i, path in enumerate(books):
        filename = os.path.basename(path)
        status = f"[{i+1}/{len(books)}] Procesando: {filename[:40]}..."
        status_text.text(status)
        progress_bar.progress((i + 1) / len(books))
        
        # [Simular Upload y lógica de metadatos igual...]
        
        # Extraer título/autor (simplificado para ahorrar espacio en diff, mantengo lógica original)
        name = os.path.splitext(filename)[0]
        
        if "Carta_Buffett" in filename:
            author = "Warren Buffett"
            title = f"Carta a los Accionistas {filename.split('_')[-1].split('.')[0]}"
            topics = ['value investing', 'buffett']
        elif "Z-Library" in filename:
            parts = name.replace(" (Z-Library)", "").split(" (")
            title = parts[0].strip()
            author = parts[1].strip("_)") if len(parts) > 1 else "Unknown"
            topics = ['value investing']
        elif any(x in filename.lower() for x in ['tsla', 'intc', 'pypl', '10-k']):
            ticker = filename.split("-")[0].upper()
            author = f"{ticker} Inc."
            title = f"10-K {ticker}"
            topics = ['sec filings']
        else:
            author = "Unknown"
            title = name
            topics = ['general']
        
        class FakeFile:
            def __init__(self, p):
                self._path = p
                self.name = os.path.basename(p)
            def read(self):
                with open(self._path, 'rb') as f:
                    return f.read()
        
        try:
            fake = FakeFile(path)
            # Llamada real
            n, msg = lib.add_book(fake, title, author, topics)
            
            if n > 0:
                indexed += 1
            else:
                errors += 1
                error_details.append(f"❌ {filename}: {msg}")
                
        except Exception as e:
            err_msg = str(e)[:100]
            # st.warning comentada para no ensuciar la UI mientras corre
            errors += 1
            error_details.append(f"⚠️ {filename}: {err_msg}")
    
    progress_bar.progress(1.0)
    status_text.text("✅ Proceso completado")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Indexados", f"{indexed}/{len(books)}")
    col2.metric("❌ Errores", errors)
    col3.metric("📊 Total Biblioteca", lib.book_count)
    
    if error_details:
        st.error(f"Hubo {len(error_details)} errores. Revisa los detalles abajo:")
        with st.expander("❌ Ver Detalle de Errores (Archivos fallidos)", expanded=True):
            for err in error_details:
                st.write(err)
    else:
        st.balloons()
        st.success("🎉 ¡Indexación perfecta! Todos los libros procesados correctamente.")
    
    st.markdown("---")
    st.subheader("📚 Libros en la biblioteca:")
    
    for book in lib.books:
        st.text(f"- {book.title} ({book.author}) - {book.num_chunks} chunks")

st.markdown("---")
st.caption("💡 Después de indexar, puedes cerrar esta página y usar la app normalmente")
