"""Consultar disponibilidad de taller - RAG simulado de horarios y servicios."""

from agents.taller.state import TallerState
from agents.taller.data_mecanicos import get_mecanicos
from agents.taller.nodes.rama_agendamiento.simulated_availability import (
    get_service_areas,
    get_available_dates,
    get_available_slots_for_date,
    format_availability_display,
)
from datetime import datetime
import json


def consultar_disponibilidad_taller(state: TallerState) -> dict:
    """
    Consulta RAG simulada de disponibilidad del taller.
    - 5 mecánicos con especialidades variadas
    - 6 áreas de servicio
    - Disponibilidades para 15 días (excluyendo domingos y festivos colombianos)
    """
    print(f"[CONSULTAR_DISPONIBILIDAD] Consultando disponibilidad del taller...")

    # Obtener datos centralizados
    mechanics = get_mecanicos()
    service_areas = get_service_areas()
    available_dates = get_available_dates(15)

    # Formatear mecánicos
    mecanicos_info = "\n".join([
        f"- {m['nombre']} ({m['especialidad_principal']}) - {m['experiencia_anos']} años de experiencia"
        for m in mechanics
    ])

    # Formatear áreas de servicio
    areas_info = "\n".join([
        f"- {a['nombre']}: {a['tipo']}"
        for a in service_areas
    ])

    # Formatear fechas disponibles (próximos 15 días)
    dates_info = "\n".join([
        f"  {'✅' if available else '❌'} {formatted}"
        for date, formatted, available in available_dates[:10]  # Mostrar primeras 10
    ])

    # Construir pregunta de selección de mecánico
    mecanicos_numerados = "\n".join([
        f"   {i}. {m['nombre']} ({m['especialidad_principal']})"
        for i, m in enumerate(mechanics, 1)
    ])

    # Construir respuesta formateada
    disponibilidad_info = f"""
╔════════════════════════════════════════════════════════════╗
║         📅 DISPONIBILIDAD TALLER MECÁNICO 2026             ║
╚════════════════════════════════════════════════════════════╝

⏰ HORARIOS GENERALES:
  • Lunes a Viernes: 08:00 - 18:00
  • Sábado: 09:00 - 14:00
  • Domingo: ❌ CERRADO
  • Festivos Colombianos: ❌ CERRADO

👨‍🔧 MECÁNICOS DISPONIBLES (5):
{mecanicos_info}

🔧 ÁREAS DE SERVICIO (6):
{areas_info}

📅 FECHAS DISPONIBLES (próximos 15 días):
{dates_info}

💡 Nota: El Lunes 18 de mayo es festivo (Lunes de Pentecostés) - CERRADO

---

👨‍🔧 ¿CON CUÁL MECÁNICO TE GUSTARÍA TRABAJAR?
{mecanicos_numerados}

Responde con el número (1-5) o di "cualquiera" / "está bien" si te parece bien el recomendado.
"""

    print(f"[CONSULTAR_DISPONIBILIDAD] ✅ Información recuperada")
    print(f"[CONSULTAR_DISPONIBILIDAD] Mecánicos: {len(mechanics)}")
    print(f"[CONSULTAR_DISPONIBILIDAD] Áreas de servicio: {len(service_areas)}")
    print(f"[CONSULTAR_DISPONIBILIDAD] Fechas disponibles: {len([d for d in available_dates if d[2]])}")

    consultas_count = state.get("consultas_disponibilidad", 0) + 1

    return {
        "disponibilidad_context": disponibilidad_info,
        "mecanicos_disponibles": mechanics,
        "puestos_servicio": service_areas,
        "servicios": [
            "Diagnóstico completo",
            "Cambio de bujías y filtros",
            "Reparación de motor",
            "Revisión de frenos",
            "Alineación y balanceo de llantas",
            "Reparación de suspensión",
            "Reparación de transmisión",
            "Reparación eléctrica",
            "Aire acondicionado",
            "Mantenimiento general",
        ],
        "consultas_disponibilidad": consultas_count,
    }
