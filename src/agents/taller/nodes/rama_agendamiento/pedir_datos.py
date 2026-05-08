"""Nodo para pedir datos faltantes durante el agendamiento."""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState


def pedir_datos_faltantes(state: TallerState) -> dict:
    """
    Envía un mensaje específico pidiendo solo los datos que faltan.
    Los datos faltantes se detectan del estado actual.
    """
    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")

    # Detectar qué datos faltan
    missing_fields = []
    if not customer_name:
        missing_fields.append("customer_name")
    if not phone:
        missing_fields.append("phone")
    if not preferred_date:
        missing_fields.append("preferred_date")
    if not preferred_time:
        missing_fields.append("preferred_time")

    print(f"[PEDIR_DATOS] Datos faltantes: {missing_fields}")

    # Construir mensaje personalizado según qué datos faltan
    field_messages = {
        "customer_name": "tu nombre completo",
        "phone": "tu número de teléfono",
        "preferred_date": "la fecha preferida para la cita (ej: mañana, próxima semana, una fecha específica)",
        "preferred_time": "la hora preferida para la cita (ej: 10:00, por la tarde, por la mañana)",
    }

    missing_text = ", ".join([field_messages.get(f, f) for f in missing_fields])

    # Crear mensaje pidiendo los datos faltantes
    if customer_name and phone:
        # Si tenemos nombre y teléfono, solo pedir fecha/hora
        ask_msg = f"""Perfecto {customer_name}, tengo tu teléfono ({phone}).
Ahora necesito confirmar algunos detalles para tu cita:

- {missing_text}

¿Puedes proporcionar esta información?"""
    else:
        # Si faltan datos básicos
        ask_msg = f"""Para agendar tu cita necesito los siguientes datos:

- {missing_text}

Por favor, proporcióname esta información para poder proceder con el agendamiento."""

    print(f"[PEDIR_DATOS] Enviando mensaje pidiendo: {missing_fields}")

    return {
        "messages": [AIMessage(content=ask_msg)],
        "missing_fields": [],  # Limpiar para evitar acumular en siguiente iteración
    }
