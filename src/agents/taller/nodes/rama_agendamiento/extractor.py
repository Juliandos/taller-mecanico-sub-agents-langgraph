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

def _parse_date_string(date_str: str, rejected_date: str = None) -> datetime:
    """
    Convierte strings de fecha a datetime.
    Soporta: "mañana", "18 de mayo", "martes 19", "el día siguiente", "2026-05-15", etc.
    Retorna None si no puede parsear.
    Si rejected_date se proporciona, puede interpretar "el día siguiente" relativamente.
    """
    if not date_str or date_str.strip() == "":
        return None

    date_lower = date_str.lower().strip()

    # Reemplazar caracteres especiales
    date_lower = date_lower.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    # Caso 0: Fechas relativas al día rechazado (cuando hay festivo)
    if rejected_date:
        rejected_parsed = _parse_date_string(rejected_date, None)
        if rejected_parsed:
            relative_keywords = [
                "el dia siguiente", "el siguiente", "dia despues", "dia siguiente",
                "siguiente", "despues", "al dia siguiente", "al siguiente", "mañana entonces"
            ]
            for keyword in relative_keywords:
                if keyword in date_lower:
                    return rejected_parsed + timedelta(days=1)

    # Caso 1: "mañana" = hoy + 1 día
    if date_lower == "manana":
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

def _validar_hora_laboral(hora_str: str, fecha_str: str = "", rejected_date: str = None) -> tuple:
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
        fecha_parsed = _parse_date_string(fecha_str, rejected_date)
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


