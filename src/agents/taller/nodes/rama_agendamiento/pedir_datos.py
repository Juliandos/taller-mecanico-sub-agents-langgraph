"""Nodo para pedir datos faltantes durante el agendamiento."""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from agents.taller.nodes.rama_agendamiento.simulated_availability import (
    get_available_dates,
    get_mechanics,
    get_service_areas,
)


def pedir_datos_faltantes(state: TallerState) -> dict:
    """
    Envía un mensaje específico pidiendo solo los datos que faltan.
    Los datos faltantes se detectan del estado actual.
    """
    new_state: TallerState = {}

    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")
    missing_fields = state.get("missing_fields", [])

    print(f"[PEDIR_DATOS] Datos faltantes: {missing_fields}")

    # Detectar condiciones especiales
    hora_fuera_horario = "preferred_time_invalid" in missing_fields
    fecha_es_festivo = any(f.startswith("preferred_date_holiday:") for f in missing_fields)
    necesita_hora_especifica = any(f.startswith("time_period:") for f in missing_fields)
    necesita_seleccion_mecanico = "select_mechanic" in missing_fields

    disponibilidad_consultada = bool(state.get("disponibilidad_context", ""))

    # Extraer nombre del festivo si existe
    holiday_name = ""
    if fecha_es_festivo:
        for f in missing_fields:
            if f.startswith("preferred_date_holiday:"):
                holiday_name = f.split(":", 1)[1]
                break

    # Extraer horarios disponibles si es un periodo
    available_hours = ""
    if necesita_hora_especifica:
        for f in missing_fields:
            if f.startswith("time_period:"):
                available_hours = f.split(":", 1)[1]
                break

    # Construir mensaje personalizado según qué datos faltan
    field_messages = {
        "customer_name": "tu nombre completo",
        "phone": "tu número de teléfono",
        "preferred_date": "la fecha preferida para la cita",
        "preferred_time": "la hora preferida para la cita",
    }

    # Filtrar campos para mensaje - excluir marcas especiales
    campos_pedir = [
        f for f in missing_fields
        if f != "preferred_time_invalid"
        and not f.startswith("preferred_date_holiday:")
        and not f.startswith("time_period:")
    ]
    missing_text = ", ".join([field_messages.get(f, f) for f in campos_pedir])

    # Construir sugerencias de fechas/horas disponibles si hay disponibilidad consultada
    disponibilidad_texto = ""
    if disponibilidad_consultada and ("preferred_date" in campos_pedir or "preferred_time" in campos_pedir):
        available_dates = get_available_dates(15)
        mechanics = get_mechanics()
        service_areas = get_service_areas()

        # Mostrar próximas 5 fechas disponibles
        fechas_sugeridas = "\n".join([
            f"  • {formatted}"
            for date, formatted, available in available_dates[:5] if available
        ])

        # Mostrar mecánicos disponibles
        mecanicos_text = "\n".join([f"  • {m['nombre']} ({m['especialidad']})" for m in mechanics[:3]])

        disponibilidad_texto = f"""
📅 **FECHAS DISPONIBLES (próximas semanas):**
{fechas_sugeridas}

👨‍🔧 **MECÁNICOS DISPONIBLES:**
{mecanicos_text}

⏰ **HORARIOS:**
  • Lunes-Viernes: 08:00 - 18:00
  • Sábado: 09:00 - 14:00
  • Domingo y festivos: CERRADO
"""

    # Crear mensaje pidiendo los datos faltantes
    if necesita_seleccion_mecanico:
        # Mostrar lista de mecánicos disponibles
        mecanicos = state.get("mecanicos_disponibles", [])
        if mecanicos:
            mecanicos_text = "\n".join([
                f"   {i}. {m['nombre']} ({m['especialidad']})"
                for i, m in enumerate(mecanicos, 1)
            ])
            ask_msg = f"""¿Con cuál mecánico prefieres trabajar?

{mecanicos_text}

Responde con el número (1-5) o di "cualquiera" si cualquiera de ellos te parece bien."""
        else:
            ask_msg = "¿Con cuál mecánico prefieres trabajar? Responde con el número o nombre del mecánico."

    elif fecha_es_festivo:
        # La fecha seleccionada es festivo
        ask_msg = f"""Lo siento, este día es festivo ({holiday_name}) y estamos cerrados.{disponibilidad_texto}

Por favor, sugiere otra fecha. Preferiblemente menciona el día de la semana y el número (ej: martes 19, 19 de mayo), o cualquier otra forma específica que tengas en mente. Aceptamos varios formatos, solo queremos asegurar que nos entiendamos bien.

¿Cuál sería una fecha más conveniente para ti?"""

    elif necesita_hora_especifica:
        # El usuario dijo un periodo (mañana, tarde) pero necesita hora específica
        period_text = "por la mañana" if ("mañana" in preferred_time.lower() or "08:00 - 12:00" in available_hours) else "por la tarde"
        ask_msg = f"""Perfecto, entendí que prefieres {period_text}.

Los horarios disponibles son: {available_hours}

¿Cuál hora específica te vendría bien? Por ejemplo:
- 10:00 ({period_text})
- 15:00 (por la tarde)
- 14:00 (temprano por la tarde)"""

    elif customer_name and phone and not hora_fuera_horario:
        # Si tenemos nombre y teléfono, solo pedir fecha/hora
        ask_msg = f"""Perfecto {customer_name}, tengo tu teléfono ({phone}).
Ahora necesito confirmar algunos detalles para tu cita:{disponibilidad_texto}

Por favor, proporciona:
- {missing_text}

Ejemplo: "Mañana a las 10:00 AM" o "Próxima semana el martes a las 2:00 PM" """
    elif hora_fuera_horario:
        # Si la hora está fuera de horario, mostrar mensaje específico
        ask_msg = f"""Lo siento, el horario que solicitaste está fuera de nuestro horario de atención.{disponibilidad_texto}

Por favor, proporciona una hora dentro de estos rangos. Por ejemplo:
- 10:00 (mañana por la mañana)
- 14:00 (mañana por la tarde)
- 16:30 (mañana al final de la tarde)

¿Cuál sería una hora más conveniente para ti?"""
    else:
        # Si faltan datos básicos
        ask_msg = f"""Para agendar tu cita necesito los siguientes datos:

- {missing_text}{disponibilidad_texto}

Por favor, proporcióname esta información para poder proceder con el agendamiento."""

    print(f"[PEDIR_DATOS] Enviando mensaje pidiendo: {campos_pedir}")

    new_state["messages"] = [AIMessage(content=ask_msg)]
    new_state["missing_fields"] = []
    return new_state
