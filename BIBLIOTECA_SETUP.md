# 📚 Guía de Indexación de Biblioteca

## 🎯 Objetivo
Indexar automáticamente todos los libros de inversión para que la IA pueda consultarlos.

---

## 📥 Opción 1: Descarga Manual (Recomendada)

### Paso 1: Descargar desde Google Drive
1. Ve a: https://drive.google.com/drive/folders/1jORbWga1qQYHcRgA9PpOiYCRW_mbY-Sb
2. Haz clic derecho en la carpeta → **Descargar**
3. Se descargará como `biblioteca_maestra.zip`

### Paso 2: Extraer archivos
```powershell
# En PowerShell (Windows)
cd C:\Users\PCUser\.gemini\antigravity\scratch\sindicato_v8

# Extraer ZIP
Expand-Archive -Path "C:\Users\PCUser\Downloads\biblioteca_maestra.zip" -DestinationPath ".\biblioteca_maestra"
```

### Paso 3: Indexar libros
```powershell
# Indexar todos los libros de la carpeta
python scripts\index_books.py biblioteca_maestra
```

---

## 🤖 Opción 2: Descarga Automática con gdown

### Paso 1: Instalar gdown
```powershell
pip install gdown
```

### Paso 2: Descargar e indexar
```powershell
# Descarga desde Google Drive e indexa automáticamente
python scripts\download_library.py --download --index
```

---

## 📖 Uso del Script de Indexación

### Indexar una carpeta específica:
```powershell
python scripts\index_books.py "ruta/a/tu/carpeta"
```

### Formatos soportados:
- ✅ PDF
- ✅ EPUB
- ✅ MOBI
- ✅ TXT
- ✅ Markdown (.md)
- ✅ HTML

### Convención de nombres (opcional):
Para mejor extracción de metadatos, nombra tus archivos así:
```
Autor - Título.pdf

Ejemplos:
Warren Buffett - Cartas a los Accionistas.pdf
Benjamin Graham - The Intelligent Investor.epub
Charlie Munger - Poor Charlie's Almanack.pdf
```

---

## 🔍 Verificar Biblioteca

### Desde la App:
1. Abre la app: `streamlit run app.py`
2. Ve a la pestaña **📚 BIBLIOTECA**
3. Verás todos los libros indexados

### Desde Python:
```python
from services import KnowledgeLibrary

lib = KnowledgeLibrary()
print(f"Libros indexados: {lib.book_count}")

for book in lib.books:
    print(f"- {book.title} ({book.author}) - {book.num_chunks} chunks")
```

---

## 🎨 Topics Automáticos

El script detecta automáticamente topics basándose en el nombre del archivo:

| Palabras clave | Topic asignado |
|----------------|----------------|
| buffett, munger, graham, lynch, value | `value investing` |
| technical, chart, trading | `technical analysis` |
| macro, economy, dalio, gil | `macroeconomics` |
| psychology, behavioral, kahneman | `behavioral finance` |

---

## 📊 Ejemplo de Salida

```
📁 Indexando carpeta: biblioteca_maestra

📚 Encontrados 47 libros

[1/47] Warren Buffett - Cartas a los Accionistas.pdf
   ✅ 234 chunks

[2/47] Benjamin Graham - The Intelligent Investor.epub
   ✅ 456 chunks

[3/47] Pablo Gil - Macro para Inversores.pdf
   ✅ 189 chunks

...

🎉 Completado: 45/47 libros indexados
📊 Total en biblioteca: 48
```

---

## 🗂️ Estructura de Archivos

Después de indexar, tendrás:

```
sindicato_v8/
├── biblioteca_maestra/          # Libros originales
│   ├── Warren Buffett - Cartas.pdf
│   ├── Graham - Intelligent Investor.epub
│   └── ...
│
├── knowledge_library/           # Datos persistentes
│   ├── vectorstore/             # Embeddings (FAISS)
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── metadata.json            # Info de libros
│
└── scripts/
    ├── index_books.py           # Indexador simple
    └── download_library.py      # Descarga desde GDrive
```

---

## 🚀 Uso en la App

Una vez indexados, los libros están disponibles automáticamente:

### En el Comité:
El comité puede consultar la biblioteca para enriquecer su análisis:
```
"¿Qué dice Buffett sobre empresas con deuda alta?"
→ Busca en la biblioteca y cita las fuentes
```

### En Búsqueda Manual:
1. Ve a **📚 BIBLIOTECA**
2. Escribe tu consulta: "moat analysis"
3. Verás fragmentos relevantes con citas

### En el Mentor:
El mentor puede recomendar lecturas específicas basándose en tu pregunta.

---

## 🔧 Troubleshooting

### Error: "ebooklib no instalado"
```powershell
pip install ebooklib
```

### Error: "No se encontraron libros"
Verifica que la carpeta existe y contiene archivos PDF/EPUB/MOBI.

### Error: "Error extrayendo PDF"
Algunos PDFs están protegidos. Intenta:
1. Abrirlo en Adobe Reader
2. Imprimir a PDF (sin protección)
3. Usar el nuevo PDF

### Los libros no aparecen en la app
1. Reinicia Streamlit: `Ctrl+C` y `streamlit run app.py`
2. Verifica que `knowledge_library/metadata.json` existe

---

## 💡 Tips

1. **Indexa una vez**: Los embeddings se guardan en disco, no necesitas re-indexar cada vez.

2. **Nombres descriptivos**: Usa el formato `Autor - Título` para mejor organización.

3. **Topics personalizados**: Puedes editar `metadata.json` manualmente para ajustar topics.

4. **Búsqueda avanzada**: En la app, puedes filtrar por autor o topic.

---

¿Necesitas ayuda? Revisa los logs en la terminal donde corre Streamlit.
