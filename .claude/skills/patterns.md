# 🏛️ Pattern Skills - 3 Patrones Arquitectónicos

**Aprende los 3 patrones fundamentales de LangGraph**

---

## Pattern 1: Orchestrator-Worker (Paralelización)

### Cuándo Usar
- ✅ Múltiples tareas independientes
- ✅ Diagnóstico + Agendamiento paralelo
- ✅ Validaciones en paralelo
- ✅ Análisis múltiple de datos

### Problema que Resuelve
```
❌ Secuencial: START → TASK1 (2s) → TASK2 (3s) → END = 5 segundos
✅ Paralelo:   START → TASK1 + TASK2 en paralelo → END = 3 segundos (max)
```

### Implementación

```python
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END

# 1. ORQUESTADOR: Decide qué enviar
def orchestrator(state: State) -> list[Send]:
    """Envía tareas a múltiples workers en paralelo."""
    return [
        Send("worker_diagnostico", state),
        Send("worker_booking", state),
        Send("worker_inventory", state),
    ]

# 2. WORKERS: Procesan tareas independientes
def worker_diagnostico(state: State) -> dict:
    # Análisis de síntomas
    return {"diagnostico_summary": "..."}

def worker_booking(state: State) -> dict:
    # Agendamiento
    return {"appointment_summary": "..."}

def worker_inventory(state: State) -> dict:
    # Consulta de inventario
    return {"inventory_data": "..."}

# 3. AGGREGADOR: Combina resultados
def aggregador(state: State) -> dict:
    diagnostico = state.get("diagnostico_summary", "")
    appointment = state.get("appointment_summary", "")
    inventory = state.get("inventory_data", "")
    
    final_response = f"""
🔧 Diagnóstico: {diagnostico}
📅 Cita: {appointment}
📦 Inventario: {inventory}
"""
    return {"messages": [AIMessage(content=final_response)]}

# 4. CONECTAR GRAFO
graph = StateGraph(State)
graph.add_node("orchestrator", orchestrator)
graph.add_node("worker_diagnostico", worker_diagnostico)
graph.add_node("worker_booking", worker_booking)
graph.add_node("worker_inventory", worker_inventory)
graph.add_node("aggregador", aggregador)

# Conexiones
graph.add_edge(START, "orchestrator")

# Enviar a workers (PARALELO)
graph.add_edge("orchestrator", ["worker_diagnostico", "worker_booking", "worker_inventory"])

# Todos convergen al agregador
graph.add_edge("worker_diagnostico", "aggregador")
graph.add_edge("worker_booking", "aggregador")
graph.add_edge("worker_inventory", "aggregador")

graph.add_edge("aggregador", END)

chain = graph.compile()
```

### Diagrama

```
       ┌─────────────────┐
       │  ORCHESTRATOR   │
       └────────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌─────────┐ ┌────────┐ ┌──────────┐
│DIAGNOSTIC│ │BOOKING│ │INVENTORY│  (PARALELO)
└────┬────┘ └───┬────┘ └────┬─────┘
     │          │           │
     └──────────┼───────────┘
                │
                ▼
           ┌──────────┐
           │AGGREGADOR│
           └────┬─────┘
                │
                ▼
               END
```

### Caso Real: Taller Mecánico

```python
def orchestrator_taller(state: State) -> list[Send]:
    """Paralleliza diagnóstico y agendamiento."""
    return [
        Send("rama_diagnostico", state),
        Send("rama_agendamiento", state),
    ]

graph.add_edge(START, "orchestrator")
graph.add_edge("orchestrator", ["rama_diagnostico", "rama_agendamiento"])
graph.add_edge(["rama_diagnostico", "rama_agendamiento"], "agregador")
```

---

## Pattern 2: Evaluator-Optimizer (Loop Iterativo)

### Cuándo Usar
- ✅ RAG con evaluación de relevancia
- ✅ Generación de contenido con feedback
- ✅ Búsqueda iterativa hasta satisfacer criterio
- ✅ Validación multi-paso

### Problema que Resuelve
```
❌ Una sola búsqueda: Información insuficiente
✅ Búsqueda iterativa: "¿Tengo suficiente?" → Sí/No → Loop
```

