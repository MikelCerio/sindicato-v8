"""
🏭 LLM FACTORY - SINGLETON FOR AI MODELS
Centraliza la creación de modelos para soportar OpenRouter y múltiples proveedores.
"""

import os
import logging
from typing import Optional, Literal

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Obtenemos configuración directamente de os.environ para evitar problemas de orden de importación
# ya que config.py initialize() corre al arranque
IS_OPENROUTER = bool(os.getenv("OPENROUTER_API_KEY"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

# === MODEL CONSTANTS ===
MODEL_FAST = "google/gemini-flash-1.5"        # Para lectura masiva (Free/Cheap)
MODEL_LONG_CONTEXT = "moonshot/moonshot-v1-128k"   # Kimi 128k (o 8k si no disponible)
MODEL_REASONING = "deepseek/deepseek-r1"    # DeepSeek R1 (O1 level)
MODEL_CHAT = "deepseek/deepseek-chat"       # DeepSeek V3 (GPT-4 level, super cheap)
MODEL_PREMIUM = "anthropic/claude-3-opus"   # Claude 3 Opus (Top Quality)
MODEL_EMBEDDING = "openai/text-embedding-3-small"

class LLMFactory:
    """Fabrica de modelos configurada para OpenRouter."""
    
    @staticmethod
    def create(
        provider: Literal["fast", "context", "reasoning", "chat", "premium"] = "chat",
        temperature: float = 0.7
    ) -> ChatOpenAI:
        """
        Crea una instancia de ChatOpenAI apuntando a OpenRouter (si está configurado).
        
        Args:
            provider: Tipo de modelo deseado:
                - 'fast': Gemini Flash (Barato, rápido)
                - 'context': Kimi (Contexto largo)
                - 'reasoning': DeepSeek R1 (Razonamiento profundo)
                - 'chat': DeepSeek V3 (Chat general barato)
                - 'premium': Claude 3 Opus (Calidad máxima, caro)
        """
        # Re-check environment variables at runtime
        is_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if is_openrouter:
            base_url = "https://openrouter.ai/api/v1"
            
            # Seleccionar modelo
            if provider == "fast":
                model = MODEL_FAST
            elif provider == "context":
                model = MODEL_LONG_CONTEXT
            elif provider == "reasoning":
                model = MODEL_REASONING
            elif provider == "premium":
                model = MODEL_PREMIUM
            else:
                model = MODEL_CHAT
                
            logger.info(f"🔌 LLMFactory: Creando {model} via OpenRouter")
            
            return ChatOpenAI(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                default_headers={
                    "HTTP-Referer": "https://sindicato.ai", # Required by OpenRouter
                    "X-Title": "Sindicato V8"
                }
            )
        else:
            # Fallback a OpenAI directo si no hay OpenRouter configurado
            logger.warning("⚠️ LLMFactory: OpenRouter no configurado. Usando OpenAI directo.")
            from config import OPENAI_API_KEY
            return ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=temperature)

    @staticmethod
    def create_embeddings():
        """Crea embeddings via OpenRouter o OpenAI."""
        if IS_OPENROUTER:
            logger.info(f"🔌 LLMFactory: Embeddings via OpenRouter ({MODEL_EMBEDDING})")
            return OpenAIEmbeddings(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                model=MODEL_EMBEDDING
            )
        else:
            from config import OPENAI_API_KEY
            return OpenAIEmbeddings(api_key=OPENAI_API_KEY)
