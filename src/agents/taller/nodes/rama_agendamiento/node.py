"""Rama 2: Agendamiento - Extractor + Booking Agent"""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState
from agents.taller.nodes.rama_agendamiento.extractor import extractor_datos
from agents.taller.nodes.rama_agendamiento.booking_agent import booking_agent
from agents.taller.nodes.rama_agendamiento.route_booking import route_extractor
import random


def agent_booking(state: TallerState) -> dict:
    """
    Agent Booking: React Agent que recopila datos para agendar cita.

    Flujo:
    1. Extrae datos del cliente (nombre, teléfono, fecha, hora)
    2. Consulta disponibilidad (simulado, RAG en FASE 2)
    3. Decide: agendar o transferir a humano
    """
    new_state: TallerState = {}

    messages = state.get("messages", [])
    print("[AGENT_BOOKING] Iniciando recopilación de datos...")

    # Extrae datos del último mensaje (maneja dicts y Message objects)
    last_message = ""
    if messages:
        last = messages[-1]
        if isinstance(last, dict):
            last_message = str(last.get("content", "")).lower()
        else:
            last_message = str(last.content).lower() if hasattr(last, "content") else ""

    # Simulación: detecta información
    has_name = any(word in last_message for word in ["soy", "llamo", "nombre"])
    has_phone = any(char.isdigit() for char in last_message)
    has_date = any(
        word in last_message for word in ["mañana", "hoy", "próximo", "2026", "mayo", "junio"]
    )

    # Datos recopilados
    customer_name = state.get("customer_name", "")
    if not customer_name and has_name:
        # Extracto simple de nombre (FASE 2: LLM estructurado)
        words = last_message.split()
        for i, word in enumerate(words):
            if word.lower() in ["soy", "llamo"] and i + 1 < len(words):
                customer_name = words[i + 1]
                break

    print(f"[AGENT_BOOKING] Detectado - Nombre: {customer_name}, Teléfono: {has_phone}, Fecha: {has_date}")

    # Respuesta: preguntar datos faltantes o agendar
    if not customer_name or not has_phone or not has_date:
        response_content = "Para agendar tu cita necesito:\n"
        if not customer_name:
            response_content += "- Tu nombre\n"
        if not has_phone:
            response_content += "- Tu teléfono de contacto\n"
        if not has_date:
            response_content += "- Fecha preferida\n"
        response_content += "\n¿Puedes proporcionar esta información?"

        decision = "recopilar_datos"
    else:
        decision = "agendar"

    response = AIMessage(content=response_content)

    new_state["messages"] = [response]
    new_state["booking_decision"] = decision
    new_state["customer_name"] = customer_name
    return new_state


def ejecutar_tool_booking(state: TallerState) -> dict:
    """
    Ejecuta tools de agendamiento (simulado, RAG en FASE 2):
    - Consultar horarios disponibles
    - Consultar mecánicos
    - Verificar inventario
    - Agendar cita
    """
    new_state: TallerState = {}

    booking_decision = state.get("booking_decision", "recopilar_datos")

    print(f"[EJECUTAR_TOOL_BOOKING] Decision: {booking_decision}")

    if booking_decision != "agendar":
        return new_state

    # Simulación: agendar cita
    confirmation_id = f"TM-{random.randint(10000, 99999)}"
    customer_name = state.get("customer_name", "Cliente")

    response_content = f"""✅ ¡CITA AGENDADA EXITOSAMENTE!

📋 Confirmación: {confirmation_id}
👤 Cliente: {customer_name}
📅 Fecha: 2026-05-15
🕐 Hora: 10:00 AM
🔧 Servicio: Cambio de bujías/filtro
👨‍🔧 Mecánico: Juan García
💰 Costo estimado: $180,000

⚠️ Instrucciones:
- Llega 10 minutos antes
- Guarda tu número de confirmación
- Para cancelar: 300-AUTO-PRO (300-288-6776)
"""

    response = AIMessage(content=response_content)

    new_state["messages"] = [response]
    new_state["appointment_summary"] = response_content
    new_state["booking_confirmed"] = True
    return new_state


def transferir_a_humano(state: TallerState) -> dict:
    """
    Transfiere a un asesor humano cuando no se puede agendar.
    """
    new_state: TallerState = {}

    print("[TRANSFERIR_A_HUMANO] Iniciando transferencia...")

    ticket_id = f"HT-{random.randint(1000, 9999)}"
    customer_name = state.get("customer_name", "Cliente")

    response_content = f"""📞 TRANSFERENCIA A ASESOR HUMANO

Hola {customer_name}, un asesor de nuestro taller se comunicará contigo pronto.

🎫 Ticket: {ticket_id}
⏰ Tiempo de respuesta: 24 horas
📞 Línea directa: 300-AUTO-PRO (300-288-6776)
💬 WhatsApp: +57 300-123-4567
📧 Email: citas@tallerautopartespro.com

Un asesor revisará tu solicitud y te contactará pronto.
"""

    response = AIMessage(content=response_content)

    new_state["messages"] = [response]
    new_state["appointment_summary"] = response_content
    new_state["requires_human"] = True
    return new_state


def route_booking(state: TallerState) -> str:
    """Enrutamiento del agent booking."""
    booking_decision = state.get("booking_decision", "recopilar_datos")

    if booking_decision == "agendar":
        return "ejecutar_tool_booking"
    elif booking_decision == "transferir":
        return "transferir_a_humano"
    else:
        return "agent_booking"  # Loop: seguir recopilando datos
