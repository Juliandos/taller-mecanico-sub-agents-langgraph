# Flujo: Rama Diagnóstico

## 1. De dónde viene todo: `langchain_core`

Antes de ver los nodos, hay que entender la base sobre la que está construido el agente.

### `langchain_core/agents.py`

Este archivo define los **contratos base** del sistema de agentes: qué es una acción, qué es un resultado, cómo se serializan. Las clases clave son:

```
AgentAction     → "el LLM decidió llamar a esta herramienta con este input"
AgentFinish     → "el LLM decidió terminar y devolver este resultado"
AgentStep       → acción + observación (lo que devolvió la herramienta)
```

Estas clases existen para compatibilidad con el paradigma antiguo (ReAct clásico). En LangGraph, **no usamos estas clases directamente** — en su lugar, usamos `StateGraph` con un `TypedDict` como estado. Pero las librerías internas de LangChain las usan internamente al gestionar mensajes y herramientas.

---

## 2. Cómo LangGraph reemplaza el paradigma antiguo

### El modelo antiguo (LangChain clásico)
```
LLM → AgentAction → Tool → Observation → LLM → AgentFinish
```
El LLM controla el loop y decide cuándo parar.

### El modelo nuevo (LangGraph)
```
StateGraph + Nodos + Edges condicionales
```
El **grafo** controla el loop. Cada nodo recibe el estado completo, hace su trabajo, y devuelve solo los cambios. El grafo decide qué nodo viene después según las funciones de routing.

---

## 3. El Estado compartido: `TallerState`

```python
# src/agents/taller/state.py

class TallerState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]  # se acumulan
    customer_name: str
    initial_symptom: str
    diagnostico_decision: str   # "buscar_info" | "generar_resumen"
    diagnostico_summary: str
    rag_calls: int
    # ... otros campos de agendamiento
```

`Annotated[list, operator.add]` significa que cuando dos nodos escriben en `messages`,
LangGraph **suma** las listas en lugar de sobreescribir. Todos los demás campos se sobreescriben con el valor más reciente.

---

## 4. El Grafo principal: `agent.py`

```python
builder = StateGraph(TallerState)

# Nodos registrados
builder.add_node("orquestador", orquestador)
builder.add_node("generador_conversacion", generador_conversacion)
builder.add_node("evaluador_pieza_dañada", evaluador_pieza_dañada)
builder.add_node("buscar_rag_mecanica", buscar_rag_mecanica)
builder.add_node("generar_resumen_diagnostico", generar_resumen_diagnostico)
builder.add_node("agregador", agregador)

# Edges
builder.add_edge(START, "orquestador")

builder.add_conditional_edges(
    "orquestador",
    route_orchestrator,
    {
        "rama_diagnostico": "generador_conversacion",
        "rama_agendamiento": "agent_booking",
    }
)
```

Cada `add_node` registra una función Python como nodo. Cada `add_edge` define por dónde fluye el estado.

---

## 5. Nodo 1: `orquestador`

**Archivo:** `src/agents/taller/nodes/orquestador/node.py`

**Qué hace:** Lee el último mensaje del cliente y decide a qué rama ir.

```
Input:  state["messages"][-1] → "mi motor vibra mucho"
Output: state["active_branches"] → ["rama_diagnostico"]
        route_orchestrator() → devuelve "rama_diagnostico"
```

**Palabras clave que detecta:**
- Síntomas → `["problema", "falla", "vibra", "ruido", "humo", "pierde"]` → rama_diagnostico
- Citas    → `["cita", "agendar", "reservar", "quiero ir"]` → rama_agendamiento
- Ambas   → ejecución paralela

---

## 6. Nodo 2: `generador_conversacion`

**Archivo:** `src/agents/taller/nodes/rama_diagnostico/node.py`

**Qué hace:** Responde de forma empática al cliente y hace preguntas de diagnóstico.

```
Input:  state["messages"] → [HumanMessage("mi motor vibra")]
Output: state["messages"] += [AIMessage("Entiendo tu problema...")]
```

**Posición en el grafo:**
```
orquestador → generador_conversacion → evaluador_pieza_dañada
```

Es el primer nodo de la rama. Su única función es generar una respuesta conversacional que invite al cliente a dar más detalles. No toma decisiones de routing.

---

## 7. Nodo 3: `evaluador_pieza_dañada` (Evaluator-Optimizer loop)

**Archivo:** `src/agents/taller/nodes/rama_diagnostico/node.py`

**Qué hace:** Decide si tiene suficiente información para diagnosticar o si necesita buscar en los manuales.

```
Input:  state["messages"], state["rag_calls"]
Output: state["diagnostico_decision"] → "buscar_info" | "generar_resumen"
        state["rag_calls"] += 1 si decide buscar
```

