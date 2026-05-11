"""Extractor de datos para agendamiento de citas."""

import re
from datetime import datetime, timedelta
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from agents.taller.state import TallerState
from agents.taller.nodes.rama_agendamiento.simulated_availability import is_holiday

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

# Hoy es 11 de mayo de 2026
TODAY = datetime(2026, 5, 11)

# Mapeo de periodos a horas
TIME_PERIODS = {
    "mañana": {"start": 8, "end": 12, "label": "08:00 - 12:00"},
    "tarde": {"start": 14, "end": 18, "label": "14:00 - 18:00"},
    "mañanita": {"start": 8, "end": 12, "label": "08:00 - 12:00"},
    "por la mañana": {"start": 8, "end": 12, "label": "08:00 - 12:00"},
    "por la tarde": {"start": 14, "end": 18, "label": "14:00 - 18:00"},
    "temprano": {"start": 8, "end": 10, "label": "08:00 - 10:00"},
}

def _parse_date_string(date_str: str) -> datetime:
    """
    Convierte strings de fecha a datetime.
    Soporta: "mañana", "18 de mayo", "martes 19", "2026-05-15", etc.
    Retorna None si no puede parsear.
    """
    if not date_str or date_str.strip() == "":
        return None

    date_lower = date_str.lower().strip()

    # Reemplazar caracteres especiales
    date_lower = date_lower.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    # Caso 1: "mañana" = hoy + 1 día
    if date_lower == "manana" or date_lower == "mañana":
        return TODAY + timedelta(days=1)

    # Caso 2: Formato ISO "2026-05-15"
    if re.match(r"\d{4}-\d{2}-\d{2}", date_lower):
        try:
            return datetime.strptime(date_lower, "%Y-%m-%d")
        except:
            return None

    # Caso 3: "18 de mayo" o "18 mayo"
    day_month_match = re.search(r"(\d{1,2})\s+(?:de\s+)?(\w+)", date_lower)
    if day_month_match:
        day = int(day_month_match.group(1))
        month_str = day_month_match.group(2)

        months = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }

        if month_str in months:
            month = months[month_str]
            try:
                return datetime(2026, month, day)
            except:
                return None

    # Caso 4: "martes 19" o "miercoles 20"
    day_match = re.search(r"(\d{1,2})", date_lower)
    if day_match:
        day = int(day_match.group(1))
        try:
            return datetime(2026, 5, day)
        except:
            return None

    return None

def _check_holiday(date: datetime) -> tuple:
    """
    Verifica si una fecha es festivo.
    Retorna (is_holiday: bool, holiday_name: str)
    """
    if is_holiday(date):
        date_str = date.strftime("%Y-%m-%d")
        from agents.taller.nodes.rama_agendamiento.simulated_availability import COLOMBIAN_HOLIDAYS
        holiday_name = COLOMBIAN_HOLIDAYS.get(date_str, "Festivo")
        return (True, holiday_name)
    return (False, "")

def _validar_hora_laboral(hora_str: str, fecha_str: str = "") -> tuple:
    """
    Valida que la hora esté dentro del horario laboral.
    Retorna (is_valid: bool, error_type: str, available_times: str)
    error_type: "holiday", "time_period_needs_hour", "invalid_hour", "valid"
    """
    if not hora_str:
        return (False, "missing_time", "")

    hora_lower = hora_str.lower().strip()
    hora_lower = hora_lower.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    # Primero, verificar si la fecha es festivo
    if fecha_str:
        fecha_parsed = _parse_date_string(fecha_str)
        if fecha_parsed:
            is_hol, holiday_name = _check_holiday(fecha_parsed)
            if is_hol:
                return (False, "holiday", holiday_name)

    # Verificar si es un periodo de tiempo (mañana, tarde, etc.)
    for period, info in TIME_PERIODS.items():
        if period in hora_lower:
            # Es un periodo de tiempo, necesita hora específica
            return (False, "time_period_needs_hour", info["label"])

    # Buscar formato de hora (HH:MM o HH)
    hora_match = re.search(r'(\d{1,2}):?(\d{2})?', hora_lower)
    if not hora_match:
        return (False, "invalid_hour", "")

    hora = int(hora_match.group(1))

    # Si dice "pm" o "p.m." y no es 12
    if ('pm' in hora_lower or 'p.m.' in hora_lower) and hora != 12:
        hora += 12
    # Si dice "am" o "a.m." y es 12, convertir a 0
    elif ('am' in hora_lower or 'a.m.' in hora_lower) and hora == 12:
        hora = 0

    # Validar rango horario (8 AM - 6 PM = 8:00 - 18:00)
    if hora < BUSINESS_HOURS_START or hora >= BUSINESS_HOURS_END:
        return (False, "invalid_hour", "")

    return (True, "valid", "")

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
        else:
            # Validar hora considerando la fecha
            is_valid, error_type, extra_info = _validar_hora_laboral(
                schema.preferred_time,
                schema.preferred_date
            )
            if not is_valid:
                print(f"[EXTRACTOR_DATOS] ⚠️ Error de hora/fecha: {error_type} - {schema.preferred_time}")
                missing_fields.append("preferred_time")

                # Agregar marcas especiales según el tipo de error
                if error_type == "holiday":
                    missing_fields.append(f"preferred_date_holiday:{extra_info}")
                elif error_type == "time_period_needs_hour":
                    missing_fields.append(f"time_period:{extra_info}")
                elif error_type == "invalid_hour":
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
