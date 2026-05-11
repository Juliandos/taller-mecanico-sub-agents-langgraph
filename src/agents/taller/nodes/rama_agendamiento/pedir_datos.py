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
    missing_fields = state.get("missing_fields", [])

    print(f"[PEDIR_DATOS] Datos faltantes: {missing_fields}")

    # Detectar si la hora está fuera de horario
    hora_fuera_horario = "preferred_time_invalid" in missing_fields

    # Construir mensaje personalizado según qué datos faltan
    field_messages = {
        "customer_name": "tu nombre completo",
        "phone": "tu número de teléfono",
        "preferred_date": "la fecha preferida para la cita (ej: mañana, próxima semana, una fecha específica)",
        "preferred_time": "la hora preferida para la cita",
    }

    # Filtrar campos para mensaje
    campos_pedir = [f for f in missing_fields if f != "preferred_time_invalid"]
    missing_text = ", ".join([field_messages.get(f, f) for f in campos_pedir])

    # Crear mensaje pidiendo los datos faltantes
    if customer_name and phone and not hora_fuera_horario:
        # Si tenemos nombre y teléfono, solo pedir fecha/hora
        ask_msg = f"""Perfecto {customer_name}, tengo tu teléfono ({phone}).
Ahora necesito confirmar algunos detalles para tu cita:

- {missing_text}

¿Puedes proporcionar esta información?"""
    elif hora_fuera_horario:
        # Si la hora está fuera de horario, mostrar mensaje específico
        ask_msg = f"""Lo siento, el horario que solicitaste está fuera de nuestro horario de atención.

⏰ **Horario de atención: 8:00 AM - 6:00 PM**

Por favor, proporciona una hora dentro de este rango. Por ejemplo:
- 10:00 AM (mañana por la mañana)
- 2:00 PM (mañana por la tarde)
- 4:30 PM (mañana al final de la tarde)

¿Cuál sería una hora más conveniente para ti?"""
    else:
        # Si faltan datos básicos
        ask_msg = f"""Para agendar tu cita necesito los siguientes datos:

- {missing_text}

⏰ Nota: El horario de atención es de 8:00 AM a 6:00 PM.

Por favor, proporcióname esta información para poder proceder con el agendamiento."""

    print(f"[PEDIR_DATOS] Enviando mensaje pidiendo: {campos_pedir}")

    return {
        "messages": [AIMessage(content=ask_msg)],
        "missing_fields": [],  # Limpiar para evitar acumular en siguiente iteración
    }
