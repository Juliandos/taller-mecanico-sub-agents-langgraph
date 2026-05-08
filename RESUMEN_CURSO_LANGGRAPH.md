# 📚 RESUMEN COMPLETO: Curso LangGraph - Platzi

## 🎯 Propósito del Curso
Construir **agentes inteligentes y autónomos** con LangGraph que:
- Razonan y toman decisiones
- Se comunican con múltiples LLMs
- Usan herramientas (tools) y búsqueda (RAG)
- Se orquestan en paralelo o secuencial
- Persisten memoria de conversaciones

---

## 📖 ESTRUCTURA: 3 FASES

---

## ✅ FASE 1: FUNDAMENTOS (Clases 1-10)

### Clase 1-3: Intro, Messages, LLM Basics
**Notebooks:** `01-notebook.ipynb`, `02-simple.ipynb`, `03-messages.ipynb`

- Concepto de **MessagesState** (historial de conversación)
- Tipos de mensajes: HumanMessage, AIMessage, SystemMessage
- Flujo básico: Usuario → LLM → Respuesta

### Clase 4: LLM Invoke
**Notebook:** `04-llm.ipynb`

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o")
response = llm.invoke("Hola")
```

- Inicializar LLMs con `init_chat_model()`
- Invocar con `llm.invoke()`
- Soporta OpenAI, Anthropic, etc.

### Clase 5: Threads/State (Memoria)
**Concepto teórico**

```python
class State(MessagesState):
    customer_name: str
    phone: str
```

- **State**: Memoria compartida entre nodos
- **Threads**: Conversaciones independientes
- Cada usuario = thread diferente con su propio state

### Clase 6: Chaining
**Notebook:** `06-chaining.ipynb`

```python
response1 = llm.invoke(prompt1)
response2 = llm.invoke(response1)
```

- Encadenar respuestas de LLMs
- Pasar salida de un LLM a otro
- Flujos secuenciales

### Clase 7: Structured Output
**Notebook:** `07-structured-output.ipynb`

```python
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str

llm_structured = llm.with_structured_output(ContactInfo)
info = llm_structured.invoke(prompt)
```

- Extraer datos estructurados en JSON
- Validación con Pydantic
- Usado por: extractors, routers, evaluadores

### Clase 8: RAG (Retrieval-Augmented Generation)
**Notebook:** `05-rag.ipynb`

```python
file_search_tool = {
    "type": "file_search",
    "vector_store_ids": ["vs_12345..."]
}
llm = llm.bind_tools([file_search_tool])
```

- Consultar PDFs/documentos guardados
- OpenAI File Search (vector stores)
- Evitar alucinaciones con datos reales

### Clase 9: Prompting Avanzado
**Notebook:** `09-prompting.ipynb`

- System prompts claros con reglas explícitas
- Few-shot: Ejemplos en el prompt
- Context injection: Variables dinámicas
- Importancia de instrucciones claras

### Clase 10: Tools Concepto Base
**Notebook:** `10-tools.ipynb`

```python
from langchain_core.tools import tool

@tool("get_products")
def get_products(query: str) -> str:
    """Busca productos"""
    return results

llm_with_tools = llm.bind_tools([get_products, get_weather])
```

- Definir tools con `@tool` decorator
- Bindear tools al LLM: `bind_tools()`
- LLM detecta cuándo usar tools automáticamente

---

## ✅ FASE 2: MODULARIZACIÓN Y PATRONES (Clases 11-13)

### Clase 11: Modularización de Agentes
**Archivo:** `src/agents/support/`

```
support/
├── state.py              # TallerState: customer_name, phone, my_age
├── agent.py              # make_graph(config) → grafo compilado
├── nodes/
│   ├── extractor/        # node.py + prompt.py
│   ├── conversation/     # node.py + prompt.py + tools.py
│   └── booking/          # node.py + prompt.py + tools.py
└── routes/
    └── intent/           # route.py + prompt.py
```

**Patrón:**
- 1 archivo = 1 responsabilidad
- State centralizado
- Prompts declarativos
- Imports limpios

### Clase 12: Extractor Mejorado
**Archivo:** `src/agents/support/nodes/extractor/`

```python
# Ejecuta en CADA turno, no solo al inicio
# Solo actualiza si hay datos válidos (filtra "unknown", "none", etc)
# Valida información antes de guardar en state

if schema.name and schema.name.lower() not in ["unknown", "none"]:
    new_state["customer_name"] = schema.name
```

**Casos cubiertos:**
- Extractor confunde roles (extrae doctor en lugar de paciente) → se auto-corrige
- Extractor captura datos incluso si usuario pregunta sobre documentos primero
- Usuario puede actualizar datos: "Ahora me llamo X" → se actualiza

### Clase 13: Booking Agent (React Pattern)
**Archivo:** `src/agents/support/nodes/booking/`

```python
# Crear agente React con tools
agent = create_react_agent(
    model=llm,
    tools=[book_appointment, get_appointment_availability],
    system_prompt=PROMPT
)

