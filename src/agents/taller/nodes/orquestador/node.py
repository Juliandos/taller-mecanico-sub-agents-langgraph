"""Nodo Orquestador - Evalúa intención y enruta a ramas"""

import re
from agents.taller.state import TallerState
from langchain_core.messages import AIMessage


def find_keywords(text: str, keywords: list) -> bool:
    """
    Busca palabras clave de forma robusta en un texto.
    Ignora: mayúsculas, espacios múltiples, puntuación.

    Ejemplos:
    - text="Tengo UN PROBLEMA!" keywords=["problema"] → True
    - text="Quiero  agendar" keywords=["agend"] → True
    - text="¿Mañana  a las 3?" keywords=["mañana"] → True
    """
    # Normalizar: minúsculas, múltiples espacios → 1, eliminar puntuación
    clean = re.sub(r'\s+', ' ', text.lower().strip())
    clean = re.sub(r'[.,!?;:\-—¿¡]', '', clean)

    # Buscar si alguna palabra clave está contenida
    return any(kw in clean for kw in keywords)


def orquestador(state: TallerState) -> dict:
    """
    Orquestador: Analiza el mensaje y decide a qué rama enviar.
    - Si habla de problemas/síntomas → RAMA 1 (Diagnóstico)
    - Si habla de agendar/cita → RAMA 2 (Agendamiento)
    - Pueden ser ambas
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    # Extrae content del último mensaje (maneja dicts, Message objects, y listas)
    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        content = last_msg.get("content", "")
    else:
        content = last_msg.content if hasattr(last_msg, "content") else ""

    # Si content es lista, concatenar
    if isinstance(content, list):
        content = " ".join(str(c) if not isinstance(c, str) else c for c in content)

    last_message = str(content)

    # 🔧 PALABRAS CLAVE PARA DIAGNÓSTICO (síntomas, problemas)
    symptom_keywords = [
        # Problemas generales
        "problema", "falla", "daño", "error", "avería", "mal funcionamiento",
        "no funciona", "defecto", "rotura", "quiebre", "ruptura",

        # Ruidos y vibraciones
        "ruido", "vibra", "vibración", "vibrar", "sonido extraño", "ruidos extraños",
        "rechina", "cruje", "golpe", "golpea", "taqueo", "taquea",

        # Problemas del motor
        "motor", "tose", "tiembla", "calienta", "se sobrecalienta", "humo", "vapor",
        "olor", "quemado", "gasolina", "aceite", "refrigerante",

        # Problemas de rendimiento
        "pierde potencia", "potencia", "aceleración", "acelera", "no acelera",
        "lento", "no arranca", "arranca", "cuesta arrancar", "difícil arrancar",
        "para", "se apaga", "se detiene", "pérdida", "consumo",

        # Frenos
        "freno", "frenada", "recorre", "pisa freno", "frena", "no frena",

        # Suspensión y dirección
        "suspensión", "rebote", "rebota", "dirección", "volante", "dirección pesada",
        "dirección fácil", "tira a un lado", "desviación",

        # Llantas
        "llanta", "neumático", "pinchazo", "pinchada", "desinflada", "llanta plana",
        "neumáticos", "vibración en la dirección",

        # Inglés y sinónimos
        "issue", "problem", "malfunction", "symptom", "malfunction", "broken",
        "doesn't work", "not working", "failure", "trouble",

        # Palabras de confirmación de síntoma
        "síntoma", "síntomas", "ayuda", "diagnóstico", "diagnostico", "diagnose",
        "revisar", "chequear", "check", "revisor", "mecánico",
    ]

    # 📅 PALABRAS CLAVE PARA FECHAS Y HORARIOS
    date_keywords = [
        # Fechas relativas
        "hoy", "mañana", "pasado mañana", "pasado", "próximo", "siguiente",
        "próxima semana", "esta semana", "el próximo", "el siguiente",

        # Días de la semana
        "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo",
        "semana", "fin de semana",

        # Meses
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic",

        # Años y períodos
        "2024", "2025", "2026", "2027", "este año", "próximo año",

        # Períodos del día
        "mañana", "tarde", "noche", "madrugada", "mediodía",
        "mañana por la mañana", "por la tarde", "por la noche",

        # Horas en formato HH:MM (14:00, 09:30, etc)
        "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
        "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "20", "21", "22", "23",
        "en punto", ":00", ":30", ":15", ":45",

        # 🕐 HORAS EXPLÍCITAS CON AM/PM
        # AM: 1am, 2am, 3am, ..., 12am (y variantes con :00, :30)
        "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", "10am", "11am", "12am",
        "1:00am", "2:00am", "3:00am", "4:00am", "5:00am", "6:00am", "7:00am", "8:00am", "9:00am",
        "10:00am", "11:00am", "12:00am",
        "1:30am", "2:30am", "3:30am", "4:30am", "5:30am", "6:30am", "7:30am", "8:30am", "9:30am",
        "10:30am", "11:30am", "12:30am",

        # PM: 1pm, 2pm, 3pm, ..., 12pm (y variantes con :00, :30)
        "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm", "12pm",
        "1:00pm", "2:00pm", "3:00pm", "4:00pm", "5:00pm", "6:00pm", "7:00pm", "8:00pm", "9:00pm",
        "10:00pm", "11:00pm", "12:00pm",
        "1:30pm", "2:30pm", "3:30pm", "4:30pm", "5:30pm", "6:30pm", "7:30pm", "8:30pm", "9:30pm",
        "10:30pm", "11:30pm", "12:30pm",
    ]

    # 🔖 PALABRAS CLAVE PARA AGENDAMIENTO (citas, reservas)
    booking_keywords = [
        # Citas y agendamiento
        "cita", "citas", "agendar", "agend", "agenda", "agendada",
        "reserva", "reserv", "reservación", "reservar",
        "appointment", "booking", "book", "schedule", "scheduled",

        # Disponibilidad
        "disponibilidad", "disponible", "disponibilidades", "disponibles",
        "horario", "horarios", "turno", "turnos",

        # Programación
        "programar", "programación", "programado", "cuando", "cuándo",

        # Calendario
        "calendario", "calendarizar", "fecha", "fechas", "hora", "horas",

        # Confirmación de agendamiento
        "confirma", "confirmación", "confirmada", "agendar", "agendado",
        "reservada", "booked", "scheduled",

        # Modificación (específico a citas, no genérico)
        "cambiar cita", "cambiar fecha", "cambiar hora", "cambiar turno",
        "modificar cita", "reprogramar cita", "reprogramar",

        # Variaciones
        "necesito cita", "quiero cita", "dame cita", "una cita", "una reserva",
        "necesito reserva", "necesito turno", "solicitar cita", "solicitar turno",
    ]

    # Detectar intención usando find_keywords
    has_symptom = find_keywords(last_message, symptom_keywords)
    has_booking = find_keywords(last_message, booking_keywords)
    has_date = find_keywords(last_message, date_keywords)

    print(f"[ORQUESTADOR] has_symptom={has_symptom}, has_booking={has_booking}, has_date={has_date}")

    # Retornar decisión
    routes = []
    if has_symptom:
        routes.append("rama_diagnostico")
    if has_booking or has_date:  # Si menciona fechas/horarios → agendamiento
        routes.append("rama_agendamiento")
    if not routes:
        routes = ["rama_diagnostico"]  # default

    print(f"[ORQUESTADOR] Routes asignadas: {routes}")
    return {"routes": routes}


def route_orchestrator(state: TallerState) -> str:
    """
    Función de enrutamiento - Controla flujo según estado de diagnóstico.

    Flujo:
    1. Si diagnóstico NO completo → rama_diagnostico (recolectar info)
    2. Si cliente confirmó diagnóstico → rama_agendamiento (agendar cita)
    3. Si diagnóstico completo pero NO confirmado → rama_diagnostico (esperar confirmación)
    """
    diagnosis_complete = state.get("diagnosis_complete", False)
    client_confirmed = state.get("client_confirmed_diagnosis", False)
    damaged_part = state.get("damaged_part", "")

    print(f"\n[ROUTE ORCHESTRATOR] ══════════════════════════════")
    print(f"  - diagnosis_complete: {diagnosis_complete}")
    print(f"  - client_confirmed_diagnosis: {client_confirmed}")
    print(f"  - damaged_part: {damaged_part}")

    # Si cliente ya confirmó el diagnóstico → ir a agendamiento
    if client_confirmed:
        print(f"[ROUTE ORCHESTRATOR] ✅ RUTEANDO A: rama_agendamiento")
        return "rama_agendamiento"

    # Si no hay confirmación → seguir con diagnóstico
    print(f"[ROUTE ORCHESTRATOR] 📋 RUTEANDO A: rama_diagnostico")
    return "rama_diagnostico"
