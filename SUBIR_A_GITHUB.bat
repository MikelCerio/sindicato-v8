@echo off
REM ============================================================================
REM 🏛️ SINDICATO V8 ELITE - Script de Subida a GitHub
REM ============================================================================
REM
REM INSTRUCCIONES:
REM 1. Crea un repositorio VACÍO en GitHub (sin README, .gitignore, ni LICENSE)
REM    URL: https://github.com/new
REM
REM 2. Copia la URL del repositorio (ej: https://github.com/TU-USUARIO/sindicato-v8.git)
REM
REM 3. Edita este script y reemplaza TU-USUARIO con tu nombre de usuario
REM
REM 4. Ejecuta este script desde PowerShell o CMD
REM ============================================================================

echo.
echo 🏛️ SINDICATO V8 ELITE - Subida a GitHub
echo ========================================
echo.

REM Configura tu repositorio aquí:
set REPO_URL=https://github.com/TU-USUARIO/sindicato-v8.git

echo Añadiendo remote origin...
git remote add origin %REPO_URL%

echo Renombrando branch a main...
git branch -M main

echo Subiendo a GitHub...
git push -u origin main

echo.
echo ✅ ¡Listo! Tu código está en GitHub.
echo.
echo 📌 PRÓXIMOS PASOS:
echo    1. Ve a https://share.streamlit.io
echo    2. Conecta tu cuenta de GitHub
echo    3. Selecciona el repositorio: sindicato-v8
echo    4. Branch: main
echo    5. Main file: app.py
echo    6. En Settings > Secrets, añade:
echo       OPENAI_API_KEY = "sk-..."
echo    7. ¡Deploy!
echo.
pause
