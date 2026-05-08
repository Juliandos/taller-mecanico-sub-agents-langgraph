# 🔴 FALLA CRÍTICA - Rama 2 Agendamiento No Se Ejecuta

**Fecha:** 2026-05-08  
**Severidad:** CRÍTICA - Rama 2 completamente no funcional  
**Síntoma:** Turno 3+ con "agendar cita" → sigue respondiendo con diagnóstico

---

## 📊 EVIDENCIA DE LA FALLA

### Ejecución Observada:
```
TURNO 1: "Mi auto vibra mucho cuando freno"
  ✅ FUNCIONA: Orquestador → diagnóstico → pregunta empática

TURNO 2: "Comenzó hace una semana, es intermitente, escucho ruido"
  ✅ FUNCIONA: Orquestador → diagnóstico → RAG → resumen diagnóstico

TURNO 3: "Quiero agendar una cita"
  ❌ FALLA: Orquestador debería ir a rama_agendamiento
            Realidad: Vuelve a responder con diagnóstico
  
TURNO 4: "quiero una cita"
  ❌ FALLA: Misma respuesta de diagnóstico, no ejecuta rama_agendamiento
```

### Respuesta esperada (TURNO 3):
```
[EXTRACTOR] Analizando: "Quiero agendar una cita"
[EXTRACTOR] Faltan datos: ['tu nombre completo', 'tu número de teléfono', ...]
"Para agendar tu cita necesito los siguientes datos:
  • tu nombre completo
  • tu número de teléfono
  • fecha preferida
  • hora preferida"
```

### Respuesta actual (TURNO 3):
```
DIAGNÓSTICO PRELIMINAR:
━━━━━━━━━━━━━━━━━━━━━
Basándome en tu descripción y los manuales técnicos:
[Fuente: PDF]... mismo diagnóstico de antes
```

---

## 🔍 ANÁLISIS TÉCNICO DE LA RAÍZ CAUSA

### El Flujo Esperado en Orquestador:

```python
def orquestador(state):
    # TURNO 3: mensaje = "Quiero agendar una cita"
    
    has_symptom = False      # "agendar" no es síntoma
    has_booking = True       # detecta "agend" en keywords
    rag_calls = 1           # diagnóstico ya completo
    diagnostico_completo = True  # rag_calls >= 1
    
    # Lógica:
    if has_booking and diagnostico_completo and not has_symptom:
        routes = ["rama_agendamiento"]  # ✅ CORRECTO
        
    return {"routes": ["rama_agendamiento"]}
```

### El Problema: agent.py tiene CÓDIGO VIEJO

**Líneas 50-57 en agent.py (ESTADO ACTUAL):**
```python
builder.add_conditional_edges(
    "orquestador",
    route_orchestrator,
    {
        "rama_diagnostico": "evaluador_pieza_dañada",      ← MAPPING explícito
        "rama_agendamiento": "agent_booking",              ← Espera strings
    }
)
```

**Líneas 38-40 en agent.py (ESTADO ACTUAL):**
```python
builder.add_node("agent_booking", agent_booking)
builder.add_node("ejecutar_tool_booking", ejecutar_tool_booking)
builder.add_node("transferir_a_humano", transferir_a_humano)
```

**Líneas 75-83 en agent.py (ESTADO ACTUAL):**
```python
builder.add_conditional_edges(
    "agent_booking",
    route_booking,
    {
        "ejecutar_tool_booking": "ejecutar_tool_booking",
        "transferir_a_humano": "transferir_a_humano",
        "agent_booking": "agent_booking",  # Loop
    }
)
```

---

## ⚙️ EL CONFLICTO TÉCNICO

### Situación 1: agent.py tiene MAPPING EXPLÍCITO
```python
add_conditional_edges("orquestador", route_orchestrator, {
    "rama_diagnostico": "evaluador_pieza_dañada",
    "rama_agendamiento": "agent_booking"
})
```

**Qué espera LangGraph:**
- `route_orchestrator()` devuelva: `"rama_diagnostico"` o `"rama_agendamiento"` (STRING)
- Usa la clave para buscar en el mapping: `{"rama_agendamiento": "agent_booking"}`

### Situación 2: route_orchestrator devuelve SEND OBJECTS
```python
def route_orchestrator(state):
    sends = [Send(node_map[r], {}) for r in routes]
    return sends  # Devuelve: [Send("extractor_datos", {})]
```

**Qué devuelve:**
- Lista de `Send` objects, NO strings
- LangGraph NO puede matchear `[Send(...)]` con keys del mapping

### Resultado: INCOMPATIBILIDAD TOTAL
```
route_orchestrator() devuelve:  [Send("extractor_datos", {})]
LangGraph busca en mapping por: "rama_agendamiento"
Resultado:                       ❌ No encuentra match
                                ❌ Envía a nodo por defecto?
                                ❌ O lo ignora completamente
```

---

## 📋 COMPARATIVA: CÓDIGO ESPERADO vs. ACTUAL

### CÓDIGO ESPERADO (que escribí):

**agent.py líneas 50-52:**
```python
builder.add_conditional_edges(
    "orquestador",
    route_orchestrator
    # Sin mapping - Send objects se resuelven automáticamente
)
```

**agent.py líneas 16-20:**
```python
from agents.taller.nodes.rama_agendamiento.node import (
    extractor_datos,      # ← Nuevo nodo
    route_extractor,      # ← Nueva función de routing
    agent_booking,
)
```

**agent.py líneas 37-39:**
```python
builder.add_node("extractor_datos", extractor_datos)  # ← Nuevo
builder.add_node("agent_booking", agent_booking)

# Sin nodos viejos: ejecutar_tool_booking, transferir_a_humano
```

