@echo off
echo ============================================================
echo INDEXADOR DE BIBLIOTECA - Sindicato V8
echo ============================================================
echo.

REM Verificar si existe la API key
if not defined OPENAI_API_KEY (
    echo [ERROR] OPENAI_API_KEY no configurada
    echo.
    echo Por favor, configura tu API key de OpenAI:
    echo.
    echo 1. Opcion A - Temporal ^(solo esta sesion^):
    echo    set OPENAI_API_KEY=sk-tu-api-key-aqui
    echo    run_indexer.bat
    echo.
    echo 2. Opcion B - Permanente:
    echo    - Crea el archivo .streamlit\secrets.toml
    echo    - Copia el contenido de .streamlit\secrets.toml.example
    echo    - Reemplaza "sk-your-api-key-here" con tu API key real
    echo.
    pause
    exit /b 1
)

echo [OK] OPENAI_API_KEY configurada
echo.
echo Iniciando indexacion...
echo.

REM Ejecutar el indexador
C:\Users\PCUser\.local\bin\python3.11.exe index_biblioteca.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] La indexacion fallo
    pause
    exit /b 1
)

echo.
echo ============================================================
echo INDEXACION COMPLETADA
echo ============================================================
echo.
echo Los libros estan listos para usar en la app
echo.
pause
