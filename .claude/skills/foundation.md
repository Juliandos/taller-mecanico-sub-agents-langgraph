# 🏗️ Foundation Skills - Fundamentos de LangGraph

**Domina los conceptos básicos de LangGraph**

---

## 1. State (Estado Compartido)

### Concepto
El **State** es la memoria compartida que persiste entre nodos. Es un `TypedDict` que define todos los datos que tu agente maneja.

### ✅ Good Design

```python
from typing_extensions import TypedDict, Annotated
import operator

class TallerState(TypedDict):
    # Listas que acumulan (SIEMPRE con operator.add)
    messages: Annotated[list, operator.add]
    
    # Campos que se reemplazan
    customer_name: str
    phone: str
    symptoms: str
    
    # Contadores y flags
    rag_calls: int
    requires_human: bool
    
    # Resúmenes procesados
    diagnostico_summary: str
    appointment_summary: str
```

### ❌ Bad Design

```python
class BadState(TypedDict):
    # ❌ Sin operator.add: pierde mensajes anteriores
    messages: list
    
    # ❌ Pre-formateado: mezcla datos con formato
    full_prompt: str
    
    # ❌ Datos redundantes
    customer_name: str
    customer_name_lowercase: str
```

### Reglas de Oro

| Regla | ✅ Correcto | ❌ Incorrecto |
|-------|-----------|--------------|
| **Listas acumulativas** | `Annotated[list, operator.add]` | `list` |
| **Datos raw** | `symptoms: str` | `formatted_prompt: str` |
| **Sin redundancia** | Una fuente de verdad | Datos duplicados |
| **Type hints** | Todos los campos tipados | `dict` sin tipado |

### Ejemplo Real: Taller Mecánico

```python
class TallerMecanicoState(TypedDict):
    # Comunicación
    messages: Annotated[list, operator.add]           # Historial completo
    
    # Datos del cliente
    customer_name: str                                 # "Juan García"
    phone: str                                         # "300-123-4567"
    vehicle_info: str                                  # "Toyota Corolla 2019"
    
    # Síntomas y diagnóstico
    initial_symptom: str                               # "Motor vibra"
    rag_calls: int                                     # Contador de búsquedas
    diagnostico_summary: str                           # Resultado final
    
    # Agendamiento
    appointment_date: str                              # "2026-05-15"
    appointment_time: str                              # "10:00"
    appointment_summary: str                           # Confirmación
    
    # Flags de control
    booking_confirmed: bool                            # Cita confirmada?
    requires_human: bool                               # Necesita humano?
```

---

## 2. Nodes (Pasos de Ejecución)

### Concepto
Un **Node** es una función que:
1. Lee el estado
2. Procesa datos
3. Retorna cambios al estado

### Anatomía de un Node

```python
def my_node(state: TallerState) -> dict:
    """
    Descripción clara del qué hace este nodo.
    
    Inputs (del state):
    - messages: historial de conversación
    - customer_name: nombre extraído
    
    Outputs (retornados):
    - messages: añade respuesta del LLM
    """
    # 1. LEER del estado
    messages = state.get("messages", [])
    customer_name = state.get("customer_name", "")
    
    # 2. PROCESAR
    last_message = messages[-1].content if messages else ""
    result = process_data(last_message, customer_name)
    
    # 3. RETORNAR CAMBIOS (merge automático)
    return {
        "field_1": value_1,
        "field_2": value_2,
        # NO incluyas campos que no cambien
    }
```

### Tipos de Nodes

#### Extractor Node (Extrae datos estructurados)

```python
from langchain_core.messages import AIMessage
from pydantic import BaseModel

class CustomerInfo(BaseModel):
    name: str
    phone: str

def extractor_node(state: TallerState) -> dict:
    """Extrae info del cliente del mensaje."""
    messages = state.get("messages", [])
    if not messages:
        return {}
    
    last_msg = messages[-1].content
    
    # Extraer con LLM estructurado
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    structured_llm = llm.with_structured_output(CustomerInfo)
    
    try:
        info = structured_llm.invoke(last_msg)
        return {
            "customer_name": info.name or state.get("customer_name", ""),
            "phone": info.phone or state.get("phone", "")
        }
    except:
        return {}
```

