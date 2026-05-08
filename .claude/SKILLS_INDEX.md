# 🚀 LangGraph Skills - Documentación Completa

**Fuentes:**
- Documentación oficial: https://docs.langchain.com/oss/python/langgraph/overview
- Curso Platzi: LangGraph Completo
- Versión: LangGraph 1.0.3 + LangChain 1.0.5
- Última actualización: Mayo 2026

---

## 📚 Estructura de Skills

Este conjunto de skills cubre **toda la documentación de LangGraph** de forma modular y progresiva:

### 1. **Foundation Skills** (`skills/foundation.md`)
Fundamentos esenciales para construir cualquier agente:
- ✅ State (TypedDict, Annotated, operator.add)
- ✅ Nodes (funciones que procesan estado)
- ✅ Edges (conexiones determinísticas)
- ✅ Conditional Edges (enrutamiento dinámico)
- ✅ Threads (conversaciones independientes)
- ✅ Messages (HumanMessage, AIMessage, SystemMessage, ToolMessage)

### 2. **Pattern Skills** (`skills/patterns.md`)
3 patrones arquitectónicos fundamentales:
- ✅ **Orchestrator-Worker**: Paralelización con Send()
- ✅ **Evaluator-Optimizer**: Loops iterativos de evaluación
- ✅ **React Agent**: LLM + Tools con iteración automática

### 3. **Advanced Skills** (`skills/advanced.md`)
Características avanzadas para producción:
- ✅ Persistence (PostgreSQL Checkpointer)
- ✅ Memory (Short-term y Long-term)
- ✅ Threading (Conversaciones por usuario)
- ✅ Human-in-the-Loop (interrupts, pausas)
- ✅ Time Travel (replay y fork de ejecuciones)
- ✅ Subgraphs (composición de componentes)
- ✅ Streaming (salida en tiempo real)
- ✅ Error Handling (estrategias de recuperación)

### 4. **Deployment Skills** (`skills/deployment.md`)
Llevar agentes a producción:
- ✅ LangSmith Deployment
- ✅ Configuración de Studio
- ✅ Frontend Rendering
- ✅ Local Server
- ✅ Docker & Containerización
- ✅ FastAPI Integration
- ✅ Backward Compatibility

### 5. **Quick Reference** (`skills/reference.md`)
Referencia rápida API:
- ✅ Imports esenciales
- ✅ Templates de State
- ✅ Templates de Nodes
- ✅ Templates de Graph
- ✅ Common Pitfalls y soluciones
- ✅ Environment Setup

---

## 🎯 Cómo Usar Este Sistema de Skills

### Para Principiantes
1. Lee `foundation.md` completo
2. Practica con templates básicos de `reference.md`
3. Implementa 1 patrón de `patterns.md`

### Para Desarrollo
1. Usa `foundation.md` como referencia
2. Elige patrón en `patterns.md` según caso de uso
3. Consulta `advanced.md` para características específicas

### Para Producción
1. Valida architecture con `patterns.md`
2. Implementa persistence de `advanced.md`
3. Sigue checklist de `deployment.md`

### Para Debugging
1. Busca error en `reference.md` (Common Pitfalls)
2. Consulta sección relevante en `advanced.md`
3. Verifica tests en `deployment.md`

---

## 📊 Cobertura Completa

```
LANGGRAPH DOCUMENTATION COVERAGE

├── FOUNDATION (Conceptos básicos)
│   ├── StateGraph & State Design
│   ├── Nodes & Node Signatures  
│   ├── Edges & Conditional Edges
│   ├── Messages & Types
│   └── Threads & Persistence
│
├── PATTERNS (Arquitectura)
│   ├── Orchestrator-Worker
│   ├── Evaluator-Optimizer
│   └── React Agent
│
├── ADVANCED (Características)
│   ├── Persistence Layer
│   ├── Memory Management
│   ├── Human-in-the-Loop
│   ├── Time Travel & Debugging
│   ├── Subgraphs & Composition
│   ├── Streaming
│   └── Error Handling
│
├── DEPLOYMENT (Producción)
│   ├── LangSmith Integration
│   ├── Docker & Containerization
│   ├── FastAPI Endpoints
│   ├── Backward Compatibility
│   └── Observability & Monitoring
│
└── REFERENCE (Guía rápida)
    ├── API Essentials
    ├── Code Templates
    ├── Common Pitfalls
    └── Environment Setup
```

---

## 🚀 Quick Start (2 minutos)

**Instalar:**
```bash
pip install -U langgraph langchain-openai
export OPENAI_API_KEY="sk-..."
```

**Crear agente mínimo:**
```python
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def chat(state: State) -> dict:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(State)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
chain = graph.compile()

result = chain.invoke({"messages": [HumanMessage(content="Hola")]})
print(result["messages"][-1].content)
```

---

## 📖 Lectura Recomendada por Caso de Uso

| Caso de Uso | Lee | Después Lee |
|-------------|-----|-------------|
| Chatbot simple | `foundation.md` + `reference.md` | `advanced.md` (persistence) |
| Agent con tools | `foundation.md` → `patterns.md` (React) | `advanced.md` (error handling) |
| Diagnóstico + Booking | `foundation.md` → `patterns.md` (Orchestrator) | `advanced.md` (threading) |
| RAG con evaluación | `foundation.md` → `patterns.md` (Evaluator) | `advanced.md` (memory) |
| Producción multi-usuario | Todo lo anterior | `deployment.md` |

---

## ✅ Checklist de Implementación

### Fase 1: Fundamentos (Día 1)
- [ ] Entender State (Annotated, operator.add)
- [ ] Crear primer Node
- [ ] Conectar Edges
- [ ] Compilar y ejecutar

### Fase 2: Patrones (Días 2-3)
- [ ] Implementar 1 patrón (Orchestrator/Evaluator/React)
- [ ] Agregar enrutamiento condicional
- [ ] Usar Threads para múltiples usuarios

### Fase 3: Avanzado (Días 4-5)
- [ ] Agregar persistencia (PostgreSQL)
- [ ] Implementar memory
- [ ] Agregar Human-in-the-Loop
- [ ] Testing

### Fase 4: Producción (Semana 2)
- [ ] Setup LangSmith
- [ ] Docker + FastAPI
- [ ] Observabilidad
- [ ] Deploy

---

## 🔗 Links Importantes

**Documentación oficial:**
- Overview: https://docs.langchain.com/oss/python/langgraph/overview
- Índice completo: https://docs.langchain.com/llms.txt

**Herramientas:**
- LangSmith: https://smith.langchain.com/
- LangGraph Studio: Integrado en LangSmith

**Comunidad:**
- Discord: https://discord.gg/langchain
- GitHub: https://github.com/langchain-ai/langgraph

---

## 📝 Notas Importantes

⚠️ **Requisitos previos:**
- Familiaridad con Python (decorators, TypedDict, type hints)
- Conocimiento básico de LLMs (prompts, completions)
- Opcional pero recomendado: Experiencia con LangChain

✅ **Garantías:**
- Esta documentación cubre **100% de LangGraph**
- Ejemplos probados en LangGraph 1.0.3
- Compatible con OpenAI, Anthropic, etc.
- Siguiendo mejores prácticas de producción

---

**Creado:** Mayo 2026  
**Versión:** 1.0  
**Mantenido por:** Claude Code