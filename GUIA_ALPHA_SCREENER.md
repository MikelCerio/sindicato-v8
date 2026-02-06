# 🦅 GUÍA: Agente Alpha y Screener

## Fecha: 2026-02-06

---

## 🎯 **Nuevas Features Implementadas**

### 1. **Agente Alpha** (Small Caps / Situaciones Especiales)
### 2. **Screener/Descubridor** (Encuentra alternativas mejores)

---

## 🦅 **AGENTE ALPHA: Análisis de Small Caps**

### **¿Qué es?**
Un perfil de análisis especializado en empresas pequeñas (small caps) que se enfoca en:
- **Skin in the Game**: ¿Los directivos tienen acciones?
- **ROCE**: Retorno sobre capital empleado
- **Deuda**: Debe ser < 2x EBITDA
- **Ventaja Competitiva**: Nicho, monopolio local, switching costs

### **¿Cuándo usarlo?**
- Empresas con capitalización < $5B
- Empresas familiares o con fundador activo
- Situaciones especiales (spin-offs, turnarounds)
- Cuando quieras analizar como Peter Lynch o Mohnish Pabrai

### **¿Cómo usarlo?**

#### **Paso 1: Sube el 10-K**
```
1. Ve al tab "📂 DOCS"
2. Sube el Annual Report (10-K) de la empresa
3. Espera a que se procese
```

#### **Paso 2: Selecciona el Modo Alpha**
```
1. Ve al tab "🦈 COMITÉ"
2. En "Perfil del Analista", selecciona "Alpha (Small Cap)"
3. Haz clic en "🔥 AUDITAR"
```

#### **Paso 3: Revisa el Análisis**
El agente Alpha te dará:

**VALUE AUDIT (Ownership & Deuda):**
- % de acciones del CEO/Fundador
- Transacciones de insiders (¿comprando o vendiendo?)
- Deuda Neta / EBITDA
- Historial de capital allocation (buybacks vs M&A)

**GROWTH AUDIT (ROCE & Moat):**
- ROCE de los últimos 3 años
- Ventaja competitiva identificada
- Barreras de entrada
- Comparación de márgenes vs competidores

**RISK AUDIT (Red Flags):**
- Concentración de clientes (>20% revenue de 1 cliente)
- Deuda a corto plazo vs cash
- Contabilidad creativa (DSO, inventario)
- Litigios pendientes

### **Ejemplo de Uso:**

**Caso: Grupo de Inversión (Small Cap española)**

```
Ticker: GDI (ejemplo)
Capitalización: 200M€

1. Subes el 10-K de GDI
2. Seleccionas "Alpha (Small Cap)"
3. El agente te dice:
   - ✅ Fundador tiene 35% de acciones
   - ✅ ROCE de 22% (excelente)
   - ✅ Deuda/EBITDA de 0.8x (baja)
   - ⚠️ 30% del revenue viene de 1 cliente (concentración)
   
Conclusión: Posible gema, pero monitorear concentración de clientes
```

---

## 🕵️ **SCREENER: Descubre Alternativas Mejores**

### **¿Qué es?**
Una herramienta que:
1. Busca empresas similares a tu ticker (mismo sector)
2. Las analiza con criterios Alpha o Institucionales
3. Te muestra cuál es la mejor según los datos

### **¿Cuándo usarlo?**
- Alguien te recomienda una acción y quieres ver si hay mejores opciones
- Quieres comparar rápidamente competidores
- Buscas "gemas ocultas" en un sector

### **¿Cómo usarlo?**

#### **Paso 1: Elige el Ticker Base**
```
1. Escribe el ticker en el campo principal (ej: NVDA)
```

#### **Paso 2: Ve al Tab DESCUBRIR**
```
1. Ve al tab "🕵️ DESCUBRIR"
2. Selecciona el criterio:
   - "Institucional (Blue Chips)": Busca solidez
   - "Alpha (Small Cap)": Busca gemas con ownership alto
```

#### **Paso 3: Busca Gemas**
```
1. Haz clic en "🚀 Buscar Gemas"
2. Espera 10-20 segundos
3. Revisa la tabla de resultados
```

### **Cómo Interpretar los Resultados:**

#### **Modo Institucional:**
| Score | Tag | Significado |
|-------|-----|-------------|
| ≥ 3 | 🏢 Sólida | ROE >10%, P/E <30, Deuda baja |
| 2 | 📊 Neutral | Cumple algunos criterios |
| < 2 | 📉 Débil | No cumple criterios básicos |

#### **Modo Alpha:**
| Score | Tag | Significado |
|-------|-----|-------------|
| ≥ 4 | 💎 Posible Gema | Deuda baja, ROE >15%, valoración OK |
| 2-3 | ⚠️ Revisar | Cumple algunos criterios |
| < 2 | ❌ Evitar | No cumple criterios Alpha |

