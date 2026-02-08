"""
🧪 TEST OPENROUTER CONNECTIVITY
Ejecuta este script para verificar que tu API Key de OpenRouter funciona correctamente.
Uso: python scripts/test_openrouter.py
"""
import sys
import os

# Añadir directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_factory import LLMFactory
from langchain_core.messages import HumanMessage

def test_connection():
    print("🔌 Probando conexión a OpenRouter...")
    
    # 1. Verificar Key
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("❌ ERROR: No se encontró OPENROUTER_API_KEY en variables de entorno.")
        print("Asegúrate de haber configurado el .env o secrets.toml")
        return
    
    print(f"✅ API Key detectada: {key[:8]}...")
    
    # 2. Probar Chat (DeepSeek V3)
    try:
        print("🤖 Iniciando modelo Chat (DeepSeek V3)...")
        llm = LLMFactory.create(provider="chat")
        
        response = llm.invoke([HumanMessage(content="Hola, ¿qué modelo eres y qué puedes hacer?")])
        
        print("\n✅ RESPUESTA RECIBIDA:")
        print("-" * 50)
        print(response.content)
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR CONECTANDO AL CHAT: {e}")
        return

    # 3. Probar Embeddings
    try:
        print("\n🧠 Probando Embeddings (OpenAI via OpenRouter)...")
        embeddings = LLMFactory.create_embeddings()
        vector = embeddings.embed_query("Test de vectorización")
        
        if len(vector) > 0:
            print(f"✅ Embeddings generados vector de dimensión: {len(vector)}")
        else:
            print("❌ Embeddings generados pero vacíos.")
            
    except Exception as e:
        print(f"\n❌ ERROR CONECTANDO A EMBEDDINGS: {e}")
        return
        
    print("\n🎉 ¡TODO LISTO! OpenRouter está configurado y funcionando.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_connection()