# El agente itera hasta resolver el problema
agent.invoke({"messages": history})
```

**React Pattern:**
- LLM → Decide qué tool usar
- Ejecuta tool → Retorna resultado
- LLM → Interpreta resultado
- Repite hasta finalizar

---

## ✅ FASE 3: ROUTING, TOOLS AVANZADOS, ORQUESTACIÓN (Clases 14-19)

### Clase 14-15: Tools + APIs + Bind Tools
**Archivo:** `src/agents/react.py`

```python
@tool("get_weather")
def get_weather(city: str) -> str:
    # Llamar a API externa
    response = requests.get(f"https://api.openweather.com/data/2.5/weather?q={city}")
    return f"Clima en {city}: {response.json()['main']['temp']}°C"

tools = [get_products, get_weather]
llm_with_tools = llm.bind_tools(tools)
```

**Flujo:**
1. LLM analiza mensaje → Detecta que necesita tool
2. LLM decide qué tool + parámetros
3. App ejecuta tool → Obtiene resultado
4. LLM reformatea resultado → Respuesta al usuario

### Clase 16: Evaluador (Loop Iterativo)
**Archivo:** `src/agents/evaluator.py`

```python
# Generator → Evaluator → Route (condicional)
# Si no es "funny" → vuelve al generator
# Si es "funny" → END

def route_edge(state: State) -> Literal[END, "generator_node"]:
    if state.get("is_funny"):
        return END
    return "generator_node"  # Loop hasta mejorar
```

**Patrón:** 
- Generar contenido
- Evaluar calidad
- Si no cumple → regenerar
- Si cumple → finalizar

### Clase 17-18: Routing Condicional + Intent Route
**Archivo:** `src/agents/support/routes/intent/`

```python
# Router con structured output
class IntentDecision(BaseModel):
    step: Literal["conversation", "booking"]

# Decide dinámicamente dónde enviar el mensaje
if "cita" in mensaje.lower():
    return "booking"
else:
    return "conversation"
```

**Casos:**
- Usuario pregunta sobre documentos → conversation
- Usuario quiere agendar → booking
- Usuario tiene problema Y quiere cita → ambos

### Clase 19: Paralelización con Send()
**Archivo:** `src/agents/orchestrator.py`

```python
from langgraph.types import Send

def route_to_nodes(state: State) -> list[Send]:
    nodes = state.get("nodes_to_execute")
    # Ejecutar múltiples nodos SIMULTÁNEAMENTE
    return [Send(node, state) for node in nodes]

# START → orquestador → Send([node_1, node_2, node_3]) → agregador → END
```

**Ventaja:**
- `node_1`, `node_2`, `node_3` se ejecutan en paralelo
- Tiempo total = max(T1, T2, T3) en lugar de T1+T2+T3
- Agregador espera a todos y combina resultados

---

## 🏗️ ARQUITECTURAS IMPLEMENTADAS

### 1️⃣ Support Agent (Clases 11-18)
```
EXTRACTOR
    ↓
INTENT_ROUTER (condicional)
    ├─ CONVERSATION (RAG)
    └─ BOOKING (React)
        ↓
    END
```

**Archivos:** `src/agents/support/`

### 2️⃣ Evaluator Agent (Clase 16)
```
GENERATOR
    ↓
EVALUATOR
    ↓
ROUTER (condicional loop)
    ├─ si no cumple → vuelve a GENERATOR
    └─ si cumple → END
```

**Archivo:** `src/agents/evaluator.py`

### 3️⃣ Orchestrator Agent (Clase 19)
```
ORCHESTRATOR
    ↓
Send() paralelo:
    ├─ NODE_1
    ├─ NODE_2
    └─ NODE_3
        ↓
AGGREGATOR → END
```

**Archivo:** `src/agents/orchestrator.py`

### 4️⃣ React Agent (Clases 14-15)
```
AGENT (React Pattern)
    ├─ Tool Call 1
    ├─ Tool Call 2
    └─ Decisión iterativa
        ↓
    END
```

**Archivo:** `src/agents/react.py`

### 5️⃣ Code Review Agent (Clase 18)
```
PARALLEL:
    ├─ SECURITY_REVIEW
    └─ MAINTAINABILITY_REVIEW
        ↓