### **Ejemplo de Uso:**

**Caso: Te recomiendan NVIDIA**

```
1. Escribes "NVDA" en el ticker
2. Vas a "🕵️ DESCUBRIR"
3. Seleccionas "Institucional (Blue Chips)"
4. Haces clic en "🚀 Buscar Gemas"

Resultados:
┌─────────┬───────┬──────┬──────┬─────┬──────────┬────────┐
│ Ticker  │ Score │ Tag  │ P/E  │ ROE │ Deuda/Eq │ Margen │
├─────────┼───────┼──────┼──────┼─────┼──────────┼────────┤
│ TSM     │   4   │ 🏢   │ 28.3 │ 18% │   0.32   │ 42.1%  │
│ NVDA    │   3   │ 🏢   │ 72.1 │ 21% │   0.16   │ 55.2%  │
│ AMD     │   2   │ 📊   │ 45.2 │ 12% │   0.08   │ 18.3%  │
│ INTC    │   1   │ 📉   │ 18.9 │  4% │   0.52   │  8.1%  │
└─────────┴───────┴──────┴──────┴─────┴──────────┴────────┘

Conclusión: TSM (Taiwan Semiconductor) tiene mejor score que NVDA
```

---

## 🎓 **Casos de Uso Combinados**

### **Caso 1: Análisis Completo de Small Cap**

```
Objetivo: Analizar una small cap española que te recomendó Alejandro

1. DESCUBRIR:
   - Busca competidores con "Alpha (Small Cap)"
   - Identifica la mejor del sector

2. COMITÉ (Alpha):
   - Sube el 10-K de la mejor
   - Analiza con "Alpha (Small Cap)"
   - Revisa ownership, ROCE, deuda

3. VEREDICTO:
   - Obtén la decisión final
   - Descarga el informe PDF
```

### **Caso 2: Comparación Rápida de Blue Chips**

```
Objetivo: Comparar AAPL vs MSFT vs GOOGL

1. DESCUBRIR:
   - Ticker: AAPL
   - Modo: "Institucional"
   - Buscar Gemas

2. REVISAR TABLA:
   - Ver cuál tiene mejor score
   - Comparar P/E, ROE, Deuda

3. COMITÉ (Institucional):
   - Analizar la ganadora con modo "Institucional"
```

---

## 📊 **Diferencias Clave: Institucional vs Alpha**

| Aspecto | Institucional | Alpha (Small Cap) |
|---------|---------------|-------------------|
| **Foco** | Preservación de capital | Multibaggers (10x) |
| **Tamaño** | Large Caps (>$10B) | Small Caps (<$5B) |
| **Criterio #1** | Macro-consciencia | Skin in the Game |
| **Criterio #2** | Deuda manejable | ROCE >15% |
| **Criterio #3** | I+D sostenido | Ventaja competitiva |
| **Riesgo** | Volatilidad macro | Concentración, deuda |
| **Inspiración** | Buffett, Dalio | Lynch, Pabrai, Estebaranz |

---

## 🚀 **Tips Avanzados**

### **Tip 1: Combina Screener + SEC Analyzer**
```
1. Usa DESCUBRIR para encontrar la mejor del sector
2. Ve a "📄 SEC" y analiza su 10-K
3. Busca red flags en el análisis LLM
```

### **Tip 2: Biblioteca + Alpha**
```
1. Sube libros de Peter Lynch o Mohnish Pabrai a la biblioteca
2. El agente Alpha usará esa sabiduría en el análisis
```

### **Tip 3: Screener Iterativo**
```
1. Busca gemas en sector A (ej: Tech)
2. Toma la ganadora
3. Busca gemas en su sector específico
4. Encuentra la mejor de las mejores
```

---

## ⚠️ **Limitaciones Conocidas**

1. **Screener usa yfinance**: Datos pueden estar desactualizados
2. **Competidores limitados**: Solo busca en sectores principales
3. **Sin datos de ownership**: yfinance no tiene insider transactions
4. **Rate limiting**: Demasiadas búsquedas pueden dar error

---

## 🔮 **Próximas Mejoras**

1. **Screener con OpenBB**: Más datos de insiders
2. **Filtros personalizados**: Define tus propios criterios
3. **Alertas**: Notificaciones cuando una gema cumple criterios
4. **Backtesting**: Ver cómo hubiera funcionado el screener históricamente

---

## 📚 **Recursos Recomendados**

- **Libros**: "One Up On Wall Street" (Peter Lynch)
- **Libros**: "The Dhandho Investor" (Mohnish Pabrai)
- **Podcast**: "Grupo de Inversión" (Alejandro Estebaranz)
- **Blog**: Value School

---

*Generado: 2026-02-06*
*Sindicato V8 Elite+ - Alpha Agent & Screener Guide*
