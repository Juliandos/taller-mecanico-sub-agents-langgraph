"""Validador y Responder consolidado - Reemplaza pedir_datos + consultar_disponibilidad."""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from agents.taller.data_mecanicos import get_mecanicos
from agents.taller.nodes.rama_agendamiento.simulated_availability import (
    get_available_dates,
    format_availability_display,
)


def validador_responder(state: TallerState) -> dict:
    """
    Nodo unificado que:
    1. Siempre consulta disponibilidad
    2. Detecta campos faltantes
    3. Si faltan → muestra disponibilidad + pide TODOS los faltantes en UN mensaje
    4. Si todo está → marca ready_to_book = True (sin mensaje)
    """
    print(f"[VALIDADOR_RESPONDER] Validando estado de agendamiento...")

    # Obtener datos del estado
    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")
    selected_mechanic = state.get("selected_mechanic", "")

    # PASO 1: Consultar disponibilidad (siempre)
    mecanicos = get_mecanicos()
    available_dates = get_available_dates(15)

    # Formatear fechas disponibles
    fechas_disponibles = "\n".join([
        f"  • {formatted} {'✅' if available else '❌'}"
        for date, formatted, available in available_dates[:10]
    ])

    # Formatear mecánicos
    mecanicos_numerados = "\n".join([
        f"  {i}. {m['nombre']} ({m['especialidad_principal']}) - {m['experiencia_anos']} años"
        for i, m in enumerate(mecanicos, 1)
    ])

    # PASO 2: Detectar campos faltantes
    missing_fields = []
    missing_labels = {}

    if not customer_name:
        missing_fields.append("customer_name")
        missing_labels["customer_name"] = "nombre completo"

    if not phone:
        missing_fields.append("phone")
        missing_labels["phone"] = "número de teléfono"

    if not preferred_date:
        missing_fields.append("preferred_date")
        missing_labels["preferred_date"] = "fecha preferida"

    if not preferred_time:
        missing_fields.append("preferred_time")
        missing_labels["preferred_time"] = "hora preferida"

    if not selected_mechanic:
        missing_fields.append("selected_mechanic")
        missing_labels["selected_mechanic"] = "mecánico"

    print(f"[VALIDADOR_RESPONDER] Campos faltantes: {missing_fields}")

    # PASO 3a: Si hay campos faltantes → mensaje con TODO de una vez
    if missing_fields:
        campos_texto = ", ".join([missing_labels[f] for f in missing_fields])

        ask_msg = f"""Para agendar tu cita necesito: {campos_texto}

📅 FECHAS DISPONIBLES (próximos 15 días):
{fechas_disponibles}

👨‍🔧 MECÁNICOS DISPONIBLES:
{mecanicos_numerados}

⏰ HORARIOS: Lunes-Viernes 08:00-18:00 | Sábado 09:00-14:00

¿Me puedes proporcionar esa información?
Ejemplo: "Juan García, 3001234567, martes 19 de mayo a las 10:00, con Juan García"
"""

        print(f"[VALIDADOR_RESPONDER] Pidiendo datos, enviando mensaje")
        return {
            "messages": [AIMessage(content=ask_msg)],
            "ready_to_book": False,
            "disponibilidad_context": fechas_disponibles,
            "mecanicos_disponibles": mecanicos,
        }

    # PASO 3b: Si tiene TODO → ready_to_book = True (sin mensaje)
    print(f"[VALIDADOR_RESPONDER] ✅ Todos los datos presentes → ready_to_book = True")
    return {
        "ready_to_book": True,
        "disponibilidad_context": fechas_disponibles,
        "mecanicos_disponibles": mecanicos,
    }


def route_validador(state: TallerState) -> str:
    """
    Router simple: 2 rutas
    - Si ready_to_book → booking_agent
    - Si falta algo → agregador (espera siguiente turn)
    """
    ready = state.get("ready_to_book", False)

    if ready:
        print(f"[ROUTE_VALIDADOR] ✅ Todo listo → booking_agent")
        return "booking_agent"
    else:
        print(f"[ROUTE_VALIDADOR] 📋 Esperando datos → agregador")
        return "agregador"
