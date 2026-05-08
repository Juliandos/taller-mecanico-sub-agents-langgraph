# 🔮 Advanced Skills - Características Avanzadas

**Domina características avanzadas de LangGraph para producción**

---

## 1. Persistence (PostgreSQL Checkpointer)

### Concepto
La **persistencia** permite que agentes sobrevivan a fallos y recuperen estado anterior.

### Instalación

```bash
pip install langgraph-checkpoint-postgres psycopg2-binary
```

### Implementación

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph

# Crear checkpointer
DB_URI = "postgresql://user:password@localhost:5432/langgraph"
checkpointer = PostgresSaver.from_conn_string(DB_URI)

# Compilar grafo con checkpointer
chain = graph.compile(checkpointer=checkpointer)

# Usar con thread_id
result = chain.invoke(
    {"messages": [HumanMessage(content="Hola")]},
    config={"configurable": {"thread_id": "user-123"}}
)

# Recuperar estado anterior
state = chain.get_state(config={"configurable": {"thread_id": "user-123"}})
print(state.values)  # Todos los mensajes anteriores
```

### Beneficios

| Beneficio | Antes | Después |
|-----------|-------|---------|
| **Crash** | Pierde todo | Recupera desde último checkpoint |
| **Escalabilidad** | En-memory solo | Múltiples procesos |
| **Debugging** | Sin historial | Acceso a todo el historial |
| **Auditoría** | Nada registrado | Todo persistido |

---

## 2. Memory (Memoria a Largo Plazo)

### Tipos de Memoria

```python
class AdvancedState(TypedDict):
    # MEMORIA DE TRABAJO (corto plazo)
    messages: Annotated[list, operator.add]
    current_task: str
    
    # MEMORIA PERSISTENTE (largo plazo)
    customer_name: str                  # Guardado siempre
    customer_history: str               # Resumen de interacciones
    preferences: dict                   # Preferencias del usuario
    
    # METADATA
    conversation_started: str           # Timestamp
    total_interactions: int
```

### Implementación: Resumen de Conversación

```python
def memory_summarizer(state: AdvancedState) -> dict:
    """Crea resumen de conversación para memoria a largo plazo."""
    from langchain_openai import ChatOpenAI
    
    messages = state.get("messages", [])
    customer_history = state.get("customer_history", "")
    
    if len(messages) < 5:
        return {}  # No es necesario resumir aún
    
    # Crear prompt para resumen
    summary_prompt = f"""
Resumen anterior:
{customer_history}

Nuevos mensajes:
{str(messages[-5:])}

Por favor, actualiza el resumen incluyendo:
- Problemas mencionados
- Soluciones propuestas
- Preferencias del cliente
"""
    
    llm = ChatOpenAI(model="gpt-4o")
    summary = llm.invoke(summary_prompt)
    
    return {"customer_history": summary.content}
```

### Guardar Preferencias

```python
def extract_preferences(state: AdvancedState) -> dict:
    """Extrae y guarda preferencias del usuario."""
    last_msg = state["messages"][-1].content
    
    # Detectar preferencias
    preferences = {
        "morning_person": "mañana" in last_msg.lower(),
        "quick_response": "rápido" in last_msg.lower(),
        "detailed": "detalles" in last_msg.lower(),
    }
    
    return {"preferences": preferences}
```

---

## 3. Threading (Concurrencia Multi-usuario)

### Gestión de Threads

```python
# Cada usuario = thread diferente
def handle_multiple_users():
    users = [
        {"id": "user-juan", "message": "Hola, soy Juan"},
        {"id": "user-maria", "message": "Hola, soy María"},
        {"id": "user-carlos", "message": "Hola, soy Carlos"},
    ]
    
    for user in users:
        result = chain.invoke(
            {"messages": [HumanMessage(content=user["message"])]},
            config={"configurable": {"thread_id": user["id"]}}
        )
        print(f"{user['id']}: {result['messages'][-1].content}")

