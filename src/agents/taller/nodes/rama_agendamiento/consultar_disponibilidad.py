"""Consultar disponibilidad de taller - RAG simulado de horarios y servicios."""

from agents.taller.state import TallerState
import json


def consultar_disponibilidad_taller(state: TallerState) -> dict:
    """
    Simula una consulta RAG a base de datos de disponibilidad del taller.
    Consulta: horarios de mecánicos, puestos de servicio, servicios disponibles.
    """
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")
    preferred_time = appointment_data.get("preferred_time", "")

    print(f"[CONSULTAR_DISPONIBILIDAD] Consultando taller para {preferred_date} a las {preferred_time}")

    # RAG simulado - Base de datos del taller
    taller_info = {
        "horarios": {
            "lunes_viernes": "08:00 - 18:00",
            "sabado": "09:00 - 14:00",
            "domingo": "CERRADO",
        },
        "mecanicos": [
            {
                "nombre": "Juan García",
                "especialidad": "Motor, suspensión, transmisión",
                "experiencia": "15 años",
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
                "nombre": "María López",
                "especialidad": "Frenos, suspensión, dirección",
                "experiencia": "12 años",
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
        "puestos_servicio": [
            {"puesto": 1, "tipo": "Diagnóstico", "disponible": True},
            {"puesto": 2, "tipo": "Motor y transmisión", "disponible": True},
            {"puesto": 3, "tipo": "Frenos y suspensión", "disponible": True},
            {"puesto": 4, "tipo": "Dirección y alineación", "disponible": True},
        ],
        "servicios": [
            "Cambio de bujías",
            "Cambio de filtros",
            "Revisión de frenos",
            "Alineación de dirección",
            "Reparación de suspensión",
            "Diagnóstico completo",
            "Reparación de transmisión",
        ],
    }

    # Formatear información disponible
    mecanicos_disponibles = "\n".join([
        f"- {m['nombre']} ({m['especialidad']}) - {m['experiencia']} de experiencia"
        for m in taller_info["mecanicos"]
    ])

    puestos_info = "\n".join([
        f"- Puesto {p['puesto']}: {p['tipo']} {'✓ Disponible' if p['disponible'] else '✗ Ocupado'}"
        for p in taller_info["puestos_servicio"]
    ])

    disponibilidad_info = f"""
╔════════════════════════════════════════╗
║    DISPONIBILIDAD TALLER MECÁNICO      ║
╚════════════════════════════════════════╝

📅 HORARIOS:
- Lunes a Viernes: {taller_info['horarios']['lunes_viernes']}
- Sábado: {taller_info['horarios']['sabado']}
- Domingo: {taller_info['horarios']['domingo']}

👨‍🔧 MECÁNICOS DISPONIBLES:
{mecanicos_disponibles}

🔧 PUESTOS DE SERVICIO:
{puestos_info}

✅ SERVICIOS DISPONIBLES:
{", ".join(taller_info['servicios'])}
"""

    print(f"[CONSULTAR_DISPONIBILIDAD] ✅ Información recuperada")

    consultas_count = state.get("consultas_disponibilidad", 0) + 1

    return {
        "disponibilidad_context": disponibilidad_info,
        "mecanicos_disponibles": taller_info["mecanicos"],
        "puestos_servicio": taller_info["puestos_servicio"],
        "servicios": taller_info["servicios"],
        "consultas_disponibilidad": consultas_count,
    }
