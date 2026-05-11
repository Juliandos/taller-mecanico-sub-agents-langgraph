"""Nodo Agregador - Combina respuestas de ambas ramas y detecta handoff"""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState


def agregador(state: TallerState) -> dict:
    """
    Agregador: Consolidador final de respuestas.

    - Entrega los messages agregados por nodos anteriores
    - Si cliente pide transferencia a humano:
      * 1ª vez: Pregunta empática sobre diagnóstico
      * 2ª vez+: Handoff definitivo
    - Detecta si no hay conclusión útil después de varios turnos
    """
    messages = state.get("messages", [])
    customer_name = state.get("customer_name", "")
    diagnostico_summary = state.get("diagnostico_summary", "")
    appointment_summary = state.get("appointment_summary", "")
    requires_human = state.get("requires_human", False)
    human_transfer_requests = state.get("human_transfer_requests", 0)
    diagnosis_complete = state.get("diagnosis_complete", False)
    booking_confirmed = state.get("booking_confirmed", False)

    print(f"[AGREGADOR] Consolidando respuestas finales...")
    print(f"[AGREGADOR] Total messages en estado: {len(messages)}")
    print(f"[AGREGADOR] requires_human: {requires_human}, intentos: {human_transfer_requests}")

    if messages:
        last_msg = messages[-1]
        msg_type = getattr(last_msg, "type", "unknown")
        content = getattr(last_msg, "content", "")[:50]
        print(f"[AGREGADOR] Último mensaje: type={msg_type}, content={content}")

    if customer_name:
        print(f"[AGREGADOR] Cliente: {customer_name}")

    # Mensajes predefinidos
    FIRST_REQUEST_MSG = (
        "Entiendo que prefieres hablar con un asesor. "
        "Antes de transferirte, ¿podrías describir brevemente qué problema tiene tu vehículo? "
        "Con eso podré ayudarte mejor cuando hables con el equipo."
    )

    HANDOFF_MSG = (
        "De acuerdo. Un asesor humano se comunicará contigo pronto. "
        "Mientras tanto, ten en cuenta los detalles que nos compartiste. "
        "Gracias por tu paciencia."
    )

    # CASO 1: Primera solicitud de transferencia a humano
    if requires_human and human_transfer_requests == 1:
        print("[AGREGADOR] 🤝 Primera solicitud de transferencia - Preguntando por diagnóstico")
        messages_with_request = list(messages) + [AIMessage(content=FIRST_REQUEST_MSG)]
        return {
            "messages": messages_with_request,
            "diagnostico_summary": FIRST_REQUEST_MSG,
            "requires_human": False,  # No transfiere aún, reseta para siguiente turno
            "human_transfer_requests": human_transfer_requests,
        }

    # CASO 2: Segunda solicitud de transferencia (o más)
    if requires_human and human_transfer_requests >= 2:
        print("[AGREGADOR] 🤝 Segunda (o más) solicitud - Handoff definitivo a humano")
        messages_with_handoff = list(messages) + [AIMessage(content=HANDOFF_MSG)]
        return {
            "messages": messages_with_handoff,
            "diagnostico_summary": HANDOFF_MSG,
            "requires_human": True,
            "human_transfer_requests": human_transfer_requests,
        }

    # CASO 3: Sin conclusión útil después de varios turnos (sin solicitud explícita)
    user_messages = [m for m in messages if getattr(m, "type", "") in ["human", "user"]]
    last_is_user = messages and getattr(messages[-1], "type", "") in ["human", "user"]

    if (not requires_human and not diagnosis_complete and not booking_confirmed and
        len(user_messages) >= 5 and last_is_user):
        print("[AGREGADOR] 🤝 Detectada falta de conclusión después de varios turnos")
        messages_with_handoff = list(messages) + [AIMessage(content=HANDOFF_MSG)]
        return {
            "messages": messages_with_handoff,
            "diagnostico_summary": HANDOFF_MSG,
            "requires_human": True,
            "human_transfer_requests": 1,
        }

    # CASO NORMAL: Retornar estado consolidado
    return {
        "messages": messages,
        "diagnostico_summary": diagnostico_summary,
        "appointment_summary": appointment_summary,
        "requires_human": False,
    }
