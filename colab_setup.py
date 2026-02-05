"""
🏛️ SINDICATO V8 - Notebook para Google Colab
Copia este código en una celda de Colab para ejecutar.
"""

# ============================================================================
# CELDA 1: MONTAJE DE DRIVE
# ============================================================================
"""
from google.colab import drive
drive.mount('/content/drive')
"""

# ============================================================================
# CELDA 2: INSTALACIÓN DE DEPENDENCIAS
# ============================================================================
"""
%%bash
pip install -q streamlit yfinance pandas
pip install -q crewai langchain langchain-openai langchain-community
pip install -q faiss-cpu pdfplumber beautifulsoup4 textblob reportlab plotly
pip install -q python-dotenv
"""

# ============================================================================
# CELDA 3: CONFIGURAR API KEY
# ============================================================================
"""
import os
os.environ['OPENAI_API_KEY'] = 'sk-tu-api-key-aqui'  # ← REEMPLAZAR
"""

# ============================================================================
# CELDA 4: COPIAR CÓDIGO (Alternativa si no tienes los archivos)
# ============================================================================
"""
# Si ya tienes los archivos en Drive, salta esta celda
# Si no, ejecuta esta celda para crear todos los archivos

import os

base_path = '/content/drive/MyDrive/sindicato_v8'
os.makedirs(base_path, exist_ok=True)
os.makedirs(f'{base_path}/services', exist_ok=True)
os.makedirs(f'{base_path}/agents', exist_ok=True)

# Aquí irían los %%writefile para cada archivo
# (usar los archivos creados en la estructura modular)
"""

# ============================================================================
# CELDA 5: EJECUTAR STREAMLIT
# ============================================================================
"""
%%bash
cd /content/drive/MyDrive/sindicato_v8
streamlit run app.py &>/content/logs.txt &
npx localtunnel --port 8501
"""

# ============================================================================
# ALTERNATIVA: VERSION COMPACTA (TODO EN UN ARCHIVO)
# ============================================================================
# Si prefieres un solo archivo sin estructura modular,
# usa esta versión que combina todo:

COMPACT_VERSION = '''
%%writefile /content/drive/MyDrive/sindicato_v8/app_compact.py
# Versión compacta con todo incluido
# (Contenido del app.py original con imports inline)
'''

print("📋 Instrucciones para Google Colab:")
print("1. Monta Drive")
print("2. Copia la carpeta sindicato_v8 a tu Drive") 
print("3. Instala dependencias con pip")
print("4. Configura OPENAI_API_KEY")
print("5. Ejecuta streamlit + localtunnel")
