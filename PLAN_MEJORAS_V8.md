# 🚀 PLAN DE MEJORAS SINDICATO V8
## Ordenado por Prioridad (Crítico → Importante → Nice-to-Have)

---

## 🔴 PRIORIDAD 1: CRÍTICO (Bloquea el uso básico)

### 1.1 Persistencia de Estado entre Pestañas
**Problema**: Al cambiar de pestaña, los datos se pierden. No hay memoria entre secciones.
**Solución**:
- Usar `st.session_state` correctamente para TODOS los datos críticos
- Crear un `SessionManager` centralizado que persista:
  - Ticker seleccionado
  - Documento cargado (Oracle)
  - Resultados del Comité
  - Datos del SEC Analyzer
  - Portfolio configurado
- Añadir indicador visual en sidebar mostrando estado actual
**Esfuerzo**: 2-3 horas
**Archivos**: `app.py`, `services/session_manager.py`

### 1.2 Portfolio Optimizer No Funciona
**Problema**: El optimizador no calcula o no muestra resultados.
**Solución**:
- Revisar `services/portfolio_optimizer.py`
- Verificar que scipy/numpy están funcionando
- Añadir logging para debug
- Mostrar errores al usuario en lugar de fallar silenciosamente
**Esfuerzo**: 1-2 horas
**Archivos**: `services/portfolio_optimizer.py`, `app.py`

### 1.3 Biblioteca: Errores de Encoding HTML
**Problema**: 18 archivos HTML fallan por "utf-8 codec can't decode byte 0x92"
**Causa**: Los archivos HTML usan encoding Windows-1252 (cp1252), no UTF-8
**Solución**:
- Modificar `_extract_html()` en `services/knowledge_library.py`
- Probar múltiples encodings: utf-8 → latin-1 → cp1252 → errors='ignore'
**Esfuerzo**: 30 min
**Archivos**: `services/knowledge_library.py`

---

## 🟠 PRIORIDAD 2: IMPORTANTE (Afecta usabilidad)

### 2.1 "Documento Cargado: None" - Estado Visible
**Problema**: El usuario no sabe si hay documento cargado.
**Solución**:
- Crear widget en sidebar que muestre:
  ```
  📄 Documento Activo: AAPL_10-K_2024.pdf
  📊 Chunks: 245
  🕐 Cargado: hace 5 min
  ```
- Persistir en session_state
**Esfuerzo**: 1 hora
**Archivos**: `app.py`

### 2.2 SEC Analyzer: Solo 5 Chunks
**Problema**: Al indexar un 10-K solo se crean 5 chunks (muy pocos para un doc de 100+ páginas)
**Causa**: El contenido se trunca antes de chunkearse
**Solución**:
- Revisar `ingest_text()` en `services/oracle.py`
- Aumentar límite de caracteres de 10,000 a 100,000+
- Mostrar estadísticas: "Indexados X chunks de Y páginas"
**Esfuerzo**: 1 hora
**Archivos**: `services/oracle.py`, `app.py`

### 2.3 Comparador: Buscar Empresas del MISMO Sector
**Problema**: Busca empresas "similares" por market cap, no por industria.
**Solución**:
- Obtener `sector` e `industry` de yFinance
- Filtrar primero por sector, luego por tamaño
- Añadir opción: "Mismo Sector" vs "Cualquier Sector"
**Esfuerzo**: 1-2 horas
**Archivos**: `services/comparator.py`, `app.py`

### 2.4 Learning Oracle: Más Preguntas Sugeridas
**Problema**: Solo 3 preguntas sugeridas predefinidas.
**Solución**:
- Generar preguntas dinámicas basadas en:
  - Ticker actual
  - Sector/Industria
  - Eventos recientes (earnings, noticias)
- Guardar historial de preguntas del usuario
**Esfuerzo**: 1 hora
**Archivos**: `app.py`, `config.py`

---

## 🟡 PRIORIDAD 3: MEJORAS DE UX

