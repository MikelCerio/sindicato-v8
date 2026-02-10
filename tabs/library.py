import streamlit as st

def render_tab(ticker: str): # ticker param is unused but keeps signature consistent
    """
    Renderiza la pestaña de Biblioteca de Conocimiento.
    """
    st.header("📚 Biblioteca de Sabiduría")
    
    lib = st.session_state.library
    
    # 0. Header Stats
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric("Libros Indexados", lib.book_count)
    with col2:
        st.info("La biblioteca contiene principios de grandes inversores que se cruzan con el análisis del 10-K.")

    st.markdown("---")

    # 1. Action Buttons
    col_upload, col_index = st.columns([1, 1])
    
    with col_upload:
        uploaded_files = st.file_uploader("Subir PDFs / EPUBs", accept_multiple_files=True, type=['pdf', 'epub', 'txt'])
        if uploaded_files:
            if st.button("Procesar Archivos"):
                with st.spinner("Leyendo y vectorizando libros..."):
                    for f in uploaded_files:
                        # Save temp
                        path = f"temp_{f.name}"
                        with open(path, "wb") as buffer:
                            buffer.write(f.getbuffer())
                        # Add to lib
                        lib.add_book(path) # Assumes add_book method handles indexing
                    st.success("Libros añadidos a la base de conocimiento.")
                    st.rerun()

    with col_index:
        if st.button("🧠 Re-Indexar Sabiduría Esencial (Buffett/Graham)"):
            with st.spinner("Cargando clásicos..."):
                count = st.session_state.library_service.add_essential_wisdom() # Hypothetical service call
                st.success(f"Añadidos {count} bloques de sabiduría clásica.")

    # 2. Explorador de Contenido
    st.subheader("📖 Contenido Disponible")
    
    if lib.book_count > 0:
        for book in lib.books:
            with st.expander(f"📘 {book.title} - {book.author}"):
                st.write(f"Chunks: {book.num_chunks}")
                st.caption(f"Indexado el: {book.indexed_at}")
    else:
        st.warning("La biblioteca está vacía. Sube libros o carga la sabiduría esencial.")

    # 3. Búsqueda de Prueba
    st.subheader("🔍 Probador de Búsqueda Semántica")
    query = st.text_input("Buscar concepto en biblioteca:")
    if query:
        res = lib.search(query, k=3)
        for r in res:
             st.markdown(f"**{r.source}**: {r.content[:200]}...")