#### LLM Node (Llama al modelo)

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

def llm_node(state: TallerState) -> dict:
    """Genera respuesta con LLM."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    messages = state.get("messages", [])
    
    response = llm.invoke(messages)
    
    return {"messages": [response]}
```

#### Tool Node (Ejecuta herramientas)

```python
from langchain_core.messages import ToolMessage

def tool_node(state: TallerState) -> dict:
    """Ejecuta tools solicitadas por el LLM."""
    last_message = state["messages"][-1]
    
    if not hasattr(last_message, "tool_calls"):
        return {}
    
    results = []
    for tool_call in last_message.tool_calls:
        # Buscar la herramienta
        tool = next((t for t in tools if t.name == tool_call["name"]), None)
        if not tool:
            continue
        
        # Ejecutar
        try:
            result = tool.invoke(tool_call["args"])
        except Exception as e:
            result = f"Error: {str(e)}"
        
        # Crear mensaje con resultado
        results.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"]
        ))
    
    return {"messages": results}
```

#### Evaluator Node (Decide si continuar o terminar)

```python
def evaluador_node(state: TallerState) -> dict:
    """Decide si hay suficiente información."""
    rag_calls = state.get("rag_calls", 0)
    
    # Lógica de decisión
    if rag_calls < 3:
        decision = "buscar_mas"
    else:
        decision = "generar_resumen"
    
    return {"evaluador_decision": decision}
```

#### Aggregator Node (Combina resultados)

```python
def aggregador_node(state: TallerState) -> dict:
    """Combina resultados de múltiples ramas."""
    diagnostico = state.get("diagnostico_summary", "")
    appointment = state.get("appointment_summary", "")
    
    final_response = "=== RESPUESTA FINAL ===\n"
    
    if diagnostico:
        final_response += f"\n🔧 Diagnóstico:\n{diagnostico}"
    
    if appointment:
        final_response += f"\n📅 Agendamiento:\n{appointment}"
    
    return {"messages": [AIMessage(content=final_response)]}
```

---

## 3. Edges (Conexiones)

### Concepto
Los **Edges** conectan nodos. Pueden ser:
- **Determinísticos**: siempre van al mismo nodo
- **Condicionales**: deciden dónde ir basado en estado

### Unconditional Edges

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(TallerState)

# Agregar nodos primero
graph.add_node("node_a", node_a_func)
graph.add_node("node_b", node_b_func)

# Conexión simple: A → B
graph.add_edge("node_a", "node_b")

# Inicio: START → A
graph.add_edge(START, "node_a")

# Final: B → END
graph.add_edge("node_b", END)
```

### Conditional Edges

```python
def router(state: TallerState) -> str:
    """Decide a qué nodo enviar."""
    intent = state.get("evaluador_decision", "default")
    
    if intent == "buscar_mas":
        return "buscar_rag"
    elif intent == "generar":
        return "generar_resumen"
    else:
        return "error_handler"

# Registrar enrutamiento condicional
graph.add_conditional_edges(
    "evaluador_node",  # De este nodo
    router,             # Usando esta función
    {                   # Hacia estos nodos posibles
        "buscar_rag": "buscar_rag",
        "generar_resumen": "generar_resumen",
        "error_handler": "error_handler"
    }
)
```

### Loops (Condicional que vuelve atrás)

```python
# Un evaluador decide si buscar más o terminar
# Si busca, vuelve al evaluador

graph.add_edge("buscar_rag", "evaluador_node")  # Loop!

graph.add_conditional_edges(
    "evaluador_node",
    router,
    {
        "buscar_rag": "buscar_rag",
        "fin": "generar_resumen"
    }
)
```

---

## 4. Conditional Edges

### Tipos de Condicionales

#### Tipo 1: Enrutamiento por Intent

```python
def route_by_intent(state: TallerState) -> str:
    """Decide ruta basado en intención del usuario."""
    last_msg = state["messages"][-1].content.lower()
    
    if "cita" in last_msg or "agendar" in last_msg:
        return "booking_agent"
    elif "diagnóstico" in last_msg or "problema" in last_msg:
        return "diagnostic_agent"
    else:
        return "general_chat"

graph.add_conditional_edges(
    "intent_classifier",
    route_by_intent,
    ["booking_agent", "diagnostic_agent", "general_chat"]
)
```

#### Tipo 2: Enrutamiento por Evaluación

```python
def route_by_evaluation(state: TallerState) -> str:
    """Decide basado en evaluación anterior."""
    decision = state.get("evaluador_decision", "default")
    
    if decision == "buscar":
        return "buscar_rag"
    return "generar_resumen"

graph.add_conditional_edges(
    "evaluador",
    route_by_evaluation,
    ["buscar_rag", "generar_resumen"]
)
```

#### Tipo 3: Enrutamiento por Tool Calls

```python
def route_by_tools(state: TallerState) -> str:
    """Decide si hay tool calls o no."""
    last_msg = state["messages"][-1]
    
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tool_executor"
    return END  # O siguiente nodo

graph.add_conditional_edges(
    "agent",
    route_by_tools,
    ["tool_executor", END]
)
```

---

## 5. Threads (Conversaciones Independientes)

### Concepto
Un **thread_id** = una conversación independiente con su propio estado.

### Uso Básico

```python
# Usuario 1
result1 = chain.invoke(
    {"messages": [HumanMessage(content="Hola, soy Juan")]},
    config={"configurable": {"thread_id": "user-juan-123"}}
)

# Usuario 2 (conversación diferente)
result2 = chain.invoke(
    {"messages": [HumanMessage(content="Hola, soy María")]},
    config={"configurable": {"thread_id": "user-maria-456"}}
)

# Usuario 1 continúa (recuerda que se llama Juan)
result3 = chain.invoke(
    {"messages": [HumanMessage(content="¿Cuál es mi nombre?")]},
    config={"configurable": {"thread_id": "user-juan-123"}}
)
# Respuesta: "Tu nombre es Juan" ✅
```

### Políticas de Threading

| Política | Caso de Uso | Implementación |
|----------|-----------|----------------|
| **1-a-1** | Un usuario, conversación permanente | `thread_id = user_id` |
| **Por sesión** | Sesiones temporales (chat web) | `thread_id = session_id` |
| **Por objetivo** | Reinicia cuando se resuelve | Cambiar `thread_id` |
| **Caducidad** | Thread expira tras X horas | Implementar limpieza |

---

## 6. Messages (Tipos de Mensajes)

### Tipos Disponibles

```python
from langchain_core.messages import (
    HumanMessage,      # Input del usuario
    AIMessage,         # Output del LLM
    SystemMessage,     # Instrucciones al LLM
    ToolMessage,       # Resultado de una tool
    BaseMessage        # Tipo base
)

# Crear mensajes
human = HumanMessage(content="¿Cuál es el clima?")
ai = AIMessage(content="El clima es soleado")
system = SystemMessage(content="Eres un asistente meteorológico")
tool = ToolMessage(
    content="Temperatura: 25°C",
    tool_call_id="call_123",
    name="get_weather"
)
```

### En el State

```python
class State(TypedDict):
    # Mensaje singular
    last_response: str
    
    # Historial de mensajes
    messages: Annotated[list, operator.add]  # Acumula
    conversation_history: Annotated[list, operator.add]

# Acceder
messages = state.get("messages", [])
last_message = messages[-1]
last_content = last_message.content
```

---

## ✅ Checklist de Fundamentos

- [ ] Entiendo TypedDict y Annotated[list, operator.add]
- [ ] Puedo crear un State con 5+ campos
- [ ] Puedo escribir un Node que lea y modifique estado
- [ ] Entiendo la diferencia entre add_edge y add_conditional_edges
- [ ] Sé cómo crear un router function
- [ ] Entiendo threads y thread_id
- [ ] Conozco los tipos de mensajes
- [ ] Puedo compilar un grafo simple

---

## 🔗 Próximo Paso

Una vez domines Foundation:
→ Avanza a **patterns.md** para aprender 3 patrones arquitectónicos