# 🚀 Deployment Skills - Llevar a Producción

**Despliega agentes LangGraph en producción de forma robusta**

---

## 1. LangSmith Integration (Observabilidad)

### Setup

```bash
pip install langsmith

export LANGSMITH_API_KEY="ls-..."
export LANGSMITH_TRACING=true
```

### Automático en el Código

```python
from dotenv import load_dotenv
load_dotenv()

# Ya está habilitado si las vars de entorno existen
# Todo invoke() será trackeado automáticamente

result = chain.invoke(
    {"messages": [HumanMessage(content="Hola")]},
    config={"configurable": {"thread_id": "user-123"}}
)
# Aparece en https://smith.langchain.com/ automáticamente
```

### Visualizar Traces

```python
# Ver en LangSmith UI
# - Cada invocación del grafo
# - Tokens usados
- Latencia
- Errores
- Estados intermedios
```

---

## 2. LangGraph Studio (Desarrollo Visual)

### Acceso
```
https://smith.langchain.com/studio
```

### Cómo Usar

1. **Crear desde langgraph.json**
```json
{
  "graphs": {
    "taller": {
      "path": "src.agents.taller.agent:agent",
      "runnable": true
    }
  }
}
```

2. **Ejecutar Localmente**
```bash
uv run langgraph dev
# Abre: https://smith.langchain.com/studio/?baseUrl=http://localhost:2024
```

3. **Visualizar Grafo**
- Nodos en colores
- Edges claramente marcados
- Condicionales visibles
- Loops evidentes

4. **Testear Interactivamente**
- Pasar inputs
- Ver ejecución paso a paso
- Inspeccionar estado
- Simular user input

---

## 3. FastAPI Integration

### Setup

```bash
pip install fastapi uvicorn python-multipart
```

### Implementación Mínima

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import json

app = FastAPI(title="Taller Mecánico Agent")

# Checkpointer para persistencia
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(os.getenv("DB_URI"))
chain = graph.compile(checkpointer=checkpointer)

@app.get("/")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: dict):
    """Chat simple con persistencia."""
    try:
        result = chain.invoke(
            {"messages": [HumanMessage(content=request["message"])]},
            config={"configurable": {"thread_id": session_id}}
        )
        
        return {
            "response": result["messages"][-1].content,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{session_id}/history")
async def get_history(session_id: str):
    """Obtener historial de sesión."""
    try:
        state = chain.get_state(
            config={"configurable": {"thread_id": session_id}}
        )
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": "human" if type(m).__name__ == "HumanMessage" else "ai",
                    "content": m.content
                }
                for m in state.values.get("messages", [])
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found")

@app.post("/chat/{session_id}/stream")
async def chat_stream(session_id: str, request: dict):
    """Chat con streaming."""
    async def generate():
        for chunk in chain.stream(
            {"messages": [HumanMessage(content=request["message"])]},
            config={"configurable": {"thread_id": session_id}}
        ):
            yield json.dumps(chunk) + "\n"
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Ejecutar

```bash
uv run fastapi dev src/api/main.py

# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 4. Docker Containerización

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar archivos
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY .env .env

# Instalar dependencias
RUN pip install uv && uv sync --frozen

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Ejecutar
CMD ["uv", "run", "fastapi", "dev", "src/api/main.py", "--host", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: langgraph
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_URI: "postgresql://postgres:postgres@db:5432/langgraph"
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      LANGSMITH_API_KEY: ${LANGSMITH_API_KEY}
    depends_on:
      db:
        condition: service_healthy

  langgraph-studio:
    image: langchain/langgraph-studio:latest
    ports:
      - "2024:2024"
    environment:
      LANGGRAPH_API_URL: "http://api:8000"
```

### Ejecutar

```bash
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

---

## 5. Environment Setup Producción

### .env Producción

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DB_URI=postgresql://user:pass@prod-db.example.com:5432/langgraph

# LangSmith
LANGSMITH_API_KEY=ls-...
LANGSMITH_TRACING=true

# Aplicación
DEBUG=false
WORKERS=4
```

### Variables Sensibles

```bash
# NO commitear a git
# Usar Azure Key Vault, AWS Secrets, etc.

# En producción:
export OPENAI_API_KEY="$(aws secretsmanager get-secret-value --secret-id openai-key --query SecretString --output text)"
```

---

## 6. Backward Compatibility