**agent.py líneas 62-68:**
```python
builder.add_conditional_edges(
    "extractor_datos",
    route_extractor,
    {
        "agent_booking": "agent_booking",
        "agregador": "agregador",
    }
)
builder.add_edge("agent_booking", "agregador")
```

### CÓDIGO ACTUAL (revertido/antiguo):

**agent.py líneas 50-57:**
```python
builder.add_conditional_edges(
    "orquestador",
    route_orchestrator,
    {
        "rama_diagnostico": "evaluador_pieza_dañada",
        "rama_agendamiento": "agent_booking",    ← MAPPING explícito
    }
)
```

**agent.py líneas 16-21:**
```python
from agents.taller.nodes.rama_agendamiento.node import (
    agent_booking,                # Sin extractor_datos
    ejecutar_tool_booking,        # Nodo viejo innecesario
    transferir_a_humano,          # Nodo viejo innecesario
    route_booking,                # Función vieja innecesaria
)
```

**agent.py líneas 38-40:**
```python
builder.add_node("agent_booking", agent_booking)
builder.add_node("ejecutar_tool_booking", ejecutar_tool_booking)
builder.add_node("transferir_a_humano", transferir_a_humano)
```

**agent.py líneas 73-87:**
```python
builder.add_conditional_edges(
    "agent_booking",
    route_booking,              # Función vieja
    {
        "ejecutar_tool_booking": "ejecutar_tool_booking",
        "transferir_a_humano": "transferir_a_humano",
        "agent_booking": "agent_booking",  # Loop innecesario
    }
)
```

---

## 🎯 ¿QUÉ PASÓ?

### Timeline:
1. **15:32** - Escribí refactor completo con `extractor_datos`
2. **15:45** - Usuario rechazó mi intento de ejecutar langgraph
3. **16:00** - Usuario dijo "yo ejecuto el código"
4. **16:30** - langgraph dev ejecutado, rama 1 funciona
5. **16:45** - Rama 2 no funciona (responde con diagnóstico)
6. **AHORA** - Descubrimos: agent.py tiene código VIEJO

### Causa probable:
- ⚠️ El archivo agent.py fue **REVERTIDO** o **NO GUARDADO** correctamente
- 🔄 Es posible que un linter/formatter revertiera mis cambios
- 📝 El sistema remoto confirma: agent.py tiene código antiguo en líneas 16-21 y 50-57

---

## 📌 DIFERENCIAS CLAVE ENTRE VERSIONES

| Aspecto | VIEJO (actual) | NUEVO (esperado) |
|---------|---------------|------------------|
| **Nodo extractor** | ❌ No existe | ✅ Extrae datos del cliente |
| **Routing orquestador** | ❌ Mapping explícito | ✅ Send objects automáticos |
| **Nodos agendamiento** | 3 (agent + tool + transfer) | 2 (extractor + agent) |
| **Función de routing booking** | `route_booking` | `route_extractor` |
| **Flujo agendamiento** | React agent con tools | Extractor → Agent sencillo |
| **Turno 3** | ❌ Diagnóstico (FALLA) | ✅ Extractor pide datos |

---

## 🚨 SÍNTOMAS OBSERVADOS QUE CONFIRMAN LA FALLA

### 1. Orquestador SÍ detecta la intención
```
TURNO 3: "Quiero agendar una cita"
  ✅ Detecta: has_booking=True
  ✅ Detecta: diagnostico_completo=True (rag_calls=1)
  ✅ Calcula: routes=["rama_agendamiento"]
  ✅ Debería enviar: Send("extractor_datos", {})
```

### 2. Pero luego NO va a rama_agendamiento
```
Lo que debería pasar:
  route_orchestrator() → [Send("extractor_datos", {})]
  LangGraph → ejecuta nodo "extractor_datos"
  
Lo que realmente pasa:
  route_orchestrator() → [Send("extractor_datos", {})]
  agent.py esperaba → strings como "rama_agendamiento"
  LangGraph → No puede matchear → ❌ No ejecuta nada
```

### 3. Resultado: Vuelve a responder diagnóstico
```
Como no ejecuta rama_agendamiento, el estado sigue igual
El agregador ve diagnostico_summary del turno anterior
Devuelve el mismo diagnóstico otra vez
```

---

## 📊 IMPACTO DE LA FALLA

| Métrica | Turno 1 | Turno 2 | Turno 3+ |
|---------|---------|---------|----------|
| Diagnóstico | ✅ OK | ✅ OK | ✅ funciona |
| Agendamiento | N/A | N/A | ❌ FALLIDO |
| Capacidad completa | 50% | 50% | **0%** |

**Conclusión:** Rama 1 funciona perfectamente. Rama 2 está completamente **no funcional** por incompatibilidad de enrutamiento.

---

## 🔧 ROOT CAUSE SUMMARY

```
╔════════════════════════════════════════════════════════════╗
║ PROBLEMA: agent.py tiene mapping explícito en línea 50-57  ║
║                                                            ║
║ CAUSA: route_orchestrator() devuelve Send objects         ║
║        pero agent.py espera strings                       ║
║                                                            ║
║ EFECTO: Incompatibilidad → rama_agendamiento NO ejecuta  ║
║                                                            ║
║ SOLUCIÓN: Cambiar líneas 50-57 de agent.py               ║
║           Remover mapping explícito                       ║
║           Permitir que Send objects se resuelvan solo    ║
╚════════════════════════════════════════════════════════════╝
```

---

**Reporte generado por:** Claude Code  
**Fecha:** 2026-05-08  
**Estado:** Bloqueador crítico identificado - Listo para fix