# Cada usuario mantiene su propia conversación
# Sin interferencias entre threads
```

### Limpieza de Threads Antiguos

```python
from datetime import datetime, timedelta

def cleanup_old_threads(checkpointer, days=30):
    """Elimina threads no usados hace más de X días."""
    # Esto depende de tu BD específica
    # Ejemplo con PostgreSQL:
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Consultar y eliminar threads antiguos
    # (implementación específica de BD)
    pass
```

---

## 4. Human-in-the-Loop (Intervención Humana)

### Interrupts (Pausar Ejecución)

```python
from langgraph.types import interrupt

def booking_approval_node(state: AdvancedState) -> dict:
    """Pide aprobación humana antes de agendar."""
    appointment = state.get("appointment_summary", "")
    
    # Pausar y pedir confirmación
    decision = interrupt({
        "question": "¿Confirmas esta cita?",
        "appointment": appointment,
        "actions": ["confirm", "modify", "cancel"]
    })
    
    if decision == "confirm":
        return {"booking_approved": True}
    elif decision == "modify":
        return {"booking_approved": False, "needs_modification": True}
    else:
        return {"booking_approved": False, "booking_cancelled": True}

# Reanudar desde pausa:
# chain.invoke(
#     input,
#     config={
#         "configurable": {"thread_id": "user-123"},
#         "user_input": "confirm"  # Usuario elige opción
#     }
# )
```

### Human Nodes (Esperar Input Humano)

```python
def human_review_node(state: AdvancedState) -> dict:
    """Espera input humano para validar decisión."""
    
    # En una aplicación web/API:
    # Guardar en BD que necesita intervención humana
    # Retornar inmediatamente al usuario
    # Cuando humano responde, reanudar con su input
    
    return {
        "requires_human": True,
        "human_review_request": {
            "type": "approval",
            "message": "Por favor revisa el diagnóstico",
            "data": state.get("diagnostico_summary", "")
        }
    }
```

---

## 5. Time Travel (Replay y Fork)

### Concept
Poder volver a pasos anteriores y explorar rutas alternativas.

### Replay (Ejecutar de Nuevo)

```python
# Obtener checkpoint anterior
checkpoint = chain.get_state(
    config={"configurable": {"thread_id": "user-123"}},
    checkpoint_id="checkpoint_v1"  # ID específico
)

# Reanudar desde ese punto
result = chain.invoke(
    {"messages": checkpoint.values["messages"]},
    config={"configurable": {"thread_id": "user-123"}}
)
```

### Fork (Explorar Alternativa)

```python
# Crear nuevo thread desde checkpoint
new_thread_id = f"user-123-fork-{datetime.now().timestamp()}"

# Copiar estado
checkpoint = chain.get_state({"configurable": {"thread_id": "user-123"}})

# Modificar y continuar en nuevo thread
result = chain.invoke(
    {
        **checkpoint.values,
        "messages": checkpoint.values["messages"][:-1]  # Quitar último mensaje
    },
    config={"configurable": {"thread_id": new_thread_id}}
)
```

---

## 6. Subgraphs (Composición)

### Crear Subgrafo

```python
def create_diagnostic_subgraph():
    """Crea grafo independiente para diagnóstico."""
    sub_graph = StateGraph(DiagnosticState)
    
    sub_graph.add_node("evaluador", evaluador_node)
    sub_graph.add_node("rag_search", rag_search_node)
    sub_graph.add_node("generate_report", generate_report_node)
    
    sub_graph.add_edge(START, "evaluador")
    # ... rest of connections
    
    return sub_graph.compile()

# Usar subgrafo en grafo principal
main_graph.add_node("diagnostic_subgraph", create_diagnostic_subgraph())
```

### Pasar Estado Entre Grafos

```python
def invoke_subgraph(state: MainState) -> dict:
    """Invoca subgrafo con parte del estado."""
    diagnostic_graph = create_diagnostic_subgraph()
    
    subgraph_input = {
        "symptoms": state.get("symptoms", ""),
        "messages": state.get("messages", [])
    }
    
    result = diagnostic_graph.invoke(subgraph_input)
    
    return {
        "diagnostico_summary": result.get("diagnostico_summary", ""),
        "messages": state.get("messages", []) + result.get("messages", [])
    }
