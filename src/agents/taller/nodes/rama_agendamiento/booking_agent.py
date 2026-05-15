"""Agente de agendamiento para el taller mecánico."""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from datetime import datetime, timedelta
import random


def booking_agent(state: TallerState) -> dict:
    """Agente que crea la confirmación de cita con datos recopilados."""
    new_state: TallerState = {}

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
        confirmation_id = f"TM-{random.randint(10000, 99999)}"

        # Parsear fecha y hora
        appointment_date = preferred_date if preferred_date and preferred_date != "próximos días" else "2026-05-15"
        appointment_time = preferred_time if preferred_time and preferred_time != "horario disponible" else "14:00"

        if "mañana" in str(preferred_date).lower():
            tomorrow = datetime.now() + timedelta(days=1)
            appointment_date = tomorrow.strftime("%Y-%m-%d")

        if "tarde" in str(preferred_time).lower():
            appointment_time = "15:00"
        elif "mañana" in str(preferred_time).lower():
            appointment_time = "10:00"

        # Confirmación concisa
        confirmation_msg = f"""✅ ¡CITA AGENDADA!

📋 Confirmación: {confirmation_id}
👤 Cliente: {customer_name}
📅 Fecha: {appointment_date} a las {appointment_time}
🔧 Servicio: {service}
👨‍🔧 Mecánico: {mechanic_name}
💰 Costo: $180,000-350,000

⚠️ Instrucciones:
• Llega 15 minutos antes
• Guarda tu confirmación
• Cambios urgentes: 300-AUTO-PRO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿Algo está incorrecto? Puedes pedirme un cambio ahora mismo.
Ejemplo: "quiero cambiar la fecha a..." o "cambia el mecánico a..."

Para una nueva cita, recarga la página (F5) o inicia un nuevo chat."""

        print(f"[BOOKING_AGENT] ✅ {appointment_date} {appointment_time}")

        new_state["messages"] = [AIMessage(content=confirmation_msg)]
        new_state["booking_confirmed"] = True
        new_state["appointment_summary"] = confirmation_msg
        new_state["appointment_data"] = {
            "confirmation_id": confirmation_id,
            "customer_name": customer_name,
            "phone": phone,
            "date": appointment_date,
            "time": appointment_time,
            # Mantener claves "preferred_*" para que el flujo de corrección funcione
            "preferred_date": appointment_date,
            "preferred_time": appointment_time,
            "service": service,
            "mechanic": mechanic_name,
        }
        return new_state

    except Exception as e:
        print(f"[BOOKING_AGENT] ❌ {e}")
        new_state["messages"] = [AIMessage(content="Problema al agendar. Transferiendo a humano...")]
        new_state["requires_human"] = True
        return new_state
