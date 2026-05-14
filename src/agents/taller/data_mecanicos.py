"""
Data Mock de Mecánicos y Festivos - Base de Conocimiento Taller
"""

from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# MECÁNICOS: INFORMACIÓN COMPLETA
# ═══════════════════════════════════════════════════════════════════════════════

MECANICOS = [
    {
        "id": "MEX001",
        "nombre": "Juan García",
        "numero": "300-555-0101",
        "experiencia_anos": 15,
        "tiempo_empresa_anos": 8,
        "especialidad_principal": "Motor y Transmisión",
        "especialidades": ["Motor", "Transmisión", "Suspensión"],

        "bio": "Especialista en diagnóstico de motor con 15 años de experiencia. "
               "Juan es experto en identificar problemas complejos de transmisión "
               "y suspensión. Precisión y detalle son sus fortalezas.",

        "procesos_generales": [
            "Revisión visual de componentes",
            "Diagnóstico con escáner OBD-II",
            "Prueba de compresión",
            "Análisis de emisiones",
        ],

        "procesos_especializados": {
            "Motor": [
                "Cambio de bujías y cables de encendido",
                "Reparación de válvulas",
                "Alineación de pistones",
                "Cambio de correa de distribución",
                "Diagnóstico de fuga de aceite",
                "Limpieza de inyectores",
            ],
            "Transmisión": [
                "Cambio de aceite de transmisión",
                "Reparación de embrague",
                "Diagnóstico de cambios duros",
                "Reparación de pérdida de velocidades",
                "Sincronización de transmisión manual",
            ],
            "Suspensión": [
                "Cambio de amortiguadores",
                "Reparación de resortes",
                "Alineación de suspensión",
                "Cambio de terminales",
            ],
        },

        "diagnosticos_rag_relacionados": [
            "vibra al frenar",
            "no acelera bien",
            "pierde potencia",
            "consume mucho aceite",
            "hace ruido en motor",
        ],

        "horarios_disponibles": {
            "lunes": ["09:00", "10:00", "14:00", "15:00"],
            "martes": ["09:00", "11:00", "14:00", "16:00"],
            "miercoles": ["10:00", "15:00", "16:00"],
            "jueves": ["09:00", "10:00", "11:00", "14:00"],
            "viernes": ["13:00", "14:00", "15:00", "16:00"],
            "sabado": ["09:00", "10:00", "11:00", "12:00"],
        },
    },

    {
        "id": "MEX002",
        "nombre": "María López",
        "numero": "300-555-0102",
        "experiencia_anos": 12,
        "tiempo_empresa_anos": 6,
        "especialidad_principal": "Sistema de Frenos y Dirección",
        "especialidades": ["Frenos", "Dirección", "Suspensión"],

        "bio": "Experta en seguridad del vehículo con 12 años de experiencia. "
               "María tiene don especial para diagnosticar problemas de frenado "
               "y dirección. Muy meticulosa y paciente con clientes.",

        "procesos_generales": [
            "Inspección visual de frenos",
            "Prueba de frenada en rampa",
            "Medición de grosor de pastillas",
            "Diagnóstico de vibración",
        ],

        "procesos_especializados": {
            "Frenos": [
                "Cambio de pastillas de freno",
                "Reparación de discos de freno",
                "Sangrado de frenos hidráulicos",
                "Reparación de pinzas de freno",
                "Diagnóstico de frenada suave",
                "Cambio de líquido de frenos",
            ],
            "Dirección": [
                "Alineación de dirección",
                "Reparación de barra de dirección",
                "Cambio de cremallera de dirección",
                "Diagnóstico de timonel suelto",
                "Reparación de juego de ruedas",
            ],
            "Suspensión": [
                "Cambio de amortiguadores",
                "Reparación de brazos de suspensión",
                "Cambio de rótulas",
                "Alineación de ejes",
            ],
        },

        "diagnosticos_rag_relacionados": [
            "vibra al frenar",
            "frenos blandos",
            "dirección dura",
            "hace ruido al girar",
            "auto se va a un lado",
        ],

        "horarios_disponibles": {
            "lunes": ["10:00", "11:00", "15:00", "16:00"],
            "martes": ["09:00", "10:00", "13:00", "14:00"],
            "miercoles": ["09:00", "11:00", "14:00", "15:00"],
            "jueves": ["10:00", "14:00", "16:00"],
            "viernes": ["09:00", "10:00", "14:00"],
            "sabado": ["10:00", "11:00", "13:00"],
        },
    },

    {
        "id": "MEX003",
        "nombre": "Carlos Ruiz",
        "numero": "300-555-0103",
        "experiencia_anos": 18,
        "tiempo_empresa_anos": 10,
        "especialidad_principal": "Eléctrica y Electrónica",
        "especialidades": ["Eléctrica", "Diagnóstico", "Motor"],

        "bio": "Maestro electricista con 18 años de experiencia. Carlos es experto "
               "en diagnósticos complejos y problemas eléctricos. Conoce tecnología "
               "de vehículos modernos y clásicos.",

        "procesos_generales": [
            "Diagnóstico con escáner avanzado",
            "Prueba de batería y alternador",
            "Verificación de sistema de carga",
            "Análisis de códigos de error",
        ],

        "procesos_especializados": {
            "Eléctrica": [
                "Cambio de batería",
                "Reparación de alternador",
                "Cambio de estárter",
                "Reparación de circuitos eléctricos",
                "Diagnóstico de fusibles",
                "Reparación de cableado",
            ],
            "Diagnóstico": [
                "Lectura de códigos OBD-II",
                "Diagnóstico electrónico completo",
                "Análisis de sensores",
                "Pruebas de sistemas integrados",
                "Diagnóstico de verificación de luces",
            ],
            "Motor": [
                "Cambio de bujías",
                "Diagnóstico de falla de encendido",
                "Reparación de sistema de inyección",
                "Limpieza de inyectores electrónicos",
            ],
        },

        "diagnosticos_rag_relacionados": [
            "no enciende",
            "luces parpadean",
            "batería muere",
            "alternador falla",
            "códigos de error",
        ],

        "horarios_disponibles": {
            "lunes": ["08:00", "09:00", "13:00", "14:00"],
            "martes": ["08:00", "10:00", "12:00", "15:00"],
            "miercoles": ["08:00", "14:00", "16:00"],
            "jueves": ["08:00", "09:00", "10:00", "13:00"],
            "viernes": ["11:00", "12:00", "13:00", "14:00"],
            "sabado": ["08:00", "09:00", "10:00"],
        },
    },

    {
        "id": "MEX004",
        "nombre": "Ana Martínez",
        "numero": "300-555-0104",
        "experiencia_anos": 10,
        "tiempo_empresa_anos": 5,
        "especialidad_principal": "Llantas y Alineación",
        "especialidades": ["Llantas", "Alineación", "Balanceo"],

        "bio": "Especialista en alineación y llantas con 10 años de experiencia. "
               "Ana tiene precisión milimétrica en alineaciones y es experta en "
               "compostura de llantas y parches.",

        "procesos_generales": [
            "Inspección de llantas",
            "Prueba de presión",
            "Verificación de desgaste",
            "Diagnóstico de alineación",
        ],

        "procesos_especializados": {
            "Llantas": [
                "Cambio de llantas",
                "Reparación de pinchazo",
                "Parche de llanta interna",
                "Vulcanización de llantas",
                "Retirada de objetos",
            ],
            "Alineación": [
                "Alineación de ejes",
                "Calibración de ángulos",
                "Alineación de dirección",
                "Diagnóstico de descentraje",
            ],
            "Balanceo": [
                "Balanceo dinámico",
                "Balanceo estático",
                "Nivelación de ruedas",
            ],
        },

        "diagnosticos_rag_relacionados": [
            "auto se va a un lado",
            "llanta pinchada",
            "vibra en carretera",
            "desgaste irregular",
            "ruido en llantas",
        ],

        "horarios_disponibles": {
            "lunes": ["08:00", "09:00", "14:00", "16:00"],
            "martes": ["08:00", "11:00", "14:00", "17:00"],
            "miercoles": ["09:00", "13:00", "15:00"],
            "jueves": ["08:00", "09:00", "14:00", "15:00"],
            "viernes": ["10:00", "11:00", "15:00", "16:00"],
            "sabado": ["09:00", "11:00", "12:00", "13:00"],
        },
    },

    {
        "id": "MEX005",
        "nombre": "Roberto Sánchez",
        "numero": "300-555-0105",
        "experiencia_anos": 16,
        "tiempo_empresa_anos": 9,
        "especialidad_principal": "Transmisión Automática",
        "especialidades": ["Transmisión", "Caja Automática", "Embrague"],

        "bio": "Experto en transmisiones automáticas con 16 años de experiencia. "
               "Roberto es el especialista de confianza para cajas automáticas "
               "complejas. Tiene paciencia y excelente comunicación.",

        "procesos_generales": [
            "Revisión de líquido de transmisión",
            "Diagnóstico de cambios de velocidad",
            "Prueba de respuesta de embrague",
            "Análisis de deslizamiento",
        ],

        "procesos_especializados": {
            "Transmisión": [
                "Cambio de aceite de transmisión",
                "Reemplazo de filtro de transmisión",
                "Reparación de fugas",
                "Diagnóstico de cambios duros",
            ],
            "Caja Automática": [
                "Calibración de presión",
                "Reparación de solenoide",
                "Diagnóstico electrónico",
                "Reparación de válvulas",
                "Reemplazamiento de embrague",
            ],
            "Embrague": [
                "Cambio de embrague",
                "Reparación de disco de embrague",
                "Diagnostico de patinamiento",
                "Ajuste de sistema de embrague",
            ],
        },

        "diagnosticos_rag_relacionados": [
            "cambios duros",
            "pierde velocidades",
            "retraso en cambio",
            "resbalon de embrague",
            "fluido de transmisión oscuro",
        ],

        "horarios_disponibles": {
            "lunes": ["09:00", "10:00", "14:00", "15:00"],
            "martes": ["09:00", "11:00", "14:00", "16:00"],
            "miercoles": ["10:00", "15:00", "16:00"],
            "jueves": ["09:00", "10:00", "11:00", "14:00"],
            "viernes": ["13:00", "14:00", "15:00", "16:00"],
            "sabado": ["09:00", "10:00", "11:00", "12:00"],
        },
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# FESTIVOS COLOMBIA 2026
# ═══════════════════════════════════════════════════════════════════════════════

COLOMBIAN_HOLIDAYS_2026 = {
    "2026-01-01": "Año Nuevo",
    "2026-01-12": "Reyes (trasladado)",
    "2026-03-30": "Lunes Santo",
    "2026-03-31": "Martes Santo",
    "2026-04-01": "Miércoles Santo",
    "2026-05-01": "Día del Trabajo",
    "2026-05-14": "Ascensión del Señor",
    "2026-05-18": "Lunes de Pentecostés",
    "2026-05-25": "Corpus Christi",
    "2026-06-01": "Sagrado Corazón",
    "2026-06-08": "Lunes Pentecostés (trasladado)",
    "2026-06-29": "San Pedro y San Pablo",
    "2026-07-01": "San Pedro y San Pablo (trasladado)",
    "2026-08-07": "Batalla de Boyacá",
    "2026-08-15": "Asunción de María",
    "2026-08-17": "Asunción de María (trasladado)",
    "2026-10-12": "Día de la Raza",
    "2026-10-19": "Día de la Raza (trasladado)",
    "2026-11-01": "Todos los Santos",
    "2026-11-02": "Todos los Santos (trasladado)",
    "2026-11-11": "Independencia de Cartagena",
    "2026-11-16": "Independencia de Cartagena (trasladado)",
    "2026-12-08": "Inmaculada Concepción",
    "2026-12-25": "Navidad",
    "2026-12-28": "Navidad (trasladado)",
}

# ═══════════════════════════════════════════════════════════════════════════════
# INFORMACIÓN DEL TALLER
# ═══════════════════════════════════════════════════════════════════════════════

TALLER_INFO = {
    "nombre": "Taller Mecánico Auto Partes Pro",
    "misión": "Proporcionar servicio de diagnóstico y reparación de alta calidad "
              "con profesionales expertos y tecnología moderna.",
    "visión": "Ser el taller de confianza de la región, reconocido por excelencia "
              "y atención al cliente.",

    "horarios": {
        "lunes_viernes": "08:00 - 18:00",
        "sabado": "09:00 - 14:00",
        "domingo": "CERRADO",
    },

    "contacto": {
        "telefono": "300-AUTO-PRO (300-288-6776)",
        "whatsapp": "+57 300-123-4567",
        "email": "citas@tallerautopartespro.com",
        "ubicacion": "Cra. 5 # 12-34, Bogotá, Colombia",
    },

    "servicios": [
        "Diagnóstico completo",
        "Reparación de motor",
        "Reparación de frenos",
        "Alineación y balanceo",
        "Reparación de transmisión",
        "Reparación eléctrica",
        "Cambio de llantas",
    ],

    "garantia": "Todos los servicios incluyen 3 meses de garantía en piezas y mano de obra.",
}

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def get_mecanicos():
    """Retorna lista de todos los mecánicos."""
    return MECANICOS

def get_mecanico_por_nombre(nombre: str):
    """Busca un mecánico por nombre (case-insensitive)."""
    nombre_lower = nombre.lower()
    for mecanico in MECANICOS:
        if nombre_lower in mecanico["nombre"].lower():
            return mecanico
    return None

def get_mecanicos_por_especialidad(especialidad: str):
    """Retorna mecánicos que tienen esa especialidad."""
    especialidad_lower = especialidad.lower()
    return [
        m for m in MECANICOS
        if any(esp.lower() == especialidad_lower for esp in m["especialidades"])
    ]

def is_holiday_2026(date_str: str) -> bool:
    """Verifica si una fecha es festivo en 2026."""
    return date_str in COLOMBIAN_HOLIDAYS_2026

def get_holiday_name(date_str: str) -> str:
    """Retorna el nombre del festivo si existe."""
    return COLOMBIAN_HOLIDAYS_2026.get(date_str, "")

def get_taller_info():
    """Retorna información del taller."""
    return TALLER_INFO
