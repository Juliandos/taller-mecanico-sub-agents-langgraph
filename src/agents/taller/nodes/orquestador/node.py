"""Nodo Orquestador - Analiza intención y actualiza contadores"""

import re
from agents.taller.state import TallerState


def _normalize(t: str) -> str:
    """Limpia texto: minúsculas, sin puntuación, sin tildes."""
    t = t.lower().strip()
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'[.,!?;:\-—¿¡]', '', t)
    for src, dst in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ü','u'),('ñ','n')]:
        t = t.replace(src, dst)
    return t


def normalize_keywords(text: str, keywords: list) -> bool:
    """Busca palabras clave de forma robusta en un texto (ignora tildes y signos)."""
    clean = _normalize(text)
    return any(_normalize(kw) in clean for kw in keywords)


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

    faq_attempts es un flag POR TURNO (se resetea a 0 cada vez).
    booking_attempts y human_requests son acumulativos.
    """
    # faq_attempts siempre se resetea a 0 al inicio del turno
    new_state: TallerState = {"faq_attempts": 0}

    messages = state.get("messages", [])
    if not messages:
        return new_state

    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        content = last_msg.get("content", "")
    else:
        content = last_msg.content if hasattr(last_msg, "content") else ""

    if isinstance(content, list):
        content = " ".join(str(c) if not isinstance(c, str) else c for c in content)

    last_message = str(content).lower()

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
        "disponibilidad", "disponible", "turno",
        "programar", "programación",
        "necesito cita", "quiero cita", "dame cita",
    ]

    # Palabras clave para preguntas FAQ — formas interrogativas y términos específicos del taller.
    # La comparación ya es robusta (sin tildes ni signos) gracias a normalize_keywords.
    faq_keywords = [
        # Interrogativas
        "¿qué", "¿quién", "¿dónde", "¿cuándo", "¿cómo", "¿por qué", "¿cual", "¿cuál",
        "¿cuáles", "¿cuanto", "¿cuánto",
        # Datos del taller
        "horario", "horarios", "precio", "precios", "costo", "costos",
        "misión", "visión", "teléfono", "dirección", "garantía",
        "quiénes somos", "quiénes son", "cuándo abren", "cuándo cierran",
        "información del taller", "sobre el taller",
        # Preguntas sobre servicios / personal
        "qué servicios", "qué hacen", "qué ofrecen", "qué mecánicos",
        "que mecánicos", "que mecánico", "mecánicos tienen", "mecánico tienen",
        "qué procedimientos", "que procedimientos", "procedimientos especiales",
        "procedimiento especial", "especialidades", "especialidad",
    ]

    # Detectar y contar
    if normalize_keywords(last_message, human_keywords):
        human_requests = state.get("human_requests", 0) + 1
        new_state["human_requests"] = human_requests
        print(f"[ORQUESTADOR] 🤝 Solicitud de humano detectada (intento {human_requests})")

    if normalize_keywords(last_message, booking_keywords):
        booking_attempts = state.get("booking_attempts", 0) + 1
        new_state["booking_attempts"] = booking_attempts
        print(f"[ORQUESTADOR] 📅 Solicitud de cita detectada (intento {booking_attempts})")

    if normalize_keywords(last_message, faq_keywords):
        new_state["faq_attempts"] = 1
        print(f"[ORQUESTADOR] ❓ Pregunta FAQ detectada (este turno)")

    print(f"[ORQUESTADOR] Contadores: {new_state}")
    return new_state


def route_orchestrator(state: TallerState) -> str:
    """
    FUNCIÓN DE ROUTEO: Lee el estado y decide la ruta.

    Retorna:
    - "rama_agendamiento" si hay corrección post-booking
    - "rama_agendamiento" si hay flujo de booking activo (datos parciales)
    - "rama_agendamiento" si diagnóstico confirmado o el usuario confirma
    - "rama_faq" si hay pregunta FAQ en este turno (faq_attempts == 1)
    - "handoff" si human_requests >= 2
    - "rama_agendamiento" si booking_attempts >= 2 sin diagnóstico
    - "rama_diagnostico" por defecto
    """
    diagnosis_complete = state.get("diagnosis_complete", False)
    client_confirmed = state.get("client_confirmed_diagnosis", False)
    booking_attempts = state.get("booking_attempts", 0)
    human_requests = state.get("human_requests", 0)
    faq_attempts = state.get("faq_attempts", 0)
    damaged_part = state.get("damaged_part", "")
    booking_confirmed = state.get("booking_confirmed", False)

    # Extraer último mensaje (para múltiples checks)
    last_text = ""
    messages = state.get("messages", [])
    if messages:
        last = messages[-1]
        content = last.content if hasattr(last, "content") else last.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(c) for c in content)
        last_text = str(content).lower()

    print(f"\n[ROUTE_ORCHESTRATOR] ══════════════════════════════")
    print(f"  - diagnosis_complete: {diagnosis_complete}")
    print(f"  - client_confirmed_diagnosis: {client_confirmed}")
    print(f"  - booking_attempts: {booking_attempts}")
    print(f"  - human_requests: {human_requests}")
    print(f"  - faq_attempts: {faq_attempts}")
    print(f"  - booking_confirmed: {booking_confirmed}")
    print(f"  - damaged_part: {damaged_part}")

    # PRIORIDAD 1: Corrección post-booking → ir directo a agendamiento, no pasar por FAQ
    if booking_confirmed:
        correction_keywords = [
            "equivoqué", "equivoque", "cambiar", "cambio", "cambiarlos",
            "modificar", "corrijo", "corregir", "corrección", "correccion",
            "error", "incorrecto", "incorrecta", "estaba mal", "estaba equivocado",
            "dije",
        ]
        if any(kw in last_text for kw in correction_keywords):
            print(f"[ROUTE_ORCHESTRATOR] 🔄 Corrección post-booking → rama_agendamiento")
            return "rama_agendamiento"

    # PRIORIDAD 3: Flujo de booking activo (tiene datos parciales) → no interrumpir con FAQ
    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data") or {}
    has_partial_booking = bool(customer_name or phone or appointment_data.get("preferred_date"))

    if has_partial_booking and not booking_confirmed:
        print(f"[ROUTE_ORCHESTRATOR] 📋 Flujo booking activo → rama_agendamiento")
        return "rama_agendamiento"

    # PRIORIDAD 4: FAQ detectado en este turno (flag per-turno)
    if faq_attempts >= 1:
        print(f"[ROUTE_ORCHESTRATOR] ❓ RUTEANDO A: rama_faq (pregunta FAQ)")
        return "rama_faq"

    # PRIORIDAD 5: Pide humano por segunda+ vez
    if human_requests >= 2:
        print(f"[ROUTE_ORCHESTRATOR] 🤝 RUTEANDO A: handoff (humano x{human_requests})")
        return "handoff"

    # PRIORIDAD 6: Diagnóstico confirmado
    if client_confirmed and diagnosis_complete:
        print(f"[ROUTE_ORCHESTRATOR] ✅ RUTEANDO A: rama_agendamiento (diagnóstico confirmado)")
        return "rama_agendamiento"

    # PRIORIDAD 7: Insiste en cita por segunda+ vez sin diagnóstico
    if booking_attempts >= 2 and not diagnosis_complete:
        print(f"[ROUTE_ORCHESTRATOR] 📅 RUTEANDO A: rama_agendamiento (insistencia x{booking_attempts})")
        return "rama_agendamiento"

    # Default: diagnóstico
    print(f"[ROUTE_ORCHESTRATOR] 📋 RUTEANDO A: rama_diagnostico")
    return "rama_diagnostico"
