"""Evaluador de agendamiento - React Agent con tools."""

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from agents.taller.state import TallerState
from agents.taller.nodes.rama_agendamiento.tools import (
    consultar_disponibilidad,
    crear_cita as tool_crear_cita,
)


class AppointmentInfo(BaseModel):
    """Información extraída para agendar cita."""
    customer_name: str = Field(description="Nombre completo del cliente")
    phone: str = Field(description="Número de teléfono")
    preferred_date: str = Field(description="Fecha preferida")
    preferred_time: str = Field(description="Hora preferida")


llm = init_chat_model("openai:gpt-4o", temperature=0)
llm_structured = llm.with_structured_output(schema=AppointmentInfo)


def evaluador_agendamiento(state: TallerState) -> dict:
    """React Agent para agendamiento con tools internos."""
    messages = state.get("messages", [])
    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    booking_confirmed = state.get("booking_confirmed", False)

    print(f"\n[EVALUADOR_AGENDAMIENTO] Estado: nombre={bool(customer_name)}, phone={bool(phone)}, confirmado={booking_confirmed}")

    # Contar mensajes humanos
    user_messages = [m for m in messages
                     if (isinstance(m, dict) and m.get("type") == "human") or
                        (hasattr(m, "type") and m.type == "human")]

    # Detectar confirmación
    last_msg = ""
    if messages:
        last = messages[-1]
        if isinstance(last, dict):
            last_msg = str(last.get("content", "")).lower()
        else:
            last_msg = str(last.content).lower() if hasattr(last, "content") else ""

    confirm_keywords = ["sí", "si", "ok", "vale", "listo", "adelante", "confirmado", "correcto", "yes", "acepto", "aceptado"]
    has_confirmation = any(kw in last_msg for kw in confirm_keywords)

    # TURNO 1: Pedir información
    if len(user_messages) == 1:
        print("[EVALUADOR_AGENDAMIENTO] TURNO 1: pidiendo información")
        msg = """Perfecto, voy a ayudarte a agendar tu cita. Necesito:

1. Tu nombre completo
2. Tu número de teléfono
3. Fecha preferida (ej: mañana, próxima semana)
4. Hora preferida (ej: 10:00, por la tarde)

¿Puedes proporcionar esta información?"""

        return {
            "messages": [AIMessage(content=msg)],
            "agendamiento_decision": "ir_a_agregador",
        }

    # TURNO 2+: Procesar con tools
    if len(user_messages) >= 2:
        print(f"[EVALUADOR_AGENDAMIENTO] TURNO 2+: {len(user_messages)} mensajes")

        # Si cliente confirma, crear cita
        if booking_confirmed and has_confirmation:
            print("[EVALUADOR_AGENDAMIENTO] Cliente confirma → CREAR CITA")
            try:
                resultado = tool_crear_cita(
                    cliente_nombre=customer_name,
                    cliente_telefono=phone,
                    fecha=appointment_data.get("preferred_date", "2026-05-15"),
                    hora=appointment_data.get("preferred_time", "14:00"),
                    area_servicio="Diagnóstico",
                )

                confirmation_msg = f"""✅ ¡CITA AGENDADA EXITOSAMENTE!

📋 Confirmación: {resultado['confirmacion_id']}
👤 Cliente: {resultado['cliente_nombre']}
📱 Teléfono: {resultado['cliente_telefono']}
📅 Fecha: {resultado['fecha']}
🕐 Hora: {resultado['hora']}
🔧 Área: {resultado['area_servicio']}
👨‍🔧 Mecánico: {resultado['mecanico']}
💰 Costo estimado: {resultado['costo_estimado']}"""

                return {
                    "messages": [AIMessage(content=confirmation_msg)],
                    "agendamiento_decision": "ir_a_agregador",
                    "booking_confirmed": True,
                }
            except Exception as e:
                print(f"[EVALUADOR_AGENDAMIENTO] Error: {e}")
                return {
                    "messages": [AIMessage(content=f"Error al agendar: {str(e)}")],
                    "agendamiento_decision": "ir_a_agregador",
                }

        # Si no tiene confirmación, extraer datos y consultar disponibilidad
        if not booking_confirmed:
            print("[EVALUADOR_AGENDAMIENTO] Extrayendo datos...")
            try:
                system_prompt = """Extrae información de agendamiento.
Si NO encuentras algo, retorna string vacío "". NO uses valores por defecto."""

                formatted_messages = [("system", system_prompt)]
                for m in messages:
                    if isinstance(m, dict):
                        role = m.get("type", "user")
                        content = m.get("content", "")
                    else:
                        role = getattr(m, "type", "user")
                        content = getattr(m, "content", "")
                    formatted_messages.append((role, content))

                extracted = llm_structured.invoke(formatted_messages)

                # Validar datos
                missing_fields = []
                if not extracted.customer_name or extracted.customer_name.strip() == "":
                    missing_fields.append("nombre")
                if not extracted.phone or extracted.phone.strip() == "":
                    missing_fields.append("teléfono")
                if not extracted.preferred_date or extracted.preferred_date.strip() == "":
                    missing_fields.append("fecha")
                if not extracted.preferred_time or extracted.preferred_time.strip() == "":
                    missing_fields.append("hora")

                # Si faltan datos
                if missing_fields:
                    print(f"[EVALUADOR_AGENDAMIENTO] Faltan datos: {missing_fields}")
                    missing_text = ", ".join(missing_fields)
                    ask_msg = f"""Necesito: {missing_text}

¿Puedes proporcionar esta información?"""

                    result = {"messages": [AIMessage(content=ask_msg)]}
                    if extracted.customer_name and extracted.customer_name.strip():
                        result["customer_name"] = extracted.customer_name
                    if extracted.phone and extracted.phone.strip():
                        result["phone"] = extracted.phone
                    result["agendamiento_decision"] = "ir_a_agregador"
                    return result

                # Consultar disponibilidad
                print(f"[EVALUADOR_AGENDAMIENTO] Consultando disponibilidad...")
                disponibilidad = consultar_disponibilidad(
                    extracted.preferred_date,
                    extracted.preferred_time
                )

                if not disponibilidad.get("disponibilidad_confirmada"):
                    print("[EVALUADOR_AGENDAMIENTO] Sin disponibilidad")
                    no_avail = f"""No hay disponibilidad para {extracted.preferred_date} a las {extracted.preferred_time}.

Horarios del taller:
- Lunes-Viernes: 08:00-18:00
- Sábado: 09:00-14:00

¿Otra fecha/hora?"""
                    return {
                        "messages": [AIMessage(content=no_avail)],
                        "agendamiento_decision": "ir_a_agregador",
                    }

                # Disponibilidad OK
                print("[EVALUADOR_AGENDAMIENTO] Disponibilidad confirmada")
                mecanicos = "\n".join([f"- {m['nombre']} ({m['especialidad']})" for m in disponibilidad["mecanicos_disponibles"]])

                confirm_msg = f"""✅ Disponibilidad confirmada para {extracted.preferred_date} a las {extracted.preferred_time}

👨‍🔧 Mecánicos disponibles:
{mecanicos}

🔧 Áreas: Motor, Frenos, Suspensión, Dirección, Diagnóstico

¿Confirmas? (Sí/Ok/Adelante)"""

                return {
                    "messages": [AIMessage(content=confirm_msg)],
                    "customer_name": extracted.customer_name,
                    "phone": extracted.phone,
                    "appointment_data": {
                        "preferred_date": extracted.preferred_date,
                        "preferred_time": extracted.preferred_time,
                    },
                    "booking_confirmed": True,
                    "agendamiento_decision": "ir_a_agregador",
                }

            except Exception as e:
                print(f"[EVALUADOR_AGENDAMIENTO] Error: {e}")
                return {
                    "messages": [AIMessage(content=f"Error: {str(e)}")],
                    "agendamiento_decision": "ir_a_agregador",
                }

    return {"agendamiento_decision": "ir_a_agregador"}


def route_agendamiento_main(state: TallerState) -> str:
    """Enrutamiento: siempre a agregador."""
    return "agregador"
