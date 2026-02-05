# =============================================================================
# 🚀 CELDA ÚNICA PARA EJECUTAR SINDICATO V8 EN COLAB
# Copia y pega TODO este código en una celda de Colab
# =============================================================================

import os
import time
import subprocess
from getpass import getpass

# -----------------------------------------------------------------------------
# PASO 1: Configurar API Keys
# -----------------------------------------------------------------------------
print("=" * 60)
print("🔧 CONFIGURACIÓN INICIAL")
print("=" * 60)

# OpenAI API Key
if 'OPENAI_API_KEY' not in os.environ or not os.environ['OPENAI_API_KEY']:
    openai_key = getpass('🔑 Ingresa tu OpenAI API Key: ')
    os.environ['OPENAI_API_KEY'] = openai_key
    print('✅ OpenAI API Key configurada')
else:
    print('✅ OpenAI API Key ya estaba configurada')

# Ngrok Authtoken
ngrok_token = getpass('🔑 Ingresa tu Ngrok Authtoken: ')

# -----------------------------------------------------------------------------
# PASO 2: Configurar ngrok
# -----------------------------------------------------------------------------
from pyngrok import ngrok, conf

if ngrok_token:
    conf.get_default().auth_token = ngrok_token
    print('✅ Ngrok Authtoken configurado')
else:
    print('⚠️ Sin Ngrok token, usando localtunnel como alternativa')

# -----------------------------------------------------------------------------
# PASO 3: Ir al directorio de la app
# -----------------------------------------------------------------------------
APP_PATH = '/content/drive/MyDrive/Investing_vitaminado/sindicato_v8'

if os.path.exists(APP_PATH):
    os.chdir(APP_PATH)
    print(f'✅ Directorio: {APP_PATH}')
else:
    print(f'❌ ERROR: No existe {APP_PATH}')
    print('   Asegúrate de haber copiado sindicato_v8 a tu Drive')

# -----------------------------------------------------------------------------
# PASO 4: Matar procesos anteriores (por si hay streamlit zombie)
# -----------------------------------------------------------------------------
subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
time.sleep(2)
print('✅ Procesos anteriores limpiados')

# -----------------------------------------------------------------------------
# PASO 5: Iniciar Streamlit en background
# -----------------------------------------------------------------------------
print('\n🚀 Iniciando Streamlit...')

# Iniciar streamlit
process = subprocess.Popen(
    ['streamlit', 'run', 'app.py', 
     '--server.port', '8501',
     '--server.headless', 'true',
     '--server.enableCORS', 'false',
     '--server.enableXsrfProtection', 'false'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# -----------------------------------------------------------------------------
# PASO 6: Esperar a que Streamlit esté listo
# -----------------------------------------------------------------------------
print('⏳ Esperando a que Streamlit inicie...')

import socket

def is_port_open(port, host='localhost'):
    """Verifica si el puerto está disponible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except:
        return False

# Esperar hasta 30 segundos
for i in range(30):
    if is_port_open(8501):
        print('✅ Streamlit está corriendo en puerto 8501')
        break
    time.sleep(1)
    print(f'   Esperando... {i+1}s')
else:
    print('❌ ERROR: Streamlit no inició. Revisa los logs:')
    print(process.stderr.read().decode())

# -----------------------------------------------------------------------------
# PASO 7: Crear túnel con ngrok
# -----------------------------------------------------------------------------
print('\n🌐 Creando túnel público...')

try:
    # Cerrar túneles anteriores
    ngrok.kill()
    time.sleep(1)
    
    # Crear nuevo túnel
    public_url = ngrok.connect(8501)
    
    print('\n' + '=' * 60)
    print('🎉 ¡APLICACIÓN LISTA!')
    print('=' * 60)
    print(f'\n🔗 URL PÚBLICA: {public_url}')
    print('\n   Abre este link en tu navegador')
    print('   (La primera vez puede tardar unos segundos en cargar)')
    print('\n💡 Para detener: Ejecuta ngrok.kill() o reinicia el runtime')
    print('=' * 60)
    
except Exception as e:
    print(f'❌ Error con ngrok: {e}')
    print('\n📌 Alternativa: Usar localtunnel')
    print('   Ejecuta en otra celda: !npx localtunnel --port 8501')