### Actualizar Grafo en Producción

```python
# v1.0 - Grafo original
def original_agent():
    graph = StateGraph(State)
    graph.add_node("chat", chat_node)
    # ...
    return graph.compile()

# v1.1 - Añade nuevo nodo SIN romper sesiones activas
def new_agent():
    graph = StateGraph(State)
    graph.add_node("chat", chat_node)
    graph.add_node("moderador", moderador_node)  # Nuevo
    graph.add_edge("chat", "moderador")  # Nuevo edge
    # ...
    return graph.compile()

# Las sesiones activas en v1.0 pueden continuar en v1.1
# sin reconstrucción
```

### Versionamiento de API

```python
@app.post("/v1/chat/{session_id}")
async def chat_v1(session_id: str, request: dict):
    # v1.0 - endpoint original
    return handle_chat_v1(session_id, request)

@app.post("/v2/chat/{session_id}")
async def chat_v2(session_id: str, request: dict):
    # v2.0 - endpoint mejorado
    return handle_chat_v2(session_id, request)

# Los clientes pueden migrar gradualmente
```

---

## 7. Monitoring & Observability

### Logs Estructurados

```python
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_invocation(session_id, input_data, output_data, duration):
    logger.info(json.dumps({
        "event": "agent_invocation",
        "session_id": session_id,
        "input": input_data,
        "output": output_data,
        "duration_ms": duration,
        "timestamp": datetime.now().isoformat()
    }))

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: dict):
    start = time.time()
    result = chain.invoke(...)
    duration = (time.time() - start) * 1000
    
    log_invocation(session_id, request, result, duration)
    return result
```

### Métricas

```python
from prometheus_client import Counter, Histogram

invocations = Counter("agent_invocations_total", "Total invocations")
latency = Histogram("agent_latency_seconds", "Invocation latency")

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: dict):
    with latency.time():
        result = chain.invoke(...)
    
    invocations.inc()
    return result

# Exposer métricas Prometheus
from prometheus_client import make_wsgi_app
from waitress import serve

metrics_app = make_wsgi_app()
```

### Alertas

```python
def alert_on_error(session_id, error):
    """Enviar alerta si hay error."""
    import requests
    
    # Slack
    requests.post(
        "https://hooks.slack.com/services/...",
        json={
            "text": f"Error en session {session_id}: {str(error)}"
        }
    )

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: dict):
    try:
        return chain.invoke(...)
    except Exception as e:
        alert_on_error(session_id, e)
        raise
```

---

## 8. Scaling & Load Balancing

### Horizontalmente

```bash
# Ejecutar múltiples instancias con gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 src.api.main:app

# Nginx load balancer
upstream api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://api;
    }
}
```

### Caché Distribuida

```python
from redis import Redis

redis = Redis(host='localhost', port=6379, decode_responses=True)

def cached_invoke(session_id, message):
    cache_key = f"agent:{session_id}:{message}"
    
    # Buscar en caché
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Si no está en caché, invocar
    result = chain.invoke(...)
    
    # Guardar en caché (TTL: 1 hora)
    redis.setex(cache_key, 3600, json.dumps(result))
    
    return result
```

---

## 9. Security

### API Key Protection

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: dict, api_key: str = Depends(verify_api_key)):
    return chain.invoke(...)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat/{session_id}")
@limiter.limit("5/minute")
async def chat(session_id: str, request: dict, request: Request):
    return chain.invoke(...)
```

---

## ✅ Deployment Checklist

- [ ] Environment variables configuradas
- [ ] PostgreSQL en producción
- [ ] LangSmith habilitado
- [ ] FastAPI API funcionando
- [ ] Docker image built y testeada
- [ ] Health checks en lugar
- [ ] Logs estructurados
- [ ] Monitoreo activo
- [ ] Backward compatibility
- [ ] Load balancer setup
- [ ] Security (API keys, rate limit)
- [ ] Documentación actualizada

---

## 🚢 Deployment Workflow

```bash
# 1. Test localmente
uv run pytest

# 2. Build Docker image
docker build -t taller-mecanico:v1.0 .

# 3. Push a registry
docker push registry.example.com/taller-mecanico:v1.0

# 4. Deploy con compose
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl http://api:8000/

# 6. Monitor
docker-compose logs -f api
```

---

**Documentación oficial:**  
https://smith.langchain.com/  
https://python.langchain.com/docs/deployment