def _detectar_seleccion_mecanico(last_human_msg: str, mechanics_list: list) -> tuple:
    """
    Detecta si el usuario seleccionó un mecánico sin usar LLM.
    Retorna (nombre_mecanico, "Diagnóstico") o (None, None) si no detecta selección.
    """
    if not last_human_msg or not mechanics_list:
        return (None, None)

    # Manejar mensajes multimodales (pueden ser listas de dicts)
    if isinstance(last_human_msg, list):
        text_content = ""
        for item in last_human_msg:
            if isinstance(item, dict) and item.get("type") == "text":
                text_content = item.get("text", "")
                break
        last_human_msg = text_content

    if not last_human_msg:
        return (None, None)

    msg_lower = str(last_human_msg).lower().strip()
    msg_lower = msg_lower.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    # Palabras de aceptación (selecciona el primero/recomendado)
    accept_keywords = [
        "cualquiera", "ok", "bien", "esta bien", "el recomendado", "el primero",
        "me parece bien", "esta ok", "listo", "vale", "claro", "me gusta", "perfecto"
    ]
    for keyword in accept_keywords:
        if keyword in msg_lower:
            first_mechanic = mechanics_list[0]["nombre"] if mechanics_list else "Juan García"
            return (first_mechanic, "Diagnóstico")

    # Detectar números (1-5)
    numero_patterns = [
        (r"\b1\b", 0), (r"\buno\b", 0),
        (r"\b2\b", 1), (r"\bdos\b", 1),
        (r"\b3\b", 2), (r"\btres\b", 2),
        (r"\b4\b", 3), (r"\bcuatro\b", 3),
        (r"\b5\b", 4), (r"\bcinco\b", 4),
    ]
    for pattern, idx in numero_patterns:
        if re.search(pattern, msg_lower):
            if idx < len(mechanics_list):
                return (mechanics_list[idx]["nombre"], "Diagnóstico")

    # Detectar nombres de mecánicos
    mechanic_names = ["juan", "maria", "carlos", "ana", "roberto"]
    for mech in mechanics_list:
        first_name = mech["nombre"].split()[0].lower()
        first_name = first_name.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        if first_name in msg_lower or mech["nombre"].lower() in msg_lower:
            return (mech["nombre"], "Diagnóstico")

    return (None, None)


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

        # Detectar selección de mecánico incluso si los datos básicos están completos
        selected_mechanic = state.get("selected_mechanic", "")
        selected_area = state.get("selected_area", "")
        mecanicos_disponibles = state.get("mecanicos_disponibles", [])
        missing_fields = []

        if mecanicos_disponibles and not selected_mechanic:
            # Intentar detectar selección de mecánico del último mensaje
            last_message = ""
            if messages:
                last = messages[-1]
                if isinstance(last, dict):
                    last_message = last.get("content", "")
                elif hasattr(last, "content"):
                    last_message = last.content

                # Si es multimodal, extraer texto
                if isinstance(last_message, list):
                    for item in last_message:
                        if isinstance(item, dict) and item.get("type") == "text":
                            last_message = item.get("text", "")
                            break
                    else:
                        # Si no encontramos texto en multimodal, usar vacío
                        last_message = ""
                else:
                    # Asegurar que es string
                    last_message = str(last_message) if last_message else ""

            detected_mechanic, detected_area = _detectar_seleccion_mecanico(last_message, mecanicos_disponibles)

            if detected_mechanic:
                selected_mechanic = detected_mechanic
                selected_area = detected_area or "Diagnóstico"
                print(f"[EXTRACTOR_DATOS] ✓ Mecánico seleccionado: {selected_mechanic}")
            else:
                # Si no detecta selección, pedir que seleccione
                missing_fields.append("select_mechanic")
                print(f"[EXTRACTOR_DATOS] ⚠️ Pendiente selección de mecánico")

        # Si falta selección de mecánico, pedir antes de agendar
        if missing_fields:
            return {
                "missing_fields": missing_fields,
                "customer_name": customer_name,
                "phone": phone,
                "selected_mechanic": selected_mechanic,
                "selected_area": selected_area,
                "appointment_data": {
                    "customer_name": customer_name,
                    "phone": phone,
                    "preferred_date": preferred_date,
                    "preferred_time": preferred_time,
                    "service": damaged_part
                }
            }

        return {
            "missing_fields": [],
            "customer_name": customer_name,
            "phone": phone,
            "selected_mechanic": selected_mechanic,
            "selected_area": selected_area,
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

        # Obtener la fecha rechazada anterior (si la hay)
        rejected_date = state.get("rejected_date", None)

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
            # Validar hora considerando la fecha (pasando rejected_date para interpretar "el día siguiente")
            is_valid, error_type, extra_info = _validar_hora_laboral(
                schema.preferred_time,
                schema.preferred_date,
                rejected_date
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

        # Detectar selección de mecánico si disponibilidad ya fue consultada
        selected_mechanic = state.get("selected_mechanic", "")
        selected_area = state.get("selected_area", "")
        mecanicos_disponibles = state.get("mecanicos_disponibles", [])

        if mecanicos_disponibles and not selected_mechanic:
            # Intentar detectar selección de mecánico del último mensaje
            last_message = ""
            if messages:
                last = messages[-1]
                if isinstance(last, dict):
                    last_message = last.get("content", "")
                elif hasattr(last, "content"):
                    last_message = last.content

                # Si es multimodal, extraer texto
                if isinstance(last_message, list):
                    for item in last_message:
                        if isinstance(item, dict) and item.get("type") == "text":
                            last_message = item.get("text", "")
                            break
                    else:
                        # Si no encontramos texto en multimodal, usar vacío
                        last_message = ""
                else:
                    # Asegurar que es string
                    last_message = str(last_message) if last_message else ""

            detected_mechanic, detected_area = _detectar_seleccion_mecanico(last_message, mecanicos_disponibles)

            if detected_mechanic:
                selected_mechanic = detected_mechanic
                selected_area = detected_area or "Diagnóstico"
                print(f"[EXTRACTOR_DATOS] ✓ Mecánico seleccionado: {selected_mechanic}")
            elif not missing_fields:
                # Si tenemos todos los datos básicos pero sin selección de mecánico
                missing_fields.append("select_mechanic")
                print(f"[EXTRACTOR_DATOS] ⚠️ Pendiente selección de mecánico")

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
            if selected_mechanic:
                result["selected_mechanic"] = selected_mechanic
                result["selected_area"] = selected_area
            result["appointment_data"] = {
                "preferred_date": schema.preferred_date.strip() if schema.preferred_date else "",
                "preferred_time": schema.preferred_time.strip() if schema.preferred_time else "",
                "service": damaged_part,
            }
            # Si hay un error de festivo, guardar la fecha rechazada para interpretar "el día siguiente"
            if any(f.startswith("preferred_date_holiday:") for f in missing_fields):
                fecha_parsed = _parse_date_string(schema.preferred_date, rejected_date)
                if fecha_parsed:
                    result["rejected_date"] = fecha_parsed.strftime("%Y-%m-%d")
                    print(f"[EXTRACTOR_DATOS] 📅 Fecha rechazada guardada: {result['rejected_date']}")
            return result

        # Si tenemos TODOS los datos, retornar datos completos
        print(f"[EXTRACTOR_DATOS] ✓ Todos los datos extraídos correctamente")
        return {
            "customer_name": schema.customer_name,
            "phone": schema.phone,
            "missing_fields": [],  # Limpiar missing_fields
            "selected_mechanic": selected_mechanic,
            "selected_area": selected_area,
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
