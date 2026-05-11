"""Datos simulados de disponibilidad del taller con festivos colombianos."""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Hoy es 11 de mayo de 2026 (domingo)
# Simulamos disponibilidad para los próximos 15 días (11-26 mayo)
TODAY = datetime(2026, 5, 11)

# Festivos colombianos en el rango de 15 días
COLOMBIAN_HOLIDAYS = {
    "2026-05-18": "Lunes de Pentecostés"  # Lunes 18 mayo
}


def is_holiday(date: datetime) -> bool:
    """Verifica si una fecha es festivo colombiano."""
    date_str = date.strftime("%Y-%m-%d")
    return date_str in COLOMBIAN_HOLIDAYS


def get_mechanics() -> List[Dict]:
    """Retorna lista de 5 mecánicos con disponibilidad variada."""
    mechanics = [
        {
            "id": "M001",
            "nombre": "Juan García",
            "especialidad": "Motor, suspensión, transmisión",
            "experiencia": "15 años",
            "telefono": "+57 310-123-4567",
            "horarios_base": ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"],
        },
        {
            "id": "M002",
            "nombre": "María López",
            "especialidad": "Frenos, suspensión, dirección",
            "experiencia": "12 años",
            "telefono": "+57 310-234-5678",
            "horarios_base": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"],
        },
        {
            "id": "M003",
            "nombre": "Carlos Ruiz",
            "especialidad": "Eléctrica, diagnóstico, motor",
            "experiencia": "18 años",
            "telefono": "+57 310-345-6789",
            "horarios_base": ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"],
        },
        {
            "id": "M004",
            "nombre": "Ana Martínez",
            "especialidad": "Llantas, alineación, balanceo",
            "experiencia": "10 años",
            "telefono": "+57 310-456-7890",
            "horarios_base": ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"],
        },
        {
            "id": "M005",
            "nombre": "Roberto Sánchez",
            "especialidad": "Transmisión, caja automática, embrague",
            "experiencia": "16 años",
            "telefono": "+57 310-567-8901",
            "horarios_base": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"],
        },
    ]
    return mechanics


def get_service_areas() -> List[Dict]:
    """Retorna lista de 5+ áreas de servicio."""
    areas = [
        {
            "id": "AREA001",
            "nombre": "Puesto 1 - Diagnóstico",
            "tipo": "Diagnóstico y escaneo",
            "capacidad": 1,
        },
        {
            "id": "AREA002",
            "nombre": "Puesto 2 - Motor y transmisión",
            "tipo": "Motor, transmisión, embrague",
            "capacidad": 1,
        },
        {
            "id": "AREA003",
            "nombre": "Puesto 3 - Frenos y suspensión",
            "tipo": "Sistema de frenos, suspensión",
            "capacidad": 1,
        },
        {
            "id": "AREA004",
            "nombre": "Puesto 4 - Alineación y balanceo",
            "tipo": "Alineación, balanceo de llantas",
            "capacidad": 1,
        },
        {
            "id": "AREA005",
            "nombre": "Puesto 5 - Eléctrica y climatización",
            "tipo": "Sistema eléctrico, aire acondicionado",
            "capacidad": 1,
        },
        {
            "id": "AREA006",
            "nombre": "Puesto 6 - Mantenimiento general",
            "tipo": "Cambios, filtros, fluidos, accesorios",
            "capacidad": 2,
        },
    ]
    return areas


