# Cambios Intentados - 15 de Mayo 2026

## Resumen Ejecutivo
Se implementaron dos fixes para mejorar el manejo de respuestas numeradas y agregar un paso de confirmación antes de agendar citas.

---

## Fix 1: Parsed de Respuestas Numeradas

**Archivo modificado:** `src/agents/taller/nodes/rama_diagnostico/react_agent.py`

**Cambios:**
- Agregué import `re` (regex)
- Creé función `_convert_numbered_response(text: str) -> str` que:
  - Detecta respuestas numeradas en múltiples formatos
  - Soporta: "1) si", "1 si", "1. si", y respuestas multilinea
  - Convierte a lenguaje natural antes de enviar al LLM
  - Agrega logs de debug `[DIAGNOSTICO] Convertida respuesta numerada:`
- Integré la función en `evaluador_pieza_dañada_v2()` 
  - Llama `_convert_numbered_response()` antes de invocar el LLM
  - Línea agregada: `last_human_msg = _convert_numbered_response(last_human_msg)`

---

## Fix 2: Paso de Confirmación Antes de Agendar

**Archivo nuevo creado:** `src/agents/taller/nodes/rama_agendamiento/confirmation_agent.py`

**Contenido:**
- Función `confirmation_agent(state: TallerState) -> dict`
  - Muestra resumen de datos recolectados (nombre, teléfono, fecha, hora, mecánico)
  - Pide confirmación explícita
  - Retorna `messages` con el resumen y `awaiting_confirmation: True`

- Función `route_confirmation(state: TallerState) -> str`
  - Detecta palabras de confirmación: "si", "ok", "confirmado", "adelante", "dale", "perfecto", "claro", etc.
  - Detecta palabras de corrección: "corrijo", "cambio", "modifico", "error", "espera", etc.
  - Retorna "booking_agent" si confirmó
  - Retorna "agregador" si necesita corregir

**Archivo modificado:** `src/agents/taller/agent.py`

**Cambios:**
1. Agregué import (línea 14):
   ```python
   from agents.taller.nodes.rama_agendamiento.confirmation_agent import confirmation_agent, route_confirmation
   ```

2. Agregué nodo (línea 33):
   ```python
   builder.add_node("confirmation_agent", confirmation_agent)
   ```

3. Actualicé edges (líneas 69-86):
   - Cambié el destino de validador_responder cuando ready_to_book=True
   - De: "booking_agent": "booking_agent"
   - A: "booking_agent": "confirmation_agent"
   - Agregué nuevo conditional edge para confirmation_agent
   - Rutas: "booking_agent" → booking si confirmó, "agregador" → volver a recolectar si necesita corregir

---

## Flujo Resultante

```
extractor_datos
    ↓
validador_responder
    ├─ Si faltan campos → agregador (espera más info)
    └─ Si todo presente → confirmation_agent (ready_to_book=True)
        ↓
    confirmation_agent (muestra resumen)
        ├─ Si usuario confirma → booking_agent
        └─ Si usuario quiere corregir → agregador (re-recolecta datos)
            ↓
        booking_agent (crea la cita)
            ↓
        agregador (consolidación final)
            ↓
        END
```

---

## Estado Técnico

- ✅ Sintaxis validada (AST parsing)
- ✅ Todos los imports correctos
- ✅ Graph compila sin errores
- ✅ langgraph dev corriendo sin problemas
- ✅ Código listo en repositorio

---

## Comportamiento Esperado (No Testeado Completamente)

1. **Respuestas numeradas:** "1) si 2) no 3) 4 meses" → se convierte a natural language
2. **Confirmación:** Después de recolectar todos los datos → mostrar resumen → pedir "si" o "corrijo"
3. **Correcciones:** Si dice "corrijo" → vuelve al agregador para re-introducir datos

---

## Archivos Afectados

1. `src/agents/taller/nodes/rama_diagnostico/react_agent.py` - MODIFICADO
2. `src/agents/taller/nodes/rama_agendamiento/confirmation_agent.py` - NUEVO
3. `src/agents/taller/agent.py` - MODIFICADO
