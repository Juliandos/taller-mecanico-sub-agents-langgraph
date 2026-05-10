"""Tools para el React Agent de agendamiento."""

AREAS_SERVICIO = [
    "Motor",
    "Frenos",
    "Suspensión",
    "Dirección",
    "Diagnóstico",
]

TALLER_DATA = {
    "horarios": {
        "lunes_viernes": "08:00 - 18:00",
        "sabado": "09:00 - 14:00",
        "domingo": "CERRADO",
    },
    "mecanicos": [
        {
            "id": "MEX001",
            "nombre": "Juan García",
            "especialidad": "Motor, suspensión",
            "disponibilidad": {
                "lunes": ["09:00", "10:00", "14:00", "15:00"],
                "martes": ["09:00", "11:00", "14:00", "16:00"],
                "miercoles": ["10:00", "15:00", "16:00"],
                "jueves": ["09:00", "10:00", "11:00", "14:00"],
                "viernes": ["13:00", "14:00", "15:00", "16:00"],
                "sabado": ["09:00", "10:00", "11:00", "12:00"],
            }
        },
        {
            "id": "MEX002",
            "nombre": "María López",
            "especialidad": "Frenos, dirección",
            "disponibilidad": {
                "lunes": ["10:00", "11:00", "15:00", "16:00"],
                "martes": ["09:00", "10:00", "13:00", "14:00"],
                "miercoles": ["09:00", "11:00", "14:00", "15:00"],
                "jueves": ["10:00", "14:00", "16:00"],
                "viernes": ["09:00", "10:00", "14:00"],
                "sabado": ["10:00", "11:00", "13:00"],
            }
        },
    ],
    "puestos": [
        {"id": "PUESTO-1", "tipo": "Diagnóstico", "disponible": True},
        {"id": "PUESTO-2", "tipo": "Motor", "disponible": True},
        {"id": "PUESTO-3", "tipo": "Frenos", "disponible": True},
        {"id": "PUESTO-4", "tipo": "Dirección", "disponible": True},
    ],
}


def listar_areas_servicio():
    """Retorna las 5 áreas de servicio disponibles."""
    print("[TOOL] listar_areas_servicio() llamada")
    return {"areas_disponibles": AREAS_SERVICIO}


def consultar_disponibilidad(fecha: str, hora: str):
    """Consulta disponibilidad de mecánicos y puestos."""
    print(f"[TOOL] consultar_disponibilidad({fecha}, {hora})")

    mecanicos_disponibles = []
    for mecanico in TALLER_DATA["mecanicos"]:
        disponible_en_horario = False
        for dia, horas in mecanico["disponibilidad"].items():
            if hora in horas:
                disponible_en_horario = True
                break
        if disponible_en_horario:
            mecanicos_disponibles.append({
                "id": mecanico["id"],
                "nombre": mecanico["nombre"],
                "especialidad": mecanico["especialidad"]
            })

    return {
        "fecha_solicitada": fecha,
        "hora_solicitada": hora,
        "mecanicos_disponibles": mecanicos_disponibles,
        "horarios_taller": TALLER_DATA["horarios"],
        "disponibilidad_confirmada": len(mecanicos_disponibles) > 0
    }


def crear_cita(cliente_nombre: str, cliente_telefono: str, fecha: str, hora: str, area_servicio: str):
    """Crea la cita con todos los datos."""
    print(f"[TOOL] crear_cita({cliente_nombre}, {fecha}, {hora})")
    import random
    confirmation_id = f"TM-{random.randint(10000, 99999)}"

    return {
        "confirmacion_id": confirmation_id,
        "cliente_nombre": cliente_nombre,
        "cliente_telefono": cliente_telefono,
        "fecha": fecha,
        "hora": hora,
        "area_servicio": area_servicio,
        "mecanico": "Juan García",
        "especialidad": "Motor, suspensión",
        "costo_estimado": "$150,000-350,000",
        "exito": True
    }
