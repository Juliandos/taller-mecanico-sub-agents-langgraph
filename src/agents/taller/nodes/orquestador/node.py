"""Nodo Orquestador - Evalúa intención y enruta a ramas"""

from agents.taller.state import TallerState
from langchain_core.messages import AIMessage


def orquestador(state: TallerState) -> dict:
    """
    Orquestador: Analiza el mensaje y decide a qué rama enviar.
    - Si habla de problemas/síntomas → RAMA 1 (Diagnóstico)
    - Si habla de agendar/cita → RAMA 2 (Agendamiento)
    - Pueden ser ambas
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    # Extrae content del último mensaje (maneja dicts, Message objects, y listas)
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        content = last_msg.get("content", "")
    else:
        content = last_msg.content if hasattr(last_msg, "content") else ""

    # Si content es lista, concatenar
    if isinstance(content, list):
        content = " ".join(str(c) if not isinstance(c, str) else c for c in content)

    last_message = str(content).lower()

    # Detectar intención (busca prefijos, no palabras exactas)
    symptom_keywords = ["problema", "falla", "vibra", "ruido", "no funciona", "síntoma", "daño", "issue"]
    booking_keywords = ["cita", "agend", "reserv", "appointment", "fecha", "hora", "booking"]

    has_symptom = any(kw in last_message for kw in symptom_keywords)
    has_booking = any(kw in last_message for kw in booking_keywords)

    print(f"[ORQUESTADOR] has_symptom={has_symptom}, has_booking={has_booking}")

    # Retornar decisión
    routes = []
    if has_symptom:
        routes.append("rama_diagnostico")
    if has_booking:
        routes.append("rama_agendamiento")
    if not routes:
        routes = ["rama_diagnostico"]  # default

    return {"routes": routes}


def route_orchestrator(state: TallerState) -> str:
    """
    Función de enrutamiento - Controla flujo según estado de diagnóstico.

    Flujo:
    1. Si diagnóstico NO completo → rama_diagnostico (recolectar info)
    2. Si cliente confirmó diagnóstico → rama_agendamiento (agendar cita)
    3. Si diagnóstico completo pero NO confirmado → rama_diagnostico (esperar confirmación)
    """
    diagnosis_complete = state.get("diagnosis_complete", False)
    client_confirmed = state.get("client_confirmed_diagnosis", False)
    damaged_part = state.get("damaged_part", "")

    print(f"\n[ROUTE ORCHESTRATOR] ══════════════════════════════")
    print(f"  - diagnosis_complete: {diagnosis_complete}")
    print(f"  - client_confirmed_diagnosis: {client_confirmed}")
    print(f"  - damaged_part: {damaged_part}")

    # Si cliente ya confirmó el diagnóstico → ir a agendamiento
    if client_confirmed:
        print(f"[ROUTE ORCHESTRATOR] ✅ RUTEANDO A: rama_agendamiento")
        return "rama_agendamiento"

    # Si no hay confirmación → seguir con diagnóstico
    print(f"[ROUTE ORCHESTRATOR] 📋 RUTEANDO A: rama_diagnostico")
    return "rama_diagnostico"
