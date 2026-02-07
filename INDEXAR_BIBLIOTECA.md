# 🚀 Cómo Indexar la Biblioteca - GUÍA RÁPIDA

## ⚡ Opción 1: Usando el Script Automático (Recomendado)

### Paso 1: Configura tu API Key de OpenAI

**Opción A - Temporal (solo esta sesión):**
```powershell
# En PowerShell
$env:OPENAI_API_KEY = "sk-tu-api-key-aqui"
```

**Opción B - Permanente (recomendado):**
1. Copia el archivo de ejemplo:
   ```powershell
   Copy-Item ".streamlit\secrets.toml.example" ".streamlit\secrets.toml"
   ```

2. Edita `.streamlit\secrets.toml` y reemplaza:
   ```toml
   [openai]
   api_key = "sk-tu-api-key-real-aqui"
   ```

3. Configura la variable de entorno desde el archivo:
   ```powershell
   # Lee el secrets.toml y extrae la API key
   $content = Get-Content ".streamlit\secrets.toml" -Raw
   if ($content -match 'api_key\s*=\s*"([^"]+)"') {
       $env:OPENAI_API_KEY = $matches[1]
       Write-Host "✅ API Key configurada desde secrets.toml"
   }
   ```

### Paso 2: Ejecuta el Indexador

**Opción A - Doble clic:**
```
Haz doble clic en: run_indexer.bat
```

**Opción B - PowerShell:**
```powershell
.\run_indexer.bat
```

**Opción C - Python directo:**
```powershell
C:\Users\PCUser\.local\bin\python3.11.exe index_biblioteca.py
```

---

## 📊 Qué Esperar

El script va a:
1. ✅ Verificar la API key
2. ✅ Buscar 63 archivos en `1_BIBLIOTECA`
3. ✅ Extraer texto de cada archivo
4. ✅ Crear chunks (fragmentos) de ~1500 caracteres
5. ✅ Generar embeddings con OpenAI
6. ✅ Guardar todo en `knowledge_library/`

**Tiempo estimado:** 5-10 minutos (depende de tu conexión)

**Salida esperada:**
```
============================================================
📚 INDEXADOR DE BIBLIOTECA - Sindicato V8
============================================================

✅ Dependencias cargadas correctamente
✅ OPENAI_API_KEY configurada

📁 Carpeta: 1_BIBLIOTECA
📚 Archivos encontrados: 63

============================================================
🚀 INICIANDO INDEXACIÓN
============================================================

[1/63] Carta_Buffett_1977.html
   ✅ 45 chunks

[2/63] Carta_Buffett_1978.html
   ✅ 52 chunks

...

[63/63] Security Analysis (Benjamin_ (Z-Library).epub
   ✅ 1234 chunks

============================================================
💾 GUARDANDO DATOS...
============================================================
✅ Vectorstore guardado
✅ Metadata guardada

============================================================
🎉 INDEXACIÓN COMPLETADA
============================================================
✅ Indexados: 61/63
❌ Errores: 2
📊 Total en biblioteca: 61

💡 Los libros están listos para usar en la app
============================================================
```

---

## 🔧 Troubleshooting

### Error: "OPENAI_API_KEY no configurada"
**Solución:**
```powershell
$env:OPENAI_API_KEY = "sk-tu-api-key-aqui"
```

### Error: "No module named 'langchain'"
**Solución:**
```powershell
C:\Users\PCUser\.local\bin\python3.11.exe -m pip install langchain langchain-openai langchain-community faiss-cpu pdfplumber beautifulsoup4 ebooklib
```

### Error: "No se pudo extraer texto"
Algunos archivos pueden fallar (PDFs protegidos, EPUBs corruptos). Esto es normal.
El script continuará con los demás archivos.

### Error: "Rate limit exceeded"
Si tienes muchos archivos, OpenAI puede limitar las peticiones.
El script se detendrá. Espera unos minutos y vuelve a ejecutarlo.
Los archivos ya procesados no se volverán a procesar.

---

## ✅ Verificar que Funcionó

Después de indexar, verifica:

```powershell
# Ver archivos generados
dir knowledge_library\

# Deberías ver:
# - vectorstore\index.faiss
# - vectorstore\index.pkl
# - metadata.json
```

---

## 🎯 Usar la Biblioteca

Una vez indexada, los libros estarán disponibles en la app:

1. **Inicia Streamlit:**
   ```powershell
   streamlit run app.py
   ```

2. **Ve a la pestaña 📚 BIBLIOTECA**

3. **Busca algo:**
   ```
   "¿Qué dice Buffett sobre la deuda?"
   ```

4. **Verás fragmentos relevantes con citas:**
   ```
   📖 Carta a los Accionistas 1989 (Warren Buffett):
   "Una empresa realmente buena no necesita pedir prestado..."
   ```

---

## 💡 Tips

1. **Primera vez:** Indexa todos los archivos
2. **Añadir más libros:** Pon nuevos archivos en `1_BIBLIOTECA` y vuelve a ejecutar
3. **Limpiar y empezar de nuevo:**
   ```powershell
   Remove-Item -Recurse -Force knowledge_library\
   .\run_indexer.bat
   ```

---

¿Problemas? Revisa los logs en la terminal donde ejecutaste el script.
