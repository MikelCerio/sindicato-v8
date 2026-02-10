import streamlit as st

def render_tab(ticker: str):
    """
    Renderiza la pestaña del Mentor / Oráculo.
    """
    st.header(f"👨‍🏫 Mentor Financiero - Consultas sobre {ticker}")
    
    # 0. CHAT INTERFACE
    if "mentor_messages" not in st.session_state:
        st.session_state.mentor_messages = []

    # Mostrar historial
    for msg in st.session_state.mentor_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input usuario
    if prompt := st.chat_input("Pregunta lo que quieras sobre la empresa o conceptos..."):
        # 1. Guardar y mostrar usuario
        st.session_state.mentor_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Respuesta Mentor
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                # Obtener contexto del Oráculo (10-K) + Biblioteca
                context_doc = st.session_state.oraculo.search(prompt, k=3)
                # context_lib = st.session_state.library.search(prompt, k=2) # TODO: Implementar búsqueda biblioteca
                
                full_context = f"Documento {ticker}:\n{context_doc}"
                
                response = st.session_state.mentor.explain(prompt, context=full_context)
                st.markdown(response)
        
        st.session_state.mentor_messages.append({"role": "assistant", "content": response})

    st.markdown("---")
    
    # SUGERENCIAS
    st.subheader("💡 Preguntas Sugeridas")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("¿Cuál es el Foso Económico (Moat)?"):
             # Simular input (requiere rerun o callback)
             pass
    with col2:
        if st.button("Explicame los Riesgos del 10-K"):
             pass
