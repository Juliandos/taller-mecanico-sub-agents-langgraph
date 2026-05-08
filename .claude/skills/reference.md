# 📖 Quick Reference - Guía Rápida

**Referencia rápida y templates listos para copiar**

---

## 🚀 Installation & Setup

```bash
# Instalación
pip install -U langgraph langchain-openai

# Verificación
python -c "import langgraph; print(langgraph.__version__)"

# Environment
export OPENAI_API_KEY="sk-..."
export LANGSMITH_API_KEY="ls-..."
export DB_URI="postgresql://user:pass@localhost:5432/langgraph"
```

---

## 📋 State Template

```python
from typing_extensions import TypedDict, Annotated
import operator

class AppState(TypedDict):
    # Mensajes (SIEMPRE con operator.add)
    messages: Annotated[list, operator.add]
    
    # Strings
    customer_name: str
    phone: str
    symptoms: str
    
    # Números
    rag_calls: int
    total_interactions: int
    
    # Booleanos
    booking_confirmed: bool
    requires_human: bool
    
    # Lists sin acumular
    tags: list  # Se reemplaza, no acumula
    
    # Dicts
    metadata: dict
```

---

## 🔧 Node Templates

### Simple Node
```python
def my_node(state: AppState) -> dict:
    """Descripción clara."""
    result = process(state.get("field", default))
    return {"field": result}
```

### LLM Node
```python
def llm_node(state: AppState) -> dict:
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    response = llm.invoke(state.get("messages", []))
    return {"messages": [response]}
```

### Tool Node
```python
def tool_node(state: AppState) -> dict:
    from langchain_core.messages import ToolMessage
    
    last_msg = state["messages"][-1]
    results = []
    
    for tool_call in getattr(last_msg, "tool_calls", []):
        tool = next((t for t in tools if t.name == tool_call["name"]), None)
        if tool:
            result = tool.invoke(tool_call["args"])
            results.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
            ))
    
    return {"messages": results}
```

### Evaluator Node
```python
def evaluador(state: AppState) -> dict:
    counter = state.get("counter", 0)
    decision = "continuar" if counter < 3 else "terminar"
    return {"evaluador_decision": decision}
```

### Router Function
```python
def router(state: AppState) -> str:
    decision = state.get("some_decision", "default")
    if decision == "option_a":
        return "node_a"
    return "node_b"
```

---

## 📊 Graph Templates

### Minimal Graph
```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(AppState)
graph.add_node("node_a", node_a_func)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", END)

chain = graph.compile()
result = chain.invoke({"messages": [HumanMessage(content="...")]})
```

### Graph with Conditional
```python
graph.add_node("router", router_node)
graph.add_node("option_a", option_a_func)
graph.add_node("option_b", option_b_func)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    router_func,
    ["option_a", "option_b"]
)
graph.add_edge(["option_a", "option_b"], END)
```

### Graph with Loop
```python
graph.add_edge("evaluador", "executor")
graph.add_edge("executor", "evaluador")  # Loop!

graph.add_conditional_edges(
    "evaluador",
    lambda s: "executor" if s.get("continue") else "finalizer",
    ["executor", "finalizer"]
)
```

### Graph with Parallel (Send)
```python
from langgraph.types import Send

def orchestrator(state: AppState) -> list[Send]:
    return [
        Send("worker_1", state),
        Send("worker_2", state),
    ]

graph.add_edge(START, "orchestrator")
graph.add_edge("orchestrator", ["worker_1", "worker_2"])
graph.add_edge(["worker_1", "worker_2"], "aggregator")
graph.add_edge("aggregator", END)
```

---

## 🛠️ Common Tools Pattern

```python
from langchain_core.tools import tool

@tool("tool_name")
def my_tool(param1: str, param2: int = 10) -> str:
    """Descripción de qué hace."""
    # Implementación
    return "resultado"

# Bind to LLM
tools = [my_tool, another_tool]
llm_with_tools = llm.bind_tools(tools)

# Use in agent
response = llm_with_tools.invoke(messages)

# Check if has tool calls
if hasattr(response, "tool_calls"):
    for tool_call in response.tool_calls:
        # Execute tool
        pass
```

---

## 💾 Persistence Template

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Setup
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/db"
)

# Compile with persistence
chain = graph.compile(checkpointer=checkpointer)

# Use with thread_id
result = chain.invoke(
    {"messages": [HumanMessage(content="hello")]},
    config={"configurable": {"thread_id": "user-123"}}
)

# Recover state
state = chain.get_state({"configurable": {"thread_id": "user-123"}})
print(state.values)
```

---

## 🧠 Memory Template

```python
def memory_node(state: AppState) -> dict:
    """Actualiza memoria a largo plazo."""
    customer_history = state.get("customer_history", "")
    messages = state.get("messages", [])
    
    # Crear resumen
    if len(messages) > 5:
        # LLM summarization
        summary = llm.invoke(f"Resume: {messages}")
        return {"customer_history": summary.content}
    
    return {}
```

---

## 🌐 FastAPI Template

```python
from fastapi import FastAPI
from langchain_core.messages import HumanMessage

app = FastAPI()

