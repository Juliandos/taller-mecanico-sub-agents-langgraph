"""Nodo para pedir datos faltantes durante el agendamiento."""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from agents.taller.data_mecanicos import get_mecanicos
from agents.taller.nodes.rama_agendamiento.simulated_availability import (
    get_available_dates,
)


def pedir_datos_faltantes(state: TallerState) -> dict:
    """Envía mensaje pidiendo solo los datos que faltan."""
    new_state: TallerState = {}

    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    preferred_time = appointment_data.get("preferred_time", "")
    missing_fields = state.get("missing_fields", [])

    print(f"[PEDIR_DATOS] Faltantes: {missing_fields}")

    # Detectar condiciones especiales
    hora_fuera_horario = "preferred_time_invalid" in missing_fields
    fecha_es_festivo = any(f.startswith("preferred_date_holiday:") for f in missing_fields)
    necesita_hora_especifica = any(f.startswith("time_period:") for f in missing_fields)
    necesita_seleccion_mecanico = "select_mechanic" in missing_fields
    disponibilidad_consultada = bool(state.get("disponibilidad_context", ""))

    # Extraer información especial de missing_fields
    holiday_name = next(
        (f.split(":", 1)[1] for f in missing_fields if f.startswith("preferred_date_holiday:")),
        ""
    )
    available_hours = next(
        (f.split(":", 1)[1] for f in missing_fields if f.startswith("time_period:")),
        ""
    )

    # Mensajes para campos
    field_messages = {
        "customer_name": "tu nombre completo",
        "phone": "tu número de teléfono",
        "preferred_date": "la fecha preferida",
        "preferred_time": "la hora preferida",
    }

    # Campos normales (excluir flags especiales)
    campos_pedir = [
        f for f in missing_fields
        if f != "preferred_time_invalid"
        and not f.startswith("preferred_date_holiday:")
        and not f.startswith("time_period:")
    ]
    missing_text = ", ".join([field_messages.get(f, f) for f in campos_pedir])

    # Sugerencias de disponibilidad si hay contexto
    disponibilidad_texto = ""
    if disponibilidad_consultada and ("preferred_date" in campos_pedir or "preferred_time" in campos_pedir):
        available_dates = get_available_dates(15)
        mechanics = get_mecanicos()

        fechas_sugeridas = "\n".join([
            f"  • {formatted}"
            for date, formatted, available in available_dates[:5] if available
        ])

        mecanicos_text = "\n".join([
            f"  • {m['nombre']} ({m['especialidad_principal']})"
            for m in mechanics[:3]
        ])

        disponibilidad_texto = f"""
📅 FECHAS DISPONIBLES:
{fechas_sugeridas}

👨‍🔧 MECÁNICOS:
{mecanicos_text}

⏰ HORARIOS: Lunes-Viernes 08:00-18:00 | Sábado 09:00-14:00
"""

    # Construir mensaje según la situación
    if necesita_seleccion_mecanico:
        mecanicos = state.get("mecanicos_disponibles", [])
        mecanicos_text = "\n".join([
            f"   {i}. {m['nombre']} ({m['especialidad_principal']})"
            for i, m in enumerate(mecanicos, 1)
        ]) if mecanicos else "Mecánicos disponibles"
        ask_msg = f"""¿Con cuál mecánico prefieres trabajar?

{mecanicos_text}

Responde: número (1-5) o "cualquiera" """

    elif fecha_es_festivo:
        ask_msg = f"""Lo siento, {holiday_name} estamos cerrados.{disponibilidad_texto}
¿Otra fecha? (ej: martes 19, 19 de mayo)"""

    elif necesita_hora_especifica:
        period = "mañana" if "08:00 - 12:00" in available_hours else "tarde"
        ask_msg = f"""Perfecto, {period}. Horarios: {available_hours}

¿Qué hora específica? Ej: 10:00, 15:00"""

    elif customer_name and phone and not hora_fuera_horario:
        ask_msg = f"""Perfecto {customer_name}.{disponibilidad_texto}
Necesito:
- {missing_text}

Ej: "Mañana a las 10:00" o "Martes a las 2:00 PM" """

    elif hora_fuera_horario:
        ask_msg = f"""Horario fuera de atención.{disponibilidad_texto}
¿Otra hora? Ej: 10:00, 14:00, 16:30"""

    else:
        ask_msg = f"""Necesito:
- {missing_text}{disponibilidad_texto}
Por favor, proporciona esta información."""

    print(f"[PEDIR_DATOS] Pidiendo: {campos_pedir}")
    new_state["messages"] = [AIMessage(content=ask_msg)]
    new_state["missing_fields"] = []
    return new_state