### Implementación

```python
# 1. EVALUADOR: Decide si buscar más o terminar
def evaluador(state: State) -> dict:
    """Evalúa si hay suficiente información."""
    rag_calls = state.get("rag_calls", 0)
    last_result = state.get("last_rag_result", "")
    
    # Criterios de parada
    if rag_calls >= 3:
        decision = "terminar"
    elif "no encontrado" in last_result.lower():
        decision = "buscar"
    elif len(last_result) > 500:
        decision = "terminar"
    else:
        decision = "buscar"
    
    return {"evaluador_decision": decision}

# 2. BUSCADOR: Obtiene más información
def buscador_rag(state: State) -> dict:
    """Busca en manuales técnicos."""
    rag_calls = state.get("rag_calls", 0) + 1
    
    # Simulación de búsqueda RAG
    resultado = f"Resultado #{rag_calls}: información técnica..."
    
    return {
        "rag_calls": rag_calls,
        "last_rag_result": resultado,
    }

# 3. GENERADOR: Crea resultado final
def generador_resumen(state: State) -> dict:
    """Genera resumen después de evaluación."""
    rag_results = state.get("last_rag_result", "")
    
    resumen = f"DIAGNÓSTICO FINAL basado en: {rag_results}"
    
    return {
        "diagnostico_summary": resumen,
        "evaluador_decision": "terminado"
    }

# 4. ROUTER: Decide siguiente paso
def route_evaluador(state: State) -> str:
    """Enruta basado en decisión del evaluador."""
    decision = state.get("evaluador_decision", "terminar")
    
    if decision == "buscar":
        return "buscador_rag"
    return "generador_resumen"

# 5. CONECTAR GRAFO
graph = StateGraph(State)
graph.add_node("evaluador", evaluador)
graph.add_node("buscador_rag", buscador_rag)
graph.add_node("generador_resumen", generador_resumen)

graph.add_edge(START, "evaluador")

# Condicional: buscar o terminar
graph.add_conditional_edges(
    "evaluador",
    route_evaluador,
    ["buscador_rag", "generador_resumen"]
)

# Loop: si busca, vuelve al evaluador
graph.add_edge("buscador_rag", "evaluador")

# Final
graph.add_edge("generador_resumen", END)

chain = graph.compile()
```

### Diagrama

```
         ┌──────────┐
         │ EVALUADOR│◄──────────┐
         └────┬─────┘           │
              │                 │
        ┌─────┴──────┐          │
        │            │          │
        ▼            ▼          │
     BUSCAR ───────┐ GENERAR    │
        │          │             │
        └──────────┼──┼──────────┘
                   │  │ LOOP!
                   ▼  ▼
                  END
```

### Caso Real: RAG Manuales Técnicos

```python
def evaluador_manuales(state: State) -> dict:
    rag_calls = state.get("rag_calls", 0)
    if rag_calls < 2:
        decision = "buscar"
    else:
        decision = "fin"
    return {"evaluador_decision": decision}

graph.add_edge("buscador_rag", "evaluador")  # Loop!
```

---

## Pattern 3: React Agent (LLM + Tools Loop)

### Cuándo Usar
- ✅ Agentes que usan múltiples tools
- ✅ Agendamiento automático
- ✅ Consultas a APIs
- ✅ Búsqueda con herramientas

### Problema que Resuelve
```
❌ LLM solo: "Te agendar una cita" pero no la agenda
✅ React: LLM → elige tool → ejecuta → interpreta → repite
```

### Implementación

