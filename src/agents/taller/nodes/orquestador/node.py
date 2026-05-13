"""Nodo Orquestador - Analiza intención y actualiza contadores"""

import re
from agents.taller.state import TallerState


def normalize_keywords(text: str, keywords: list) -> bool:
    """Busca palabras clave de forma robusta en un texto."""
    clean = re.sub(r'\s+', ' ', text.lower().strip())
    clean = re.sub(r'[.,!?;:\-—¿¡]', '', clean)
    return any(kw in clean for kw in keywords)


def _extract_content(content) -> str:
    """Extrae texto del contenido (maneja strings, listas, Message objects)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(c) if not isinstance(c, str) else c for c in content)
    if hasattr(content, 'content'):
        return _extract_content(content.content)
    return ""


def orquestador(state: TallerState) -> dict:
    """
    NODO: Analiza la intención del usuario y actualiza contadores.

    Detecta:
    - Si el usuario pide cita/agendamiento → incrementa booking_attempts
    - Si el usuario pide hablar con humano → incrementa human_requests

    Retorna dict con los contadores actualizados.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        content = last_msg.get("content", "")
    else:
        content = last_msg.content if hasattr(last_msg, "content") else ""

    if isinstance(content, list):
        content = " ".join(str(c) if not isinstance(c, str) else c for c in content)

    last_message = str(content).lower()
    result = {}

    # Palabras clave para solicitud de humano
    human_keywords = [
        "humano", "persona", "operador", "representante", "supervisor",
        "agente", "transferencia", "transferir", "hablar con humano",
        "hablar con una persona", "agente humano", "persona real",
        "quiero hablar con alguien", "quiero un humano", "hablar con soporte",
        "soporte humano", "atiendeme", "atiéndeme", "atienda",
        "asistente real", "no quiero hablar con bot", "call center",
        "centro de servicio", "servicio al cliente", "atención al cliente",
        "quiero ser transferido", "transferencia a humano",
    ]

    # Palabras clave para solicitud de cita
    booking_keywords = [
        "cita", "citas", "agendar", "agend", "agenda", "agendada",
        "reserva", "reserv", "reservación", "reservar",
        "appointment", "booking", "book", "schedule", "scheduled",
        "disponibilidad", "disponible", "horario", "horarios", "turno",
        "programar", "programación", "fecha", "hora",
        "necesito cita", "quiero cita", "dame cita",
    ]

    # Detectar y contar
    if normalize_keywords(last_message, human_keywords):
        human_requests = state.get("human_requests", 0) + 1
        result["human_requests"] = human_requests
        print(f"[ORQUESTADOR] 🤝 Solicitud de humano detectada (intento {human_requests})")

    if normalize_keywords(last_message, booking_keywords):
        booking_attempts = state.get("booking_attempts", 0) + 1
        result["booking_attempts"] = booking_attempts
        print(f"[ORQUESTADOR] 📅 Solicitud de cita detectada (intento {booking_attempts})")

    if result:
        print(f"[ORQUESTADOR] Contadores actualizados: {result}")
    return result


def route_orchestrator(state: TallerState) -> str:
    """
    FUNCIÓN DE ROUTEO: Lee el estado y decide la ruta.

    Retorna:
    - "handoff" si human_requests >= 2
    - "rama_agendamiento" si booking_attempts >= 2 sin diagnóstico
    - "rama_agendamiento" si diagnóstico confirmado
    - "rama_diagnostico" por defecto
    """
    diagnosis_complete = state.get("diagnosis_complete", False)
    client_confirmed = state.get("client_confirmed_diagnosis", False)
    booking_attempts = state.get("booking_attempts", 0)
    human_requests = state.get("human_requests", 0)
    damaged_part = state.get("damaged_part", "")

    print(f"\n[ROUTE_ORCHESTRATOR] ══════════════════════════════")
    print(f"  - diagnosis_complete: {diagnosis_complete}")
    print(f"  - client_confirmed_diagnosis: {client_confirmed}")
    print(f"  - booking_attempts: {booking_attempts}")
    print(f"  - human_requests: {human_requests}")
    print(f"  - damaged_part: {damaged_part}")

    # Si pide humano por segunda+ vez
    if human_requests >= 2:
        print(f"[ROUTE_ORCHESTRATOR] 🤝 RUTEANDO A: handoff (humano x{human_requests})")
        return "handoff"

    # Si diagnóstico confirmado
    if client_confirmed and diagnosis_complete:
        print(f"[ROUTE_ORCHESTRATOR] ✅ RUTEANDO A: rama_agendamiento (diagnóstico confirmado)")
        return "rama_agendamiento"

    # Si insiste en cita por segunda+ vez sin diagnóstico
    if booking_attempts >= 2 and not diagnosis_complete:
        print(f"[ROUTE_ORCHESTRATOR] 📅 RUTEANDO A: rama_agendamiento (insistencia x{booking_attempts})")
        return "rama_agendamiento"

    # Default: diagnóstico
    print(f"[ROUTE_ORCHESTRATOR] 📋 RUTEANDO A: rama_diagnostico")
    return "rama_diagnostico"
