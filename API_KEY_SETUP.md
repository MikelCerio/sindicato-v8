# 🔑 Configuración de API Key - Guía para Usuarios

## 🎯 Opciones para Configurar tu API Key

Tienes **3 formas** de configurar tu API key de OpenAI. Elige la que prefieras:

---

## ⭐ Opción 1: Desde la App (Recomendado)

**La forma más fácil y segura:**

1. **Inicia la app:**
   ```bash
   streamlit run app.py
   ```

2. **En la sidebar (izquierda), verás:**
   ```
   🔑 Configuración
   ⚠️ API Key no configurada
   ```

3. **Haz clic en "🔧 Configurar API Key"**

4. **Ingresa tu API key:**
   - Pega tu API key (empieza con `sk-proj-...`)
   - Haz clic en "💾 Guardar API Key"

5. **¡Listo!** La app se recargará y estará lista para usar

### ✅ Ventajas:
- ✅ No necesitas editar archivos
- ✅ Tu API key solo se guarda en tu sesión
- ✅ No se comparte con nadie
- ✅ Fácil de cambiar

---

## 📝 Opción 2: Archivo de Configuración Local

**Para uso personal permanente:**

1. **Copia el archivo de ejemplo:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Edita `.streamlit/secrets.toml`:**
   ```toml
   [openai]
   api_key = "sk-proj-TU-API-KEY-AQUI"
   ```

3. **Guarda el archivo**

4. **Inicia la app:**
   ```bash
   streamlit run app.py
   ```

### ✅ Ventajas:
- ✅ Configuración permanente
- ✅ No necesitas ingresar la key cada vez
- ✅ El archivo está en `.gitignore` (no se sube a GitHub)

### ⚠️ Importante:
- **NUNCA** subas `secrets.toml` a GitHub
- **NUNCA** compartas este archivo
- El archivo ya está en `.gitignore` para protegerte

---

## 🌍 Opción 3: Variable de Entorno

**Para servidores o deployments:**

### Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY = "sk-proj-TU-API-KEY-AQUI"
streamlit run app.py
```

### Linux/Mac:
```bash
export OPENAI_API_KEY="sk-proj-TU-API-KEY-AQUI"
streamlit run app.py
```

### Permanente (Windows):
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-TU-API-KEY-AQUI', 'User')
```

### Permanente (Linux/Mac):
Añade a `~/.bashrc` o `~/.zshrc`:
```bash
export OPENAI_API_KEY="sk-proj-TU-API-KEY-AQUI"
```

---

## 🔐 ¿Dónde Conseguir una API Key?

1. **Ve a:** https://platform.openai.com/api-keys
2. **Inicia sesión** (o crea una cuenta)
3. **Haz clic en:** "Create new secret key"
4. **Copia la key** (empieza con `sk-proj-...`)
5. **Guárdala en un lugar seguro** (solo se muestra una vez)

---

## 🔒 Seguridad

### ✅ Buenas Prácticas:
- ✅ Usa la **Opción 1** (desde la app) si compartes el código
- ✅ Cada usuario debe usar su propia API key
- ✅ Nunca compartas tu API key
- ✅ Nunca subas `secrets.toml` a GitHub
- ✅ Rota tu API key periódicamente

### ❌ Nunca Hagas Esto:
- ❌ Hardcodear la API key en el código
- ❌ Compartir tu API key en Slack/Discord/Email
- ❌ Subir `secrets.toml` a GitHub
- ❌ Usar la misma API key para todos los usuarios

---

## 🎯 Prioridad de Configuración

La app busca la API key en este orden:

1. **Session State** (ingresada en la app) ← Prioridad más alta
2. **Streamlit Secrets** (`.streamlit/secrets.toml`)
3. **Variable de Entorno** (`OPENAI_API_KEY`)

Si tienes configurada en varios lugares, se usará la de mayor prioridad.

---

## 🔧 Troubleshooting

### "⚠️ API Key no configurada"
**Solución:** Usa la Opción 1 (desde la app) o verifica que tu archivo `secrets.toml` esté bien configurado.

### "❌ API Key inválida"
**Solución:** Verifica que tu API key:
- Empiece con `sk-proj-` o `sk-`
- No tenga espacios al inicio/final
- Sea una key válida de OpenAI

### "Error: Incorrect API key provided"
**Solución:** Tu API key es incorrecta o ha expirado. Genera una nueva en OpenAI Platform.

### "Error: You exceeded your current quota"
**Solución:** Tu cuenta de OpenAI no tiene créditos. Añade un método de pago en OpenAI Platform.

---

## 💡 Tips

1. **Para desarrollo local:** Usa la Opción 2 (archivo `secrets.toml`)
2. **Para compartir con equipo:** Cada uno usa la Opción 1 (desde la app)
3. **Para producción:** Usa la Opción 3 (variables de entorno)

---

## 📊 Verificar que Funciona

Después de configurar tu API key:

1. Verás en la sidebar:
   ```
   ✅ API Key configurada (Usuario/Secrets/Entorno)
   ```

2. Prueba cualquier función de la app:
   - 🦈 Comité de Inversiones
   - 📚 Biblioteca
   - 👨‍🏫 Mentor

3. Si funciona, ¡estás listo! 🎉

---

¿Problemas? Abre un issue en GitHub o contacta al equipo.
