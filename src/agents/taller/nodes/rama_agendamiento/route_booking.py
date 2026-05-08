"""Router para el ciclo interno de rama 2 - Agendamiento."""

from agents.taller.state import TallerState


def route_agendamiento(state: TallerState) -> str:
    """
    Router que controla el ciclo interno de rama 2.

    Flujo:
    1. Si faltan datos (nombre, teléfono, fecha, hora) → pedir_datos_faltantes
    2. Si tiene todos los datos pero no consultó disponibilidad → consultar_disponibilidad
    3. Si tiene todos los datos y disponibilidad → booking_agent → agregador
    """
    customer_name = state.get("customer_name", "")
    phone = state.get("phone", "")
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")
    disponibilidad_context = state.get("disponibilidad_context", "")
    consultas_disponibilidad = state.get("consultas_disponibilidad", 0)
    missing_fields = state.get("missing_fields", [])

    print(f"\n[ROUTE_AGENDAMIENTO] ══════════════════════════════")
    print(f"  - customer_name: {bool(customer_name)}")
    print(f"  - phone: {bool(phone)}")
    print(f"  - preferred_date: {bool(preferred_date)}")
    print(f"  - preferred_time: {bool(preferred_time)}")
    print(f"  - tiene_disponibilidad: {bool(disponibilidad_context)}")
    print(f"  - consultas_disponibilidad: {consultas_disponibilidad}")
    print(f"  - missing_fields: {missing_fields}")

    # PRIORIDAD 1: Si hay campos marcados como faltantes, pedir
    if missing_fields:
        print(f"[ROUTE_AGENDAMIENTO] 📋 Faltan datos: {missing_fields} → PEDIR_DATOS_FALTANTES")
        return "pedir_datos_faltantes"

    # PRIORIDAD 2: Si faltan datos críticos (nombre, teléfono, fecha, hora), pedir
    if not customer_name or not phone or not preferred_date or not preferred_time:
        print(f"[ROUTE_AGENDAMIENTO] 📋 Datos incompletos → PEDIR_DATOS_FALTANTES")
        missing = []
        if not customer_name: missing.append("customer_name")
        if not phone: missing.append("phone")
        if not preferred_date: missing.append("preferred_date")
        if not preferred_time: missing.append("preferred_time")
        return "pedir_datos_faltantes"

    # PRIORIDAD 3: Si tiene datos pero no consultó disponibilidad, consultar
    if not disponibilidad_context and consultas_disponibilidad == 0:
        print(f"[ROUTE_AGENDAMIENTO] 📞 Datos OK, consultando disponibilidad → CONSULTAR_DISPONIBILIDAD")
        return "consultar_disponibilidad"

    # PRIORIDAD 4: Si tiene datos y disponibilidad, agendar
    if customer_name and phone and preferred_date and preferred_time and disponibilidad_context:
        print(f"[ROUTE_AGENDAMIENTO] ✅ Todo listo → BOOKING_AGENT → AGREGADOR")
        return "booking_agent"

    # Fallback
    print(f"[ROUTE_AGENDAMIENTO] 🔄 Estado indeterminado, consultando disponibilidad")
    return "consultar_disponibilidad"
