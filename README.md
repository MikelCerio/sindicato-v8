# 🏛️ Sindicato V8 Elite - Institutional Platform

**Sindicato V8 Elite** es una plataforma de inversión institucional modularizada y potenciada por IA (OpenRouter + CrewAI). Diseñada para análisis profundo de acciones, debate de comités de inversión y gestión de carteras.

## 🚀 Características Clave
- **Smart Routing (OpenRouter)**: Uso eficiente de modelos (Gemini Flash para lectura masiva, DeepSeek R1 para razonamiento, DeepSeek V3 para debate).
- **Comité de Inversiones (CrewAI)**: Agentes especializados (Value, Growth, Risk) debaten y generan informes con UI de tarjetas.
- **SEC Analyzer**: Indexación y análisis automático de 10-K/10-Q.
- **Datos Financieros**: Integración con OpenBB para métricas fundamentales y gráficos.
- **Biblioteca de Sabiduría**: RAG sobre libros de inversión clásicos.

## 📂 Estructura del Proyecto (Modular)
El proyecto ha sido refactorizado para máxima mantenibilidad:

```
sindicato_v8/
├── app.py              # Orquestador principal (Streamlit entry point)
├── config.py           # Configuración central (API Keys, Rutas)
├── tabs/               # Módulos de la UI
│   ├── committee.py    # UI del Comité de Inversión
│   ├── data.py         # Dashboard financiero
│   ├── sec.py          # Analizador SEC
│   ├── discovery.py    # Screener de acciones
│   ├── mentor.py       # Chat con el Oráculo
│   └── library.py      # Gestión de conocimiento
├── services/           # Lógica de negocio (Backend)
│   ├── llm_factory.py  # Factoría de modelos (Smart Routing)
│   ├── oraculo.py      # Motor RAG
│   └── ...
├── agents/             # Definición de agentes CrewAI
├── deploy/             # Scripts de despliegue (Colab)
└── docs/               # Documentación y guías
```

## 🛠️ Instalación y Uso

1.  **Configurar Entorno**:
    Crea un archivo `.env` con tus claves:
    ```bash
    OPENROUTER_API_KEY=sk-or-...
    OPENAI_API_KEY=sk-... (Opcional, fallback)
    ```

2.  **Instalar Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Ejecutar la App**:
    ```bash
    streamlit run app.py
    ```

## 📚 Documentación
Guías detalladas disponibles en la carpeta `docs/`:
- [Guía de Usuario](docs/User_Guide.md)
- [Setup API](docs/Setup_API.md)
- [Despliegue](docs/Deploy.md)

---
*Refactorizado y optimizado - Febrero 2026*
