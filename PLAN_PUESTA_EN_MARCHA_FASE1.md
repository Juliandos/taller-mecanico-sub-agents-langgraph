# 🚀 PLAN PUESTA EN MARCHA - FASE 1

## Objetivo
**Validar el flujo del agente en LangGraph Studio**

Sin RAG, sin API, sin Docker.
Solo: Estado + Grafo + Nodes básicos.

---

## 📋 REQUISITOS PREVIOS

### En WSL (Ubuntu)
```bash
# Verificar que existen
uv --version              # uv 0.X.X
python3 --version        # Python 3.11+
git --version            # git X.X.X
```

### En Windows
```bash
# Solo copiar la carpeta del proyecto
# (Las tecnologías están en WSL)
```

---

## 📂 ESTRUCTURA CREADA

```
taller-mecanico-agent/
├── src/
│   ├── __init__.py
│   └── agents/
│       ├── __init__.py
│       └── taller/
│           ├── __init__.py
│           ├── state.py              ✅
│           ├── agent.py              ✅
│           └── nodes/
│               ├── orquestador/
│               │   ├── __init__.py
│               │   └── node.py       ✅
│               ├── rama_diagnostico/
│               │   ├── __init__.py
│               │   └── node.py       ✅
│               ├── rama_agendamiento/
│               │   ├── __init__.py
│               │   └── node.py       ✅
│               └── agregador/
│                   ├── __init__.py
│                   └── node.py       ✅
│
├── pyproject.toml       ✅
├── langgraph.json       ✅
├── .env                 ✅
└── PLAN_PUESTA_EN_MARCHA_FASE1.md (este archivo)
```

---

## ⚙️ PASOS PARA EJECUTAR FASE 1

### PASO 1: Preparar directorio en Windows

```bash
# En Windows PowerShell/CMD
cd C:\Users\ASUS\Desktop\rescate asus\Yo\Paginas Web\trabajo

# Crear estructura (si no existe)
mkdir taller-mecanico-agent-fase1
cd taller-mecanico-agent-fase1
```

### PASO 2: Copiar archivos FASE 1

Copia estos archivos que acabo de crear:
```
src/
├── __init__.py
└── agents/
    ├── __init__.py
    └── taller/
        ├── __init__.py
        ├── state.py
        ├── agent.py
        └── nodes/
            ├── orquestador/node.py
            ├── rama_diagnostico/node.py
            ├── rama_agendamiento/node.py
            └── agregador/node.py

pyproject.toml
langgraph.json
.env
```

### PASO 3: Entrar a WSL

```bash
# En Windows
wsl

# O si tienes una distro específica
wsl -d Ubuntu
```

### PASO 4: Navegar al proyecto en WSL

```bash
# Desde el prompt WSL
cd /mnt/c/Users/ASUS/Desktop/rescate\ asus/Yo/Paginas\ Web/trabajo/taller-mecanico-agent-fase1

# O crea un alias temporal
export PROJ=/mnt/c/Users/ASUS/Desktop/rescate\ asus/Yo/Paginas\ Web/trabajo/taller-mecanico-agent-fase1
cd $PROJ
```

### PASO 5: Instalar dependencias con uv

```bash
# Verificar uv
uv --version

# Sincronizar dependencias
uv sync

# Esto crea .venv/ y instala todo
```

### PASO 6: Actualizar .env

```bash
# Editar .env (en Windows o WSL)
nano .env

# O con vi/vim
vim .env

# Cambiar:
OPENAI_API_KEY=sk-proj-TU_API_KEY_AQUI
```

### PASO 7: Crear carpeta nodes/__init__.py

```bash
# En WSL
touch src/agents/taller/nodes/__init__.py
touch src/agents/taller/nodes/orquestador/__init__.py
touch src/agents/taller/nodes/rama_diagnostico/__init__.py
touch src/agents/taller/nodes/rama_agendamiento/__init__.py
touch src/agents/taller/nodes/agregador/__init__.py
```

### PASO 8: Probar import básico

```bash
# En WSL dentro del proyecto
uv run python -c "from src.agents.taller.agent import agent; print('✅ Import exitoso')"

# Debería retornar: ✅ Import exitoso
```

### PASO 9: Lanzar LangGraph Studio

```bash
# En WSL dentro del proyecto
uv run langgraph dev

# Debería mostrar:
# Ready!
# - API: http://localhost:2024
# - Docs: http://localhost:2024/docs
# - LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://localhost:2024
```

### PASO 10: Abrir LangGraph Studio

1. **Copiar el link de Studio** del paso anterior
2. **Abrir en navegador** (Chrome, Firefox, Edge)
3. **Seleccionar el grafo "taller"** en el dropdown
4. **Debería ver el diagrama** con todos los nodos conectados

---

## 🧪 PRUEBAS EN LANGGRAPH STUDIO