def get_available_slots_for_date(
    date: datetime,
    mechanic_id: str = None,
    area_id: str = None
) -> Dict[str, List[str]]:
    """
    Obtiene slots disponibles para una fecha específica.

    Reglas:
    - Domingos: CERRADO
    - Festivos: CERRADO
    - Lunes-Viernes: 08:00-18:00
    - Sábados: 09:00-14:00

    Returns: {"mecanicos": {mechanic_id: [horarios]}, "areas": {area_id: [horarios]}}
    """
    # Verificar si es domingo o festivo
    if date.weekday() == 6 or is_holiday(date):
        return {"mecanicos": {}, "areas": {}}

    mechanics = get_mechanics()
    areas = get_service_areas()

    available = {"mecanicos": {}, "areas": {}}

    # Determinar rango de horas según el día
    if date.weekday() < 5:  # Lunes-Viernes
        base_hours = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
    else:  # Sábado
        base_hours = ["09:00", "10:00", "11:00", "12:00", "13:00"]

    # Si se especifica mecánico, retornar solo ese
    if mechanic_id:
        for m in mechanics:
            if m["id"] == mechanic_id:
                # El mecánico tiene disponibilidad según su horario base
                available_hours = [h for h in m["horarios_base"] if h in base_hours]
                available["mecanicos"][mechanic_id] = available_hours
                break
    else:
        # Retornar disponibilidad de todos los mecánicos
        for m in mechanics:
            available_hours = [h for h in m["horarios_base"] if h in base_hours]
            if available_hours:
                available["mecanicos"][m["id"]] = available_hours

    # Si se especifica área, retornar solo esa
    if area_id:
        for a in areas:
            if a["id"] == area_id:
                available["areas"][area_id] = base_hours
                break
    else:
        # Retornar disponibilidad de todas las áreas
        for a in areas:
            available["areas"][a["id"]] = base_hours

    return available


def get_available_dates(days: int = 15) -> List[Tuple[datetime, str, bool]]:
    """
    Retorna lista de fechas disponibles en los próximos N días.

    Returns: [(date, formatted_string, is_available), ...]
    """
    dates = []
    for i in range(days):
        current_date = TODAY + timedelta(days=i)

        # Saltar domingo (índice 6)
        if current_date.weekday() == 6:
            continue

        is_holiday_flag = is_holiday(current_date)

        # Formatos de fecha
        day_name = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][current_date.weekday()]
        formatted = f"{day_name} {current_date.strftime('%d de %B').replace('May', 'mayo')}"

        if is_holiday_flag:
            holiday_name = COLOMBIAN_HOLIDAYS.get(current_date.strftime("%Y-%m-%d"), "Festivo")
            formatted += f" ({holiday_name})"

        dates.append((current_date, formatted, not is_holiday_flag))

    return dates


def format_availability_display(date: datetime) -> str:
    """Retorna texto formateado de disponibilidad para una fecha."""
    if is_holiday(date):
        holiday_name = COLOMBIAN_HOLIDAYS.get(date.strftime("%Y-%m-%d"), "Festivo")
        return f"❌ CERRADO - {holiday_name}"

    if date.weekday() == 6:  # Domingo
        return "❌ CERRADO - Domingo"

    if date.weekday() == 5:  # Sábado
        return "✅ Disponible 09:00 - 14:00"

    # Lunes-Viernes
    return "✅ Disponible 08:00 - 18:00"


def get_next_available_date() -> datetime:
    """Retorna la próxima fecha disponible (no domingo, no festivo)."""
    for i in range(15):
        current_date = TODAY + timedelta(days=i)
        if current_date.weekday() != 6 and not is_holiday(current_date):
            return current_date
    return None


if __name__ == "__main__":
    # Test
    print("PRÓXIMAS FECHAS DISPONIBLES (15 días):")
    print("=" * 60)
    for date, formatted, available in get_available_dates(15):
        status = "✅" if available else "❌"
        print(f"{status} {formatted}")

    print("\n" + "=" * 60)
    print("MECÁNICOS (5):")
    for m in get_mechanics():
        print(f"  - {m['nombre']} ({m['especialidad']})")

    print("\n" + "=" * 60)
    print("ÁREAS DE SERVICIO (6):")
    for a in get_service_areas():
        print(f"  - {a['nombre']}: {a['tipo']}")

    print("\n" + "=" * 60)
    print("DISPONIBILIDAD EJEMPLO (Martes 13 mayo):")
    test_date = datetime(2026, 5, 13)
    slots = get_available_slots_for_date(test_date)
    print(f"Mecánicos disponibles: {len(slots['mecanicos'])}")
    print(f"Áreas disponibles: {len(slots['areas'])}")
