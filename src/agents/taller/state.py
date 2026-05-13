"""State definition for Taller Mecánico Agent"""

from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
import operator


class TallerState(TypedDict):
    """Estado compartido entre todos los nodos del agente."""

    # Mensajes (acumulan)
    # Esto se podría hacer también con MessageState y un método add_message, pero para simplicidad lo dejamos como una lista normal que se va acumulando. Se asume que cada nodo que produce mensajes los agrega a esta lista.
    # Pero MessageState sería una opción más elegante y controlada, con métodos específicos para agregar mensajes de usuario, sistema, etc. Por ahora, se deja como una lista simple para enfocarnos en la lógica del taller.
    messages: Annotated[list[AnyMessage], operator.add]

    # Datos del cliente
    customer_name: str
    phone: str
    vehicle_info: str

    # Rama 1: Diagnóstico
    initial_symptom: str
    diagnostico_decision: str
    diagnostico_summary: str
    rag_context: str  # contexto de búsqueda RAG
    rag_calls: int  # contador de búsquedas RAG (deprecado, usar initial_rag_system para detección de cambios)
    initial_rag_system: str  # sistema del vehículo en la búsqueda RAG inicial (motor, frenos, transmisión, etc.)

    # Variables para control de flujo de diagnóstico
    diagnosis_complete: bool  # True cuando se identificó la pieza dañada
    damaged_part: str  # Nombre de la pieza identificada (ej: "Bujías")
    client_confirmed_diagnosis: bool  # True cuando cliente confirma el diagnóstico

    # Rama 2: Agendamiento
    booking_decision: str  # "agendar" o "transferir_humano"
    appointment_data: dict  # {fecha, hora, mecanico, costo}
    appointment_summary: str
    missing_fields: list[str]  # Campos faltantes (REPLACE, no ADD)
    disponibilidad_context: str  # Información de disponibilidad del taller
    consultas_disponibilidad: int  # Contador de consultas de disponibilidad
    mecanicos_disponibles: list  # Lista de mecánicos con disponibilidad
    puestos_servicio: list  # Puestos de servicio disponibles
    servicios: list  # Servicios disponibles
    rejected_date: str  # Fecha rechazada por festivo (para interpretar "el día siguiente")

    # Control
    requires_human: bool
    human_transfer_requests: int  # Contador de cuántas veces solicita transferencia a humano
    booking_confirmed: bool

    # Selección de mecánico y área de servicio
    selected_mechanic: str  # Nombre del mecánico elegido (vacío = usar recomendado)
    selected_area: str  # Nombre del área elegida (vacío = usar "Diagnóstico")
