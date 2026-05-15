"""Validador y Responder consolidado - Reemplaza pedir_datos + consultar_disponibilidad."""

from jinja2 import Environment
from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from agents.taller.data_mecanicos import get_mecanicos
from agents.taller.nodes.rama_agendamiento.simulated_availability import (
    get_available_dates,
    format_availability_display,
)

_env = Environment(trim_blocks=True, lstrip_blocks=True)

# Template condicional: solo muestra bloques para datos que realmente faltan.
# Si el usuario no ha dado ningún dato todavía (has_any_data=False) o faltan 4+
# campos, muestra el formulario completo con ejemplo.
_MISSING_TEMPLATE = _env.from_string("""\
{% set n = missing_fields | length %}
{% if not has_any_data or n >= 4 %}
Para agendar tu cita necesito: {{ campos_texto }}
{% elif n == 1 %}
¿Me puedes indicar tu {{ campos_texto }} para agendar la cita?
{% else %}
Para continuar con tu cita necesito: {{ campos_texto }}
{% endif %}
{% if "preferred_date" in missing_fields %}

📅 FECHAS DISPONIBLES (próximos 15 días):
{{ fechas_disponibles }}
{% endif %}
{% if "selected_mechanic" in missing_fields %}

👨‍🔧 MECÁNICOS DISPONIBLES:
{{ mecanicos_numerados }}
{% endif %}
{% if "preferred_time" in missing_fields %}

⏰ HORARIOS: Lunes-Viernes 08:00-18:00 | Sábado 09:00-14:00
{% endif %}
{% if not has_any_data or n >= 3 %}

¿Me puedes proporcionar esa información?
Ejemplo: "Juan García, 3001234567, martes 19 de mayo a las 10:00, con Juan García"
{% endif %}
""")


def validador_responder(state: TallerState) -> dict:
    """
    Nodo unificado que:
    1. Siempre consulta disponibilidad
    2. Detecta campos faltantes
    3. Si faltan → mensaje adaptativo (solo muestra bloques para datos aún faltantes)
    4. Si hay festivo → rechaza y pide alternativa
    5. Si todo está → marca ready_to_book = True (sin mensaje)
    """
    print(f"[VALIDADOR_RESPONDER] Validando estado de agendamiento...")

    # PASO 0: Si la cita ya fue confirmada, no re-agendar
    if state.get("booking_confirmed", False):
        print(f"[VALIDADOR_RESPONDER] ✅ Cita ya confirmada, ignorando")
        return {}

    # Obtener datos del estado
    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")
    selected_mechanic = state.get("selected_mechanic", "")
    missing_fields_extractor = state.get("missing_fields", [])

    # PASO 1: Consultar disponibilidad (siempre)
    mecanicos = get_mecanicos()
    available_dates = get_available_dates(15)

    fechas_disponibles = "\n".join([
        f"  • {formatted} {'✅' if available else '❌'}"
        for date, formatted, available in available_dates[:10]
    ])

    mecanicos_numerados = "\n".join([
        f"  {i}. {m['nombre']} ({m['especialidad_principal']}) - {m['experiencia_anos']} años"
        for i, m in enumerate(mecanicos, 1)
    ])

    # PASO 2: Verificar si el extractor detectó un festivo
    holiday_error = None
    for field in missing_fields_extractor:
        if field.startswith("preferred_date_holiday:"):
            holiday_error = field.split(":", 1)[1]
            break

    if holiday_error:
        print(f"[VALIDADOR_RESPONDER] ⚠️ FESTIVO DETECTADO: {holiday_error}")
        ask_msg = f"""❌ Lamentablemente, el {holiday_error} estamos cerrados por ser festivo.

📅 FECHAS DISPONIBLES (próximos 15 días):
{fechas_disponibles}

⏰ HORARIOS: Lunes-Viernes 08:00-18:00 | Sábado 09:00-14:00

¿Podrías proporcionar una fecha alternativa?
Ejemplo: "martes 19 de mayo a las 10:00"
"""
        return {
            "messages": [AIMessage(content=ask_msg)],
            "ready_to_book": False,
            "appointment_data": {"preferred_date": "", "preferred_time": ""},
            "missing_fields": [],
            "rejected_date": holiday_error,
            "disponibilidad_context": fechas_disponibles,
            "mecanicos_disponibles": mecanicos,
        }

    # PASO 3: Detectar campos faltantes
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

    # PASO 3a: Si hay campos faltantes → mensaje adaptativo con Jinja2
    if missing_fields:
        campos_texto = ", ".join([missing_labels[f] for f in missing_fields])
        has_any_data = bool(customer_name or phone or preferred_date or preferred_time or selected_mechanic)

        ask_msg = _MISSING_TEMPLATE.render(
            missing_fields=missing_fields,
            has_any_data=has_any_data,
            campos_texto=campos_texto,
            fechas_disponibles=fechas_disponibles,
            mecanicos_numerados=mecanicos_numerados,
        ).strip()

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
    if state.get("booking_confirmed", False):
        print(f"[ROUTE_VALIDADOR] ✅ Cita ya confirmada → agregador")
        return "agregador"

    ready = state.get("ready_to_book", False)

    if ready:
        print(f"[ROUTE_VALIDADOR] ✅ Todo listo → booking_agent")
        return "booking_agent"
    else:
        print(f"[ROUTE_VALIDADOR] 📋 Esperando datos → agregador")
        return "agregador"
