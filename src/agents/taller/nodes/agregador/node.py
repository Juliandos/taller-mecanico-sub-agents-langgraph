"""Nodo Agregador - Combina respuestas de ambas ramas y detecta handoff"""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from agents.taller.prompts import (
    AGREGADOR_PRIMER_REQUEST,
    AGREGADOR_HANDOFF_FINAL,
    AGREGADOR_HANDOFF_AUTOMATICO,
)


def agregador(state: TallerState) -> dict:
    """
    Agregador: Consolidador final de respuestas.

    - Entrega los messages agregados por nodos anteriores
    - Si cliente pide transferencia a humano:
      * 1ª vez: Pregunta empática sobre diagnóstico
      * 2ª vez+: Handoff definitivo
    - Detecta si no hay conclusión útil después de varios turnos
    """
    new_state: TallerState = {}

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

    # CASO 1: Primera solicitud de transferencia a humano
    if requires_human and human_transfer_requests == 1:
        print("[AGREGADOR] 🤝 Primera solicitud - pidiendo diagnóstico")
        new_state["messages"] = list(messages) + [AIMessage(content=AGREGADOR_PRIMER_REQUEST)]
        new_state["diagnostico_summary"] = AGREGADOR_PRIMER_REQUEST
        new_state["requires_human"] = False
        new_state["human_transfer_requests"] = human_transfer_requests
        return new_state

    # CASO 2: Segunda solicitud de transferencia (o más)
    if requires_human and human_transfer_requests >= 2:
        print("[AGREGADOR] 🤝 Handoff definitivo a humano")
        new_state["messages"] = list(messages) + [AIMessage(content=AGREGADOR_HANDOFF_FINAL)]
        new_state["diagnostico_summary"] = AGREGADOR_HANDOFF_FINAL
        new_state["requires_human"] = True
        new_state["human_transfer_requests"] = human_transfer_requests
        return new_state

    # CASO 3: Sin conclusión útil después de varios turnos
    user_messages = [m for m in messages if getattr(m, "type", "") in ["human", "user"]]
    last_is_user = messages and getattr(messages[-1], "type", "") in ["human", "user"]

    if (not requires_human and not diagnosis_complete and not booking_confirmed and
        len(user_messages) >= 5 and last_is_user):
        print("[AGREGADOR] 🤝 Falta de conclusión - handoff automático")
        new_state["messages"] = list(messages) + [AIMessage(content=AGREGADOR_HANDOFF_FINAL)]
        new_state["diagnostico_summary"] = AGREGADOR_HANDOFF_FINAL
        new_state["requires_human"] = True
        new_state["human_transfer_requests"] = 1
        return new_state

    # CASO NORMAL: Retornar estado consolidado
    new_state["messages"] = messages
    new_state["diagnostico_summary"] = diagnostico_summary
    new_state["appointment_summary"] = appointment_summary
    new_state["requires_human"] = False
    return new_state
