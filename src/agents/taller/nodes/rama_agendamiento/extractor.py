"""Extractor de datos para agendamiento de citas."""

import re
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from agents.taller.state import TallerState

class AppointmentData(BaseModel):
    """Datos extraídos para agendar cita."""
    customer_name: str = Field(description="Nombre completo del cliente")
    phone: str = Field(description="Número de teléfono del cliente")
    preferred_date: str = Field(description="Fecha preferida para la cita (ej: mañana, 2026-05-15)")
    preferred_time: str = Field(description="Hora preferida (ej: 10:00, mañana en la tarde)")

llm = init_chat_model("openai:gpt-4o", temperature=0)
llm = llm.with_structured_output(schema=AppointmentData)

# Horario laboral: 8:00 AM - 6:00 PM (08:00 - 18:00)
BUSINESS_HOURS_START = 8
BUSINESS_HOURS_END = 18

def _validar_hora_laboral(hora_str: str) -> bool:
    """
    Valida que la hora esté dentro del horario laboral (8 AM - 6 PM).
    Acepta formatos: "10:00", "10 am", "10 pm", "10:30", "mañana a las 10", etc.
    Retorna True si es válida, False si está fuera de horario.
    """
    if not hora_str:
        return False

    hora_lower = hora_str.lower().strip()

    # Buscar formato de hora (HH:MM o HH)
    hora_match = re.search(r'(\d{1,2}):?(\d{2})?', hora_lower)
    if not hora_match:
        return False

    hora = int(hora_match.group(1))

    # Si dice "pm" o "p.m." y no es 12
    if ('pm' in hora_lower or 'p.m.' in hora_lower) and hora != 12:
        hora += 12
    # Si dice "am" o "a.m." y es 12, convertir a 0
    elif ('am' in hora_lower or 'a.m.' in hora_lower) and hora == 12:
        hora = 0

    # Validar rango horario (8 AM - 6 PM = 8:00 - 18:00)
    if hora < BUSINESS_HOURS_START or hora >= BUSINESS_HOURS_END:
        return False

    return True

def extractor_datos(state: TallerState) -> dict:
    """
    Extrae datos de agendamiento del cliente usando LLM estructurado.
    Busca: nombre, teléfono, fecha, hora preferida.
    Si faltan datos, retorna un mensaje pidiendo esa información.
    """
    messages = state.get("messages", [])
    customer_name = state.get("customer_name", None)
    phone = state.get("phone", None)
    damaged_part = state.get("damaged_part", "revisión de vehículo")

    print("[EXTRACTOR_DATOS] Extrayendo información de agendamiento...")

    # Si ya tenemos datos completos, no extraemos (verificar TODOS los datos)
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")

    if customer_name and phone and preferred_date and preferred_time:
        print("[EXTRACTOR_DATOS] ✓ Datos ya completos")
        return {
            "missing_fields": [],
            "appointment_data": {
                "customer_name": customer_name,
                "phone": phone,
                "preferred_date": preferred_date,
                "preferred_time": preferred_time,
                "service": damaged_part
            }
        }

    # Extraer datos del historial usando LLM estructurado
    try:
        system_prompt = """Eres un asistente que extrae información de agendamiento de una conversación.

Extrae SOLO si están explícitamente mencionados en la conversación:
- nombre: nombre completo del cliente
- phone: número de teléfono (cualquier secuencia de dígitos)
- preferred_date: fecha preferida mencionada (ej: mañana, 2026-05-15, próxima semana)
- preferred_time: hora preferida mencionada (ej: 10:00, por la tarde, por la mañana)

Si NO encuentras algo, retorna un string vacío "" para ese campo. NO uses valores por defecto."""

        # Convertir mensajes a formato compatible
        formatted_messages = [("system", system_prompt)]
        for m in messages:
            if isinstance(m, dict):
                role = m.get("type", "user")
                content = m.get("content", "")
            else:
                role = getattr(m, "type", "user")
                content = getattr(m, "content", "")
            formatted_messages.append((role, content))

        schema = llm.invoke(formatted_messages)

        print(f"[EXTRACTOR_DATOS] Extraído: nombre='{schema.customer_name}' | teléfono='{schema.phone}' | fecha='{schema.preferred_date}' | hora='{schema.preferred_time}'")

        # Verificar qué datos faltan o son inválidos
        missing_fields = []
        if not schema.customer_name or schema.customer_name.strip() == "":
            missing_fields.append("customer_name")
        if not schema.phone or schema.phone.strip() == "":
            missing_fields.append("phone")
        if not schema.preferred_date or schema.preferred_date.strip() == "":
            missing_fields.append("preferred_date")
        if not schema.preferred_time or schema.preferred_time.strip() == "":
            missing_fields.append("preferred_time")
        elif not _validar_hora_laboral(schema.preferred_time):
            # La hora está fuera de horario laboral
            print(f"[EXTRACTOR_DATOS] ⚠️ Hora fuera de horario: {schema.preferred_time}")
            missing_fields.append("preferred_time")
            # Mostrar mensaje específico sobre horario inválido
            if "preferred_time_invalid" not in missing_fields:
                missing_fields.append("preferred_time_invalid")

        # Si faltan datos críticos, pedir que se proporcionen
        if missing_fields:
            print(f"[EXTRACTOR_DATOS] ⚠️ Campos faltantes: {missing_fields}")
            result = {
                "missing_fields": missing_fields,  # Reset to current missing fields (not accumulated)
            }
            # Guardar los datos que SÍ tenemos
            if schema.customer_name and schema.customer_name.strip():
                result["customer_name"] = schema.customer_name
            if schema.phone and schema.phone.strip():
                result["phone"] = schema.phone
            result["appointment_data"] = {
                "preferred_date": schema.preferred_date.strip() if schema.preferred_date else "",
                "preferred_time": schema.preferred_time.strip() if schema.preferred_time else "",
                "service": damaged_part,
            }
            return result

        # Si tenemos TODOS los datos, retornar datos completos
        print(f"[EXTRACTOR_DATOS] ✓ Todos los datos extraídos correctamente")
        return {
            "customer_name": schema.customer_name,
            "phone": schema.phone,
            "missing_fields": [],  # Limpiar missing_fields
            "appointment_data": {
                "customer_name": schema.customer_name,
                "phone": schema.phone,
                "preferred_date": schema.preferred_date,
                "preferred_time": schema.preferred_time,
                "service": damaged_part,
            }
        }
    except Exception as e:
        print(f"[EXTRACTOR_DATOS] ❌ Error: {e}")
        return {}