@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: dict):
    result = chain.invoke(
        {"messages": [HumanMessage(content=request["message"])]},
        config={"configurable": {"thread_id": session_id}}
    )
    return {"response": result["messages"][-1].content}

@app.get("/history/{session_id}")
async def history(session_id: str):
    state = chain.get_state({"configurable": {"thread_id": session_id}})
    return {"messages": state.values.get("messages", [])}
```

---

## 🐳 Docker Template

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -U langgraph langchain-openai
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV DB_URI=$DB_URI
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## ⚠️ Common Pitfalls & Solutions

### Problem 1: Messages Disappear
```python
# ❌ WRONG
class State(TypedDict):
    messages: list  # Lose previous messages!

# ✅ CORRECT
class State(TypedDict):
    messages: Annotated[list, operator.add]  # Accumulate!
```

### Problem 2: Agent Forgets
```python
# ❌ WRONG
chain.invoke(input)  # No thread_id = new conversation

# ✅ CORRECT
chain.invoke(
    input,
    config={"configurable": {"thread_id": "user-123"}}
)  # Same thread = remembers!
```

### Problem 3: Can't Invoke Graph
```python
# ❌ WRONG
graph.invoke(input)  # graph has no invoke method

# ✅ CORRECT
chain = graph.compile()
chain.invoke(input)  # compiled chain has invoke
```

### Problem 4: Tools Not Called
```python
# ❌ WRONG
llm = ChatOpenAI()
response = llm.invoke(messages)  # LLM doesn't know about tools

# ✅ CORRECT
llm_with_tools = llm.bind_tools(tools)
response = llm_with_tools.invoke(messages)  # Now LLM can use tools
```

### Problem 5: Import Circular
```python
# ❌ WRONG
class State(TypedDict):
    field: "SomeClass"  # Forward reference as string fails

# ✅ CORRECT
from __future__ import annotations
class State(TypedDict):
    field: SomeClass  # Now works!
```

### Problem 6: Tool Not Executed
```python
# ❌ WRONG
if last_message.tool_calls:  # May not exist
    for tc in last_message.tool_calls:
        pass

# ✅ CORRECT
if hasattr(last_message, "tool_calls") and last_message.tool_calls:
    for tc in last_message.tool_calls:
        pass
```

---

## 🔍 Debugging Checklist

| Issue | Check |
|-------|-------|
| Graph won't compile | `graph.compile()` → check syntax |
| Node not executing | Check `add_node()` call |
| Edge not found | Check node names match exactly |
| State not updating | Return `dict` from node |
| Conditional not working | Check router return values |
| Tools not called | Use `bind_tools()` |
| Memory not persistent | Add checkpointer to `compile()` |
| Threads mixing | Check thread_id is unique |

---

## 📊 Visualization

```python
# ASCII Mermaid
print(chain.get_graph().draw_ascii())

# Mermaid markdown
print(chain.get_graph().draw_mermaid())

# PNG (requires graphviz)
chain.get_graph().draw_mermaid_png(output_file_path="graph.png")
```

---

## 🧪 Testing Template

```python
import pytest

def test_node_isolated():
    """Test single node."""
    state = {"messages": [HumanMessage(content="test")]}
    result = my_node(state)
    assert "field" in result

def test_graph_simple():
    """Test full graph."""
    result = chain.invoke({"messages": [HumanMessage(content="hello")]})
    assert len(result["messages"]) > 1

def test_thread_isolation():
    """Test threads don't mix."""
    result1 = chain.invoke(
        {"messages": [HumanMessage(content="user 1")]},
        config={"configurable": {"thread_id": "t1"}}
    )
    result2 = chain.invoke(
        {"messages": [HumanMessage(content="user 2")]},
        config={"configurable": {"thread_id": "t2"}}
    )
    assert result1 != result2
```

---

## 📚 Message Types

```python
from langchain_core.messages import (
    HumanMessage,      # User input
    AIMessage,         # LLM response
    SystemMessage,     # Instructions
    ToolMessage,       # Tool result
)

# Create
human = HumanMessage(content="Hi")
ai = AIMessage(content="Hello!")
system = SystemMessage(content="You are helpful")
tool = ToolMessage(
    content="result",
    tool_call_id="id",
    name="tool_name"
)

# Access
print(human.content)
print(ai.tool_calls if hasattr(ai, "tool_calls") else "No tools")
```

---

## 🔗 Quick Links

- **Docs:** https://docs.langchain.com/oss/python/langgraph/overview
- **GitHub:** https://github.com/langchain-ai/langgraph
- **LangSmith:** https://smith.langchain.com/
- **Discord:** https://discord.gg/langchain

---

## ✅ Pre-Deployment Checklist

- [ ] All imports work: `python -c "from agents.taller.agent import agent"`
- [ ] Graph compiles: `chain = graph.compile()` (no error)
- [ ] Basic invoke works: `chain.invoke({"messages": [...]})`
- [ ] Thread_id works: Same thread remembers state
- [ ] Env vars set: `OPENAI_API_KEY`, `DB_URI`
- [ ] Tests pass: `pytest tests/`
- [ ] Docker builds: `docker build -t app .`
- [ ] API works: `curl http://localhost:8000/`

---

**Last Updated:** Mayo 2026  
**LangGraph Version:** 1.0.3+  
**Keep this open while coding!**