```

---

## 7. Streaming (Salida en Tiempo Real)

### Token-by-Token Streaming

```python
from langchain_openai import ChatOpenAI

def llm_node_with_streaming(state: State) -> dict:
    """LLM node que soporta streaming."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    messages = state.get("messages", [])
    
    # Para streaming en API
    return {"messages": [llm.invoke(messages)]}

# En FastAPI
@app.get("/chat/{session_id}/stream")
async def chat_stream(session_id: str, query: str):
    def generate():
        for event in chain.stream(
            {"messages": [HumanMessage(content=query)]},
            config={"configurable": {"thread_id": session_id}}
        ):
            yield json.dumps(event) + "\n"
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")
```

---

## 8. Error Handling (Estrategias)

### Errores Transitorios

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def llm_node_with_retry(state: State) -> dict:
    """Reintentar en caso de error de red."""
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

### Errores Recuperables

```python
def llm_node_with_fallback(state: State) -> dict:
    """Intentar parsear, si falla devolver error al usuario."""
    try:
        structured_llm = llm.with_structured_output(SomeSchema)
        result = structured_llm.invoke(state["messages"])
        return {"parsed_data": result}
    except Exception as e:
        # Pasar error al LLM para que lo interprete
        return {
            "messages": [AIMessage(
                content=f"No pude procesar tu solicitud: {str(e)}. ¿Puedes reformular?"
            )]
        }
```

### Errores Inesperados

```python
def safe_node(state: State) -> dict:
    """Dejar que errores inesperados burbujeen."""
    try:
        result = risky_operation(state)
        return result
    except ExpectedError as e:
        # Manejar error esperado
        return {"error_message": str(e)}
    except UnexpectedError:
        # Dejar burbujear para logging y alertas
        raise
```

---

## 9. Testing (Estrategias)

### Test de Nodo Aislado

```python
def test_extractor_node():
    """Test del nodo extractor."""
    from agents.taller.nodes.extractor import extractor_node
    
    test_state = {
        "messages": [HumanMessage(content="Hola, soy Juan, tel 300-123-4567")],
        "customer_name": "",
        "phone": ""
    }
    
    result = extractor_node(test_state)
    
    assert result.get("customer_name") == "Juan"
    assert result.get("phone") == "300-123-4567"
```

### Test de Grafo Completo

```python
def test_full_workflow():
    """Test del grafo completo."""
    result = chain.invoke(
        {"messages": [HumanMessage(content="Soy Juan, tengo un motor vibrante")]},
        config={"configurable": {"thread_id": "test-1"}}
    )
    
    assert "diagnostico_summary" in result or "appointment_summary" in result
    assert len(result["messages"]) > 1
```

### Test de Threading

```python
def test_thread_isolation():
    """Verifica que threads no interfieran."""
    result1 = chain.invoke(
        {"messages": [HumanMessage(content="Soy Juan")]},
        config={"configurable": {"thread_id": "user-1"}}
    )
    
    result2 = chain.invoke(
        {"messages": [HumanMessage(content="Soy María")]},
        config={"configurable": {"thread_id": "user-2"}}
    )
    
    # Verificar que cada uno recuerde su nombre
    assert "Juan" not in str(result2)
    assert "María" not in str(result1)
```

---

## ✅ Checklist Avanzado

- [ ] Sé cómo setup PostgreSQL Checkpointer
- [ ] Implementé memory a largo plazo
- [ ] Manejo múltiples usuarios con threads
- [ ] Agregué Human-in-the-Loop
- [ ] Entiendo Time Travel
- [ ] Creo Subgraphs
- [ ] Implementé Streaming
- [ ] Tengo estrategia de error handling
- [ ] Escribí tests

---

## 🔗 Próximo Paso

Una vez domines Advanced:
→ Avanza a **deployment.md** para poner en producción