### 3.1 Explicaciones en Tooltips
**Problema**: El usuario no entiende qué significan los campos.
**Solución**: Añadir tooltips explicativos:
- **Rendimiento (Gráficos)**: "Rentabilidad acumulada del precio en el periodo seleccionado"
- **Frontera Eficiente**: "Curva que muestra las carteras óptimas para cada nivel de riesgo"
- **Asignaciones**: "Peso % de cada activo calculado para maximizar el Ratio Sharpe"
- **Correlaciones**: "Mide cómo se mueven los activos juntos (-1 a +1)"
**Esfuerzo**: 2 horas
**Archivos**: `app.py`

### 3.2 Visión Macro: Contenido de Analistas
**Problema**: Falta integrar conocimiento de Pablo Gil u otros analistas macro.
**Opciones**:
1. **Transcripciones de videos**: Subir TXT con transcripciones de videos
2. **Cartas macro**: Indexar newsletters macro en la biblioteca
3. **API de noticias**: Integrar con NewsAPI/Finnhub para contexto actual
**Solución recomendada**: 
- Crear carpeta `biblioteca_macro/` con transcripciones
- Añadir tag "macro" para búsquedas específicas
**Esfuerzo**: 2-3 horas (preparación de contenido + código)

### 3.3 Secciones del 10-K Explicadas
**Problema**: Usuario no entiende "Business Description", "Risk Factors", etc.
**Solución**: Añadir ayuda contextual:
```
📋 Business (Item 1): Descripción del negocio, productos, competencia
⚠️ Risk Factors (Item 1A): Riesgos identificados por la empresa
📊 MD&A (Item 7): Análisis de resultados por la gerencia
💰 Financials (Item 8): Estados financieros auditados
```
**Esfuerzo**: 30 min
**Archivos**: `app.py`

---

## 🔵 PRIORIDAD 4: NICE-TO-HAVE (Futuro)

### 4.1 Integración con NotebookLM / Grafos
**Problema**: El usuario quiere una base de conocimiento más potente.
**Realidad**: NotebookLM no tiene API pública.
**Alternativas**:
1. **Neo4j/GraphRAG**: Sistema de grafos para relaciones entre conceptos
2. **Obsidian-like**: Notas interconectadas
3. **LangGraph**: Flujos de agentes con memoria
**Recomendación**: Implementar un sistema simple de "temas relacionados" primero.
**Esfuerzo**: 1-2 días (para versión básica)

### 4.2 Formato de Números en Estados Financieros
**Problema**: Los números aparecen crudos (6220000000 en lugar de $6.2B)
**Solución**: Aplicar formato B/M/K ya implementado en `format_financial_number()`
**Esfuerzo**: 30 min (ya existe la función, solo falta aplicarla)

---

## 📋 ORDEN DE EJECUCIÓN RECOMENDADO

| # | Tarea | Prioridad | Tiempo | Impacto |
|---|-------|-----------|--------|---------|
| 1 | Persistencia de Estado | 🔴 Crítico | 2h | ⭐⭐⭐⭐⭐ |
| 2 | Fix Encoding Biblioteca | 🔴 Crítico | 30min | ⭐⭐⭐⭐ |
| 3 | Portfolio Optimizer | 🔴 Crítico | 1-2h | ⭐⭐⭐⭐ |
| 4 | Estado Documento Visible | 🟠 Importante | 1h | ⭐⭐⭐⭐ |
| 5 | SEC: Más Chunks | 🟠 Importante | 1h | ⭐⭐⭐ |
| 6 | Comparador por Sector | 🟠 Importante | 1-2h | ⭐⭐⭐ |
| 7 | Tooltips Explicativos | 🟡 UX | 2h | ⭐⭐⭐ |
| 8 | Preguntas Sugeridas | 🟠 Importante | 1h | ⭐⭐ |
| 9 | Formato Números | 🟡 UX | 30min | ⭐⭐ |
| 10 | Macro Analistas | 🟡 UX | 3h | ⭐⭐ |

---

## 🎯 ¿POR DÓNDE EMPEZAMOS?

**Recomiendo empezar por #1 (Persistencia)** porque resuelve el problema de "todo se borra" y es la base para que el resto funcione bien.

¿Confirmamos este orden o prefieres priorizar diferente?
