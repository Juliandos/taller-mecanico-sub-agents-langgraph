"""Agente principal - Grafo de LangGraph para Taller Mecánico"""

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from agents.taller.state import TallerState

# Importar nodos
from agents.taller.nodes.orquestador.node import orquestador, route_orchestrator, route_orchestrator
from agents.taller.nodes.rama_diagnostico.node import (
    evaluador_pieza_dañada,
    buscar_rag_mecanica,
    route_diagnostico,
)
from agents.taller.nodes.rama_agendamiento.extractor import extractor_datos
from agents.taller.nodes.rama_agendamiento.pedir_datos import pedir_datos_faltantes
from agents.taller.nodes.rama_agendamiento.consultar_disponibilidad import consultar_disponibilidad_taller
from agents.taller.nodes.rama_agendamiento.booking_agent import booking_agent
from agents.taller.nodes.rama_agendamiento.route_booking import route_agendamiento
from agents.taller.nodes.agregador.node import agregador


def make_graph():
    """Construir grafo principal."""
    builder = StateGraph(TallerState)

    # ──── NODOS ────
    # Orquestador
    builder.add_node("orquestador", orquestador)

    # Rama 1: Diagnóstico (React Agent)
    builder.add_node("evaluador_pieza_dañada", evaluador_pieza_dañada)
    builder.add_node("buscar_rag_mecanica", buscar_rag_mecanica)

    # Rama 2: Agendamiento (Ciclo interno: Extractor con RAG simulado)
    builder.add_node("extractor_datos", extractor_datos)
    builder.add_node("pedir_datos_faltantes", pedir_datos_faltantes)
    builder.add_node("consultar_disponibilidad_taller", consultar_disponibilidad_taller)
    builder.add_node("booking_agent", booking_agent)

    # Agregador
    builder.add_node("agregador", agregador)

    # ──── EDGES ────
    # START → Orquestador
    builder.add_edge(START, "orquestador")

    # Orquestador → Ramas (enrutamiento)
    builder.add_conditional_edges(
        "orquestador",
        route_orchestrator,
        {
            "rama_diagnostico": "evaluador_pieza_dañada",
            "rama_agendamiento": "extractor_datos",
            "handoff": "agregador",  # Transferencia directa a humano
        }
    )

    # ──── RAMA 1: DIAGNÓSTICO (React Agent) ────
    # Evaluador: decide buscar RAG o ir a agregador
    builder.add_conditional_edges(
        "evaluador_pieza_dañada",
        route_diagnostico,
        {
            "buscar_rag_mecanica": "buscar_rag_mecanica",
            "agregador": "agregador",
        }
    )

    # React loop: si busca RAG, vuelve al evaluador
    builder.add_edge("buscar_rag_mecanica", "evaluador_pieza_dañada")

    # ──── RAMA 2: AGENDAMIENTO (Ciclo interno: Extractor con RAG) ────
    # Extractor extrae datos → route_agendamiento decide flujo
    builder.add_conditional_edges(
        "extractor_datos",
        route_agendamiento,
        {
            "pedir_datos_faltantes": "pedir_datos_faltantes",
            "consultar_disponibilidad": "consultar_disponibilidad_taller",
            "booking_agent": "booking_agent",
        }
    )

    # Salida: pedir_datos_faltantes → agregador (esperar respuesta del usuario en siguiente turno)
    builder.add_edge("pedir_datos_faltantes", "agregador")

    # Ciclo interno: consultar disponibilidad vuelve a extractor
    builder.add_edge("consultar_disponibilidad_taller", "extractor_datos")

    # Salida final: booking_agent → agregador
    builder.add_edge("booking_agent", "agregador")

    # ──── CONVERGENCIA ────
    # Agregador → END
    builder.add_edge("agregador", END)

    return builder.compile()


# Instancia global
agent = make_graph()


if __name__ == "__main__":
    # Test básico
    from langchain_core.messages import HumanMessage

    result = agent.invoke({"messages": [HumanMessage(content="Hola, mi auto vibra al frenar")]})
    print("\n" + "="*60)
    print("RESULTADO FINAL:")
    print("="*60)
    print(result["messages"][-1].content)
