"""Nodo FAQ - Responde preguntas sobre el taller y mecánicos."""

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from agents.taller.state import TallerState
from agents.taller.prompts import FAQ_PROMPT
from agents.taller.data_mecanicos import (
    get_mecanicos,
    get_taller_info,
    get_mecanicos_por_especialidad,
)


def nodo_faq(state: TallerState) -> dict:
    """
    Responde preguntas sobre el taller y mecánicos.
    Detecta intención oculta (diagnostico/agendamiento) y señala con INTENT:
    """
    print(f"[NODO_FAQ] Procesando pregunta...")

    # Obtener último mensaje del usuario
    messages = state.get("messages", [])
    if not messages:
        return {"messages": [AIMessage(content="No entendí tu pregunta.")]}

    last_message = messages[-1].content if messages else ""

    # Preparar información de taller y mecánicos
    taller_info = get_taller_info()
    mecanicos = get_mecanicos()

    # Formatear información del taller
    taller_texto = f"""
Nombre: {taller_info['nombre']}
Misión: {taller_info['misión']}
Horarios: L-V {taller_info['horarios']['lunes_viernes']}, Sábado {taller_info['horarios']['sabado']}
Contacto: {taller_info['contacto']['telefono']} | WhatsApp: {taller_info['contacto']['whatsapp']}
Servicios: {', '.join(taller_info['servicios'])}
Garantía: {taller_info['garantia']}
""".strip()

    # Formatear información de mecánicos
    mecanicos_texto = "\n".join([
        f"- {m['nombre']}: {m['especialidad_principal']} ({m['experiencia_anos']} años) - {m['bio'][:80]}..."
        for m in mecanicos
    ])

    # Usar LLM con FAQ_PROMPT
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    prompt_filled = FAQ_PROMPT.format(
        taller_info=taller_texto,
        mecanicos_info=mecanicos_texto,
        pregunta=last_message
    )

    response = llm.invoke(prompt_filled)
    response_text = response.content

    print(f"[NODO_FAQ] Respuesta generada")

    # Detectar intención en la respuesta
    faq_intent = ""
    if "INTENT:diagnostico" in response_text:
        faq_intent = "diagnostico"
        # Remover el marcador de intención de la respuesta
        response_text = response_text.replace("INTENT:diagnostico", "").strip()
    elif "INTENT:agendamiento" in response_text:
        faq_intent = "agendamiento"
        response_text = response_text.replace("INTENT:agendamiento", "").strip()

    print(f"[NODO_FAQ] Intent detectado: {faq_intent or 'ninguno'}")

    return {
        "messages": [AIMessage(content=response_text)],
        "faq_detected_intent": faq_intent,
    }


def route_faq(state: TallerState) -> str:
    """
    Router post-FAQ. Lee faq_detected_intent y redirige.
    """
    intent = state.get("faq_detected_intent", "")

    print(f"[ROUTE_FAQ] Intent: {intent}")

    if intent == "diagnostico":
        return "evaluador_pieza_dañada"
    elif intent == "agendamiento":
        return "extractor_datos"
    else:
        # Vuelve a menú (agregador)
        return "agregador"
