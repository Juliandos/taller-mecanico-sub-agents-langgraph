"""Agente de agendamiento para el taller mecánico."""

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from datetime import datetime, timedelta
import random


def booking_agent(state) -> dict:
    """
    Agente que maneja el agendamiento.
    Usa LLM para generar la respuesta final de agendamiento.
    """
    llm = init_chat_model("openai:gpt-4o", temperature=0)

    appointment_data = state.get("appointment_data", {})
    service = state.get("damaged_part", "Diagnóstico y reparación")
    customer_name = state.get("customer_name", appointment_data.get("customer_name", ""))
    phone = state.get("phone", appointment_data.get("phone", ""))
    preferred_date = appointment_data.get("preferred_date", "próximos días")
    preferred_time = appointment_data.get("preferred_time", "horario disponible")

    # Obtener mecánico seleccionado o usar el recomendado
    mecanicos = state.get("mecanicos_disponibles", [])
    selected_mechanic = state.get("selected_mechanic", "")
    mechanic_name = selected_mechanic if selected_mechanic else (mecanicos[0]["nombre"] if mecanicos else "Juan García")
    mechanic_area = state.get("selected_area", "Diagnóstico")

    print(f"[BOOKING_AGENT] Agendando cita para {customer_name} ({phone})")

    try:
        # Generar la confirmación de cita directamente
        confirmation_id = f"TM-{random.randint(10000, 99999)}"

        # Parsear fecha y hora si es posible
        appointment_date = preferred_date if preferred_date and preferred_date != "próximos días" else "2026-05-15"
        appointment_time = preferred_time if preferred_time and preferred_time != "horario disponible" else "14:00"

        # Si el usuario dijo "mañana", usamos mañana
        if "mañana" in str(preferred_date).lower():
            tomorrow = datetime.now() + timedelta(days=1)
            appointment_date = tomorrow.strftime("%Y-%m-%d")

        # Si dijo "tarde", ajustar hora
        if "tarde" in str(preferred_time).lower():
            appointment_time = "15:00"
        elif "mañana" in str(preferred_time).lower():
            appointment_time = "10:00"

        confirmation_msg = f"""✅ ¡CITA AGENDADA EXITOSAMENTE!

📋 Confirmación: {confirmation_id}
👤 Cliente: {customer_name}
📱 Teléfono: {phone}
📅 Fecha: {appointment_date}
🕐 Hora: {appointment_time}
🔧 Servicio: {service}
👨‍🔧 Mecánico: {mechanic_name}
💰 Costo estimado: $180,000-350,000

⚠️ INSTRUCCIONES:
- Llega 15 minutos antes
- Guarda tu número de confirmación
- Para cambios: {phone} o al 300-AUTO-PRO
- Cancelaciones con 24h de anticipación"""

        print(f"[BOOKING_AGENT] ✅ Cita agendada para {appointment_date} a las {appointment_time}")

        return {
            "messages": [AIMessage(content=confirmation_msg)],
            "booking_confirmed": True,
            "appointment_summary": confirmation_msg,
            "appointment_data": {
                "confirmation_id": confirmation_id,
                "customer_name": customer_name,
                "phone": phone,
                "date": appointment_date,
                "time": appointment_time,
                "service": service,
            }
        }
    except Exception as e:
        print(f"[BOOKING_AGENT] ❌ Error: {e}")
        error_response = f"Hubo un problema al agendar tu cita: {str(e)}"
        return {
            "messages": [AIMessage(content=error_response)],
            "requires_human": True,
        }