### Test 1: Solo Diagnóstico
```
Input: "Hola, mi auto vibra mucho al frenar"

Flujo esperado:
START → ORQUESTADOR (detecta symptom)
      → GENERADOR_CONVERSACION (respuesta empática)
      → EVALUADOR_PIEZA_DAÑADA (evalúa info)
      → GENERAR_RESUMEN_DIAGNOSTICO (crea diagnóstico)
      → AGREGADOR (prepara respuesta)
      → END

Output: Resumen con diagnóstico
```

### Test 2: Solo Agendamiento
```
Input: "Quiero agendar una cita para cambio de aceite. Soy Juan, 300-123-4567"

Flujo esperado:
START → ORQUESTADOR (detecta booking)
      → AGENT_BOOKING (recopila datos)
      → EJECUTAR_TOOL_BOOKING (agenda)
      → AGREGADOR (prepara confirmación)
      → END

Output: Confirmación de cita
```

### Test 3: Diagnóstico + Agendamiento (Paralelo)
```
Input: "Mi motor vibra y quiero agendar una cita para revisión. Soy María, 310-456-7890"

Flujo esperado:
START → ORQUESTADOR (detecta both)
      → RAMA_DIAGNOSTICO | RAMA_AGENDAMIENTO (paralelo)
      → GENERADOR_CONVERSACION / AGENT_BOOKING
      → ... (procesa ambas)
      → AGREGADOR (combina ambas respuestas)
      → END

Output: Diagnóstico + Confirmación de cita
```

---

## ✅ CHECKLIST FASE 1

- [ ] Archivos copiados en Windows
- [ ] En WSL, directorio correcto
- [ ] `uv sync` ejecutado sin errores
- [ ] `.env` actualizado con OpenAI API Key
- [ ] `__init__.py` en todas las carpetas nodes/
- [ ] Import test exitoso
- [ ] `uv run langgraph dev` ejecutado
- [ ] LangGraph Studio abierto
- [ ] Grafo visible en Studio
- [ ] Test 1 (Diagnóstico) funciona ✅
- [ ] Test 2 (Agendamiento) funciona ✅
- [ ] Test 3 (Paralelo) funciona ✅

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'src'"
```bash
# Solución: Asegúrate de estar en el directorio raíz
pwd  # Debería terminar en /taller-mecanico-agent-fase1

# O instala el paquete en desarrollo
uv pip install -e .
```

### Error: "OPENAI_API_KEY not found"
```bash
# Solución: Editar .env y agregar la key real
nano .env
# OPENAI_API_KEY=sk-proj-...real...
```

### Error: "langgraph dev not found"
```bash
# Solución: Reinstalar dependencias
uv sync
uv run langgraph dev
```

### LangGraph Studio no carga el grafo
```bash
# Solución: Verificar langgraph.json
cat langgraph.json
# Debe apuntar a: src.agents.taller.agent:agent

# Y ejecutar desde el directorio raíz
pwd  # Debe ser .../taller-mecanico-agent-fase1
```

---

## 📊 DIAGRAMA DEL FLUJO FASE 1

```
                    START
                      │
                      ▼
         ┌─────────────────────────┐
         │    ORQUESTADOR          │
         │ (Evalúa intención)      │
         └────────┬────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────────┐         ┌──────────────────┐
│RAMA 1:      │         │RAMA 2:           │
│DIAGNÓSTICO  │         │AGENDAMIENTO      │
│             │         │                  │
│┌───────────┐│         │┌────────────────┐│
││GENERADOR  ││         ││AGENT_BOOKING   ││
│└────┬──────┘│         │└────┬───────────┘│
│     │       │         │     │            │
│┌────▼──────┐│         │┌────▼───────────┐│
││EVALUADOR  ││◄────┐   ││EJECUTAR_TOOL   ││
│└────┬──────┘│     │   │└───────────────┬┘│
│     │       │     │   │ o TRANSFERIR   │
│ ┌───┴──┐    │     │   │                │
│ │BUSCAR│────┼─────┘   │                │
│ │ RAG  │    │         │                │
│ └──────┘    │         └────┬───────────┘
│     │       │              │
│┌────▼──────────┐            │
││GENERAR        │            │
││RESUMEN        │            │
│└────┬──────────┘            │
│     │                       │
└─────┴───────┬───────────────┘
              │
              ▼
      ┌──────────────┐
      │  AGREGADOR   │
      │(Combina)     │
      └──────┬───────┘
             │
             ▼
           END
```

---

## 🎯 SIGUIENTE PASO (Después de validar)

Cuando FASE 1 funcione correctamente:

**FASE 2:** Agregar RAG, API FastAPI y Docker

(El plan FASE 2 viene en PLAN_PUESTA_EN_MARCHA_FASE2.md)

---

**¿Preguntas o problemas?**
- Ejecuta con `-v` para verbosidad: `uv run langgraph dev -v`
- Chequea logs en `langgraph dev` output
- Todos los nodes tienen `print()` para debugging

¡Éxito! 🚀
