"""Nodo Agregador - Combina respuestas de ambas ramas"""

from langchain_core.messages import AIMessage
from agents.taller.state import TallerState


def agregador(state: TallerState) -> dict:
    """
    Agregador: Consolidador final de respuestas.
    Entrega los messages que ya fueron agregados por los nodos anteriores.
    """
    messages = state.get("messages", [])
    customer_name = state.get("customer_name", "")

    print(f"[AGREGADOR] Consolidando respuestas finales...")

    if customer_name:
        print(f"[AGREGADOR] Cliente: {customer_name}")

    # Retornar vacío - los messages ya están en el estado agregados por los nodos anteriores
    # El framework de LangGraph maneja la entrega de messages al usuario final
    return {}