FINAL_REVIEW → END
```

**Archivo:** `src/agents/code_review.py`

---

## 💾 PERSISTENCIA Y MEMORIA

### Checkpointer (Clases 23-25)
```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(DB_URI)
agent.invoke(state, {"configurable": {"thread_id": "user-123"}})
```

**Beneficios:**
- Mismo `thread_id` = misma conversación (memoria)
- Diferente `thread_id` = nueva conversación (sin memoria)
- PostgreSQL persiste estado entre llamadas

### Políticas de Thread
- **1-a-1:** Un usuario = un thread permanente
- **Caducidad:** Thread expira tras 24h, se crea uno nuevo
- **Por objetivo:** Cuando se resuelve el problema, nuevo thread
- **Concurrencia:** Múltiples usuarios = múltiples threads independientes

---

## 🌐 API FASTAPI

### Clases 23-25: API y Deployment

**Endpoints:**
```bash
GET  /                           # Health check
POST /chat/{session_id}          # Chat simple
POST /chat/{session_id}/stream   # Chat con streaming
GET  /sessions/{session_id}/history  # Ver historial
```

**Flow:**
```
Cliente → FastAPI → make_graph(checkpointer) → LangGraph → PostgreSQL → Respuesta
```

**Características:**
- Checkpointer para memoria persistente
- Streaming para UX en tiempo real
- Historial de conversaciones guardado

---

## 📊 CONCEPTOS TRANSVERSALES

| Concepto | Qué es | Dónde se usa |
|----------|--------|-------------|
| **State** | Memoria compartida entre nodos | Todos los agentes |
| **Prompts** | Instrucciones claras para LLMs | Cada nodo |
| **Tools** | Funciones que LLM puede llamar | Evaluador, Agendador, React |
| **Structured Output** | JSON validado de LLMs | Extractor, Router, Evaluador |
| **Conditional Edges** | Ruteo dinámico | Router, Loop de Evaluador |
| **Send()** | Paralelización | Orchestrator |
| **Checkpointer** | Persistencia de estado | API + LangGraph Studio |
| **Threading** | Conversaciones independientes | Memoria por usuario |

---

## 🎓 SKILLS ADQUIRIDAS

✅ Diseñar estados compartidos  
✅ Crear nodos especializados  
✅ Escribir prompts efectivos  
✅ Implementar tools y conectar APIs  
✅ Usar RAG para consultar documentos  
✅ Rutear dinámicamente entre nodos  
✅ Paralelizar nodos  
✅ Crear loops iterativos  
✅ Persistir conversaciones  
✅ Exponer agentes vía FastAPI  
✅ Depurar con LangGraph Studio  

---

## 🚀 PROYECTO FINAL: Taller Mecánico

**Arquitectura:**
```
START
  ↓
EXTRACTOR (nombre, teléfono, vehículo)
  ↓
ORQUESTADOR
  ↓
Send() paralelo:
  ├─ EVALUADOR_PIEZA (React + RAG manuales)
  └─ AGENDADOR (React + tools citas)
      ↓
AGREGADOR
  ↓
END
```

**Tecnologías:**
- LangGraph para el grafo
- OpenAI GPT-4o como LLM
- PostgreSQL + pgvector para RAG
- FastAPI para exposición
- Docker para infraestructura

---

## 📚 NOTEBOOKS PRINCIPALES

1. **01-notebook.ipynb** → Intro a LangGraph
2. **02-simple.ipynb** → State básico
3. **03-messages.ipynb** → Tipos de mensajes
4. **04-llm.ipynb** → Invocar LLMs
5. **05-rag.ipynb** → File Search y RAG
6. **06-chaining.ipynb** → Encadenamiento
7. **07-structured-output.ipynb** → JSON validado
8. **09-prompting.ipynb** → Técnicas de prompting
9. **10-tools.ipynb** → Tools y APIs
10. **11-conditions.ipynb** → Conditional edges
11. **12-parallization.ipynb** → Send() y paralelización
12. **13-random.ipynb** → Casos adicionales

---

## 🎯 APRENDIZAJE CLAVE

**El verdadero poder de LangGraph:**
- No es un LLM, es un **framework para orquestar LLMs**
- Permite construir **workflows complejos y determinísticos**
- Proporciona **control total** sobre el flujo (dónde van los datos, cuándo)
- Persiste **estado** entre llamadas (memoria de conversación)
- Ejecuta **nodos en paralelo** para eficiencia
- Soporta **loops iterativos** (evaluar, regenerar, mejorar)

---

## 📌 PRÓXIMOS PASOS

1. **Expandir RAG:** Cargar más manuales técnicos
2. **Mejorar Tools:** Conectar a BD reales de repuestos y citas
3. **Multi-idioma:** Soportar español, inglés, portugués
4. **Analytics:** Registrar conversaciones para mejorar prompts
5. **Fine-tuning:** Entrenar modelos específicos para el dominio
6. **Monitoreo:** Agregar logs, métricas, alertas

---

**Creado:** Mayo 2026  
**Modelo:** LangGraph 1.0.3 + LangChain 1.0.5  
**Plataforma:** OpenAI GPT-4o + PostgreSQL + FastAPI