**Lógica de decisión:**
```python
if len(mensajes_del_cliente) >= 2 or rag_calls >= 1:
    decision = "generar_resumen"   # tiene suficiente info
else:
    decision = "buscar_info"       # necesita los manuales
```

**Routing posterior (`route_diagnostico`):**
```python
def route_diagnostico(state) -> str:
    if state["diagnostico_decision"] == "buscar_info":
        return "buscar_rag_mecanica"    # va a buscar
    return "generar_resumen_diagnostico" # ya tiene info
```

**Por qué existe este loop:**
```
generador_conversacion
        ↓
evaluador_pieza_dañada ──buscar_info──→ buscar_rag_mecanica
        ↑                                        │
        └────────────────────────────────────────┘
        (buscar_rag devuelve al evaluador con nueva info)
        ↓
generar_resumen_diagnostico
```

Esto es el patrón **Evaluator-Optimizer**: el evaluador itera hasta tener suficiente contexto. El límite actual es `rag_calls >= 1` (una búsqueda máxima).

---

## 8. Nodo 4: `buscar_rag_mecanica`

**Archivo:** `src/agents/taller/nodes/rama_diagnostico/node.py`
**Módulo RAG:** `src/agents/taller/rag/retriever.py`

**Qué hace:** Busca en pgvector los fragmentos de manuales más similares al síntoma del cliente.

```
Input:  state["initial_symptom"] | state["messages"][-1 humano]
Output: state["messages"] += [AIMessage("[RAG] Información técnica...")]
```

**Internamente llama a:**
```python
# retriever.py
def get_retriever(k=3):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name="mecanica_docs",
        connection=DB_URI,
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})
```

**Cómo funciona la búsqueda semántica:**
1. El síntoma del cliente se convierte en un vector numérico (embedding) via OpenAI
2. pgvector busca los 3 vectores más cercanos por similitud coseno
3. Los chunks de texto asociados a esos vectores se devuelven como resultados
4. Los resultados se inyectan en `messages` para que el evaluador los use

**Tabla real de la DB:**
```
langchain_pg_embedding
├── uuid          (ID único)
├── collection_id (referencia a "mecanica_docs")
├── embedding     (vector float[1536] — dimensión de text-embedding-3-small)
├── document      (el chunk de texto original)
└── cmetadata     ({"source": "Manual-VIII.pdf", "tema": "..."})
```

---

## 9. Nodo 5: `generar_resumen_diagnostico`

**Archivo:** `src/agents/taller/nodes/rama_diagnostico/node.py`

**Qué hace:** Toma todo el contexto acumulado en `messages` (síntoma del cliente + resultados RAG) y genera el diagnóstico final.

```
Input:  state (todo el contexto acumulado)
Output: state["diagnostico_summary"] → texto del diagnóstico final
```

Actualmente está mockeado con un diagnóstico fijo. En FASE 3 este nodo llamará a un LLM real pasándole el contexto completo para generar un diagnóstico específico al síntoma.

---

## 10. Convergencia: `agregador`

Después de que termina la rama diagnóstico (y opcionalmente la rama agendamiento), ambas convergen en el `agregador`:

```
generar_resumen_diagnostico ──┐
                               ├─→ agregador → END
ejecutar_tool_booking    ──────┘
```

El `agregador` combina `diagnostico_summary` + `appointment_summary` en un mensaje final que recibe el cliente.

---

## Flujo completo de la rama diagnóstico (resumen visual)

```
Cliente: "mi motor vibra mucho al frenar"
         │
         ▼
    [ORQUESTADOR]
    Detecta: "vibra" → rama_diagnostico
         │
         ▼
    [GENERADOR_CONVERSACION]
    Respuesta: "Entiendo... ¿cuándo comenzó?"
    state.messages += [AIMessage]
         │
         ▼
    [EVALUADOR_PIEZA_DAÑADA]
    ¿Tengo suficiente info? NO → "buscar_info"
    state.diagnostico_decision = "buscar_info"
    state.rag_calls = 1
         │
         ▼
    [BUSCAR_RAG_MECANICA]
    Query: "mi motor vibra mucho al frenar"
    pgvector devuelve 3 chunks de manuales
    state.messages += [AIMessage("[RAG] vibración puede ser...")]
         │
         ▼
    [EVALUADOR_PIEZA_DAÑADA] (segunda iteración)
    ¿Tengo suficiente info? SÍ (rag_calls >= 1) → "generar_resumen"
         │
         ▼
    [GENERAR_RESUMEN_DIAGNOSTICO]
    state.diagnostico_summary = "DIAGNÓSTICO: Bujías y/o..."
         │
         ▼
    [AGREGADOR]
    Combina diagnóstico + cita (si aplica)
         │
         ▼
         END
```