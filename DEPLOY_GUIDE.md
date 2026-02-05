# 🚀 Guía de Despliegue - Sindicato V8 Elite

## 📋 Paso 1: Crear Repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. **Repository name:** `sindicato-v8`
3. **Description:** `🏛️ Institutional Investment Platform with AI`
4. **Visibility:** Public o Private (tu elección)
5. ⚠️ **NO marques** ninguna de estas opciones:
   - Add a README file
   - Add .gitignore
   - Choose a license
6. Click **Create repository**

---

## 📤 Paso 2: Subir el Código

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
# Navegar a la carpeta
cd c:\Users\PCUser\.gemini\antigravity\scratch\sindicato_v8

# Añadir el remote (reemplaza TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/sindicato-v8.git

# Renombrar branch a main
git branch -M main

# Subir el código
git push -u origin main
```

**Nota:** Si te pide autenticación, usa un Personal Access Token:
- Ve a GitHub > Settings > Developer settings > Personal access tokens
- Genera un token con permisos `repo`
- Úsalo como contraseña

---

## ☁️ Paso 3: Desplegar en Streamlit Cloud

### 3.1 Conectar con Streamlit

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Conecta tu cuenta de GitHub (si no lo has hecho)

### 3.2 Configurar la App

| Campo | Valor |
|-------|-------|
| Repository | `TU-USUARIO/sindicato-v8` |
| Branch | `main` |
| Main file path | `app.py` |

### 3.3 Añadir Secrets (MUY IMPORTANTE)

1. Antes de hacer deploy, click en **Advanced settings**
2. En la sección **Secrets**, añade:

```toml
OPENAI_API_KEY = "sk-tu-api-key-aquí"
```

O en formato alternativo:

```toml
[openai]
api_key = "sk-tu-api-key-aquí"
```

3. Click **Deploy!**

---

## ⏱️ Paso 4: Esperar el Despliegue

- La primera vez tarda **5-10 minutos** (instalando dependencias)
- Verás logs en tiempo real
- Si hay errores, revisa los logs

---

## ✅ Paso 5: ¡Listo!

Tu app estará disponible en:
```
https://TU-USUARIO-sindicato-v8-app-XXXXX.streamlit.app
```

---

## 🔧 Solución de Problemas

### Error: "No module named X"
- Verifica que el módulo esté en `requirements.txt`
- Redeploy la app

### Error: "OPENAI_API_KEY not found"
- Verifica que añadiste los secrets correctamente
- El formato debe ser exacto

### La app es muy lenta
- Normal la primera vez (cold start)
- Las siguientes cargas serán más rápidas

### Error con OpenBB
- OpenBB es opcional
- Si falla, la app usa yfinance como fallback

---

## 🔄 Actualizar la App

Cada vez que hagas cambios:

```powershell
cd c:\Users\PCUser\.gemini\antigravity\scratch\sindicato_v8

# Añadir cambios
git add -A

# Commit
git commit -m "Descripción del cambio"

# Subir
git push
```

Streamlit Cloud detectará automáticamente los cambios y redesplegará.

---

## 📊 Monitoreo

En el dashboard de Streamlit Cloud puedes ver:
- **Logs**: Errores y warnings
- **Analytics**: Uso de la app
- **Settings**: Cambiar secrets, reiniciar, etc.

---

## 🔐 Seguridad

- **NUNCA** subas tu API key al código
- Usa siempre Streamlit Secrets
- El archivo `.env` está en `.gitignore` por seguridad

---

<p align="center">
  <strong>🏛️ Capital Preservation First</strong>
</p>