```python
from langchain_core.tools import tool

# 1. DEFINIR TOOLS
@tool("consultar_mecanicos")
def consultar_mecanicos(especialidad: str = "") -> str:
    """Consulta mecánicos disponibles."""
    return "Juan García (Motor), Pedro Martínez (Frenos)"

@tool("agendar_cita")
def agendar_cita(nombre: str, fecha: str, hora: str) -> str:
    """Agenda una cita."""
    return f"Cita confirmada: TM-{random.randint(10000,99999)}"

@tool("consultar_disponibilidad")
def consultar_disponibilidad(fecha: str) -> str:
    """Consulta horarios disponibles."""
    return "Horarios: 09:00, 10:00, 14:00, 15:00"

tools = [consultar_mecanicos, agendar_cita, consultar_disponibilidad]

# 2. AGENT NODE: LLM decide si usar tools
def agent_node(state: State) -> dict:
    """LLM call: decide si usar herramientas."""
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    llm_with_tools = llm.bind_tools(tools)
    
    messages = state.get("messages", [])
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

# 3. TOOL NODE: Ejecuta herramientas
def tool_node(state: State) -> dict:
    """Ejecuta las tools solicitadas por el LLM."""
    last_message = state["messages"][-1]
    
    if not hasattr(last_message, "tool_calls"):
        return {}
    
    results = []
    for tool_call in last_message.tool_calls:
        tool = next((t for t in tools if t.name == tool_call["name"]), None)
        if not tool:
            continue
        
        try:
            result = tool.invoke(tool_call["args"])
        except Exception as e:
            result = f"Error: {str(e)}"
        
        results.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"]
        ))
    
    return {"messages": results}

# 4. ROUTER: Decide si continuar loop
def should_continue(state: State) -> str:
    """¿Hay más tool_calls o terminó?"""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    return END

# 5. CONECTAR GRAFO
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "agent")

# Condicional: usar tool o terminar
graph.add_conditional_edges(
    "agent",
    should_continue,
    ["tool_node", END]
)

# Loop: tool result vuelve al agent
graph.add_edge("tool_node", "agent")

chain = graph.compile()
```

### Diagrama

```
         ┌───────┐
         │ AGENT │
         └───┬───┘
             │
      ┌──────┴──────┐
      │             │
    HAS TOOLS?     NO TOOLS
      │             │
      ▼             ▼
  ┌───────────┐    END
  │ TOOL_NODE │
  └─────┬─────┘
        │ (resultado)
        ▼
    AGENT ◄──── LOOP!
```

### Caso Real: Agendador de Citas

```python
@tool("listar_mecanicos")
def listar_mecanicos(especialidad: str) -> str:
    return "M001: Juan García, M002: Pedro Martínez"

@tool("confirmar_cita")
def confirmar_cita(mecanico_id: str, fecha: str, hora: str) -> str:
    return f"✅ Cita agendada: TM-{random.randint(10000,99999)}"

tools = [listar_mecanicos, consultar_disponibilidad, confirmar_cita]

# El agent automáticamente:
# 1. Lee solicitud del usuario
# 2. Pide lista de mecánicos
# 3. Consulta disponibilidad
# 4. Confirma cita
# 5. Responde al usuario
```

---

## Comparativa de Patrones

| Aspecto | Orchestrator | Evaluator | React |
|---------|-------------|-----------|-------|
| **Casos** | Tareas paralelas | Búsqueda iterativa | Tools dinámicos |
| **Complejidad** | Media | Baja | Alta |
| **Tiempo** | Paralelo (rápido) | Iterativo (medio) | Variable (lento) |
| **Determinístico** | Sí | Sí | No (LLM decide) |
| **Ejemplo** | Diag + Booking | RAG con eval | Agent con tools |

---

## Combinando Patrones

### Architec tura Completa: Taller Mecánico

```
START
  ↓
┌─────────────────────┐
│   ORCHESTRATOR      │
└────────┬────────────┘
         │
  ┌──────┴──────┐
  │             │
  ▼             ▼
RAMA_1:       RAMA_2:
EVALUATOR     REACT
  ↓             ↓
BUSCAR_RAG    AGENT+TOOLS
  ↓             ↓
RESUMEN       BOOKING
  │             │
  └──────┬──────┘
         ▼
    AGGREGADOR
         ↓
        END
```

---

## ✅ Checklist de Patrones

- [ ] Entiendo cuándo usar cada patrón
- [ ] Puedo implementar Orchestrator
- [ ] Puedo implementar Evaluator
- [ ] Puedo implementar React Agent
- [ ] Sé cómo combinar patrones
- [ ] Entiendo loops y condicionales
- [ ] Puedo crear tools con @tool

---

## 🔗 Próximo Paso

Una vez domines Patterns:
→ Avanza a **advanced.md** para características avanzadas