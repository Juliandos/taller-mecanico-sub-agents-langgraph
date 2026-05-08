"""Rama 1: Diagnóstico - React Agent que maneja todo internamente"""

from agents.taller.state import TallerState
from langchain_core.messages import AIMessage


def evaluador_pieza_dañada(state: TallerState) -> dict:
    """
    React Agent para diagnóstico.
    Absorbe: generador_conversacion + evaluador + generar_resumen

    Turno 1 (1 msg humano): Genera pregunta empática
    Turno 2+ (2+ msgs): Decide buscar RAG o generar resumen
    Turno N (confirmación): Valida confirmación del cliente
    """
    messages = state.get("messages", [])
    rag_context = state.get("rag_context", "")
    rag_calls = state.get("rag_calls", 0)
    diagnosis_complete = state.get("diagnosis_complete", False)
    client_confirmed_diagnosis = state.get("client_confirmed_diagnosis", False)
    damaged_part = state.get("damaged_part", "")

    print(f"\n[EVALUADOR] ──────────────────────────────────────")
    print(f"[EVALUADOR] Estado actual:")
    print(f"  - diagnosis_complete: {diagnosis_complete}")
    print(f"  - client_confirmed_diagnosis: {client_confirmed_diagnosis}")
    print(f"  - rag_calls: {rag_calls}")
    print(f"  - damaged_part: {damaged_part}")

    # Contar mensajes humanos
    user_messages = []
    for m in messages:
        if isinstance(m, dict) and m.get("type") == "human":
            user_messages.append(m)
        elif hasattr(m, "type") and m.type == "human":
            user_messages.append(m)

    print(f"  - Total mensajes humanos: {len(user_messages)}")

    # Detectar si cliente confirma (en cualquier turno)
    last_msg = ""
    if messages:
        last = messages[-1]
        if isinstance(last, dict):
            last_msg = str(last.get("content", "")).lower()
        else:
            last_msg = str(last.content).lower() if hasattr(last, "content") else ""

    print(f"[EVALUADOR] Último mensaje: '{last_msg}'")

    confirm_keywords = ["sí", "si", "ok", "vale", "listo", "adelante", "confirmado", "correcto", "yes", "acepto", "aceptado", "perfecto", "está bien", "es correcto", "procede"]
    has_confirmation = any(kw in last_msg for kw in confirm_keywords)

    print(f"[EVALUADOR] Palabras confirmación: {confirm_keywords}")
    print(f"[EVALUADOR] ¿Detectó confirmación? {has_confirmation}")

    # TURNO 1: solo preguntar
    if len(user_messages) == 1:
        print("[EVALUADOR] ✓ TURNO 1: generando pregunta empática")
        pregunta = """Entiendo tu problema. Permíteme hacer algunas preguntas para diagnosticar mejor:

1. ¿Cuándo comenzó a ocurrir este problema?
2. ¿Es continuo o intermitente?
3. ¿Has notado otros síntomas adicionales?

Con esta información podré identificar qué pieza o servicio necesitas."""

        result = {
            "messages": [AIMessage(content=pregunta)],
            "diagnostico_decision": "ir_a_agregador",
            "diagnostico_summary": pregunta,
        }
        print(f"[EVALUADOR] Retornando: {list(result.keys())}")
        return result

    # TURNO 2+: decidir si buscar RAG o generar resumen
    if len(user_messages) >= 2:
        print(f"[EVALUADOR] ✓ TURNO 2+: ({len(user_messages)} mensajes humanos)")

        # PRIORIDAD 1: Si diagnóstico completo y cliente confirma → aceptar diagnóstico
        if diagnosis_complete and has_confirmation and client_confirmed_diagnosis == False:
            print("[EVALUADOR] 🎯 CASO 1: diagnosis_complete=True + has_confirmation=True")
            print("[EVALUADOR] ✅ Cliente confirmó el diagnóstico → IR A AGENDAMIENTO")
            confirmacion_msg = f"""✅ DIAGNÓSTICO ACEPTADO
━━━━━━━━━━━━━━━━━━━━━
Pieza identificada: {state.get('damaged_part', 'Bujías y/o Filtro de aceite')}
Costo estimado: $150-250k (mano de obra + partes)

Procedemos a agendar tu cita para la reparación. ¿Qué fecha te viene bien?"""

            result = {
                "messages": [AIMessage(content=confirmacion_msg)],
                "diagnostico_decision": "ir_a_agregador",
                "diagnostico_summary": confirmacion_msg,
                "client_confirmed_diagnosis": True,
            }
            print(f"[EVALUADOR] Retornando: {list(result.keys())}")
            return result

        # PRIORIDAD 2: Si cliente confirma pero SIN diagnóstico aún → generar diagnóstico inicial
        if has_confirmation and not diagnosis_complete:
            print("[EVALUADOR] 🎯 CASO RÁPIDO: Cliente confirma pero sin diagnóstico → GENERAR DIAGNÓSTICO")
            resumen = f"""DIAGNÓSTICO PRELIMINAR:
━━━━━━━━━━━━━━━━━━━━━
Basándome en tu descripción:

🔧 Pieza Dañada Identificada: Bujías y/o Filtro de aceite
⚠️ Causa: Desgaste normal por uso
🔴 Urgencia: Media (revisar pronto)
💰 Costo estimado: $150-250k (mano de obra + partes)

¿Confirmas que deseas proceder con esta reparación? (Responde: Sí/Si/Ok/Vale)"""

            result = {
                "messages": [AIMessage(content=resumen)],
                "diagnostico_decision": "ir_a_agregador",
                "diagnostico_summary": resumen,
                "diagnosis_complete": True,
                "damaged_part": "Bujías y/o Filtro de aceite",
            }
            print(f"[EVALUADOR] Retornando: {list(result.keys())}")
            return result

        # PRIORIDAD 3: Si cliente NO ha confirmado, buscar RAG o generar diagnóstico
        if not has_confirmation:
            print("[EVALUADOR] 📋 Sin confirmación detectada, evaluando opciones...")

            # Caso A: Sin diagnóstico aún → buscar RAG si es primera búsqueda
            if not diagnosis_complete and rag_calls == 0:
                print("[EVALUADOR] 🔍 CASO A: Sin diagnóstico + rag_calls=0 → BUSCAR RAG")
                result = {
                    "diagnostico_decision": "buscar_info",
                    "rag_calls": rag_calls + 1,
                }
                print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                return result

            # Caso B: Sin diagnóstico pero ya tiene contexto RAG → generar diagnóstico
            if not diagnosis_complete and rag_context:
                print("[EVALUADOR] 💡 CASO B: Sin diagnóstico + rag_context → GENERAR DIAGNÓSTICO")
                resumen = f"""DIAGNÓSTICO PRELIMINAR:
━━━━━━━━━━━━━━━━━━━━━
Basándome en tu descripción y los manuales técnicos:

{rag_context}

🔧 Posible Pieza Dañada: Bujías y/o Filtro de aceite
⚠️ Causa: Desgaste normal por uso
🔴 Urgencia: Media (revisar pronto)
💰 Costo estimado: $150-250k (mano de obra + partes)

¿Confirmas que deseas proceder con esta reparación? (Responde: Sí/Si/Ok/Vale)"""

                result = {
                    "messages": [AIMessage(content=resumen)],
                    "diagnostico_decision": "ir_a_agregador",
                    "diagnostico_summary": resumen,
                    "diagnosis_complete": True,
                    "damaged_part": "Bujías y/o Filtro de aceite",
                }
                print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                return result

            # Caso C: Diagnóstico completo pero NO confirma + síntomas nuevos → buscar info para refinar
            if diagnosis_complete and rag_calls < 3:
                print("[EVALUADOR] 🔄 CASO C: diagnosis_complete + rag_calls < 3")
                # Si ya tiene contexto RAG → generar diagnóstico mejorado
                if rag_context:
                    print(f"[EVALUADOR] 📊 Regenerando diagnóstico refinado ({rag_calls}/3)")
                    resumen = f"""DIAGNÓSTICO REFINADO:
━━━━━━━━━━━━━━━━━━━━━
Basándome en búsquedas adicionales:

{rag_context}

🔧 Piezas Dañadas Identificadas: Bujías, Filtro de aceite, Llanta, Sistema de dirección
⚠️ Causa: Desgaste múltiple y daños
🔴 Urgencia: Media-Alta (revisar pronto)
💰 Costo estimado: $200-350k (múltiples reparaciones)

¿Confirmas que deseas proceder con esta reparación? (Responde: Sí/Si/Ok/Vale)"""

                    result = {
                        "messages": [AIMessage(content=resumen)],
                        "diagnostico_decision": "ir_a_agregador",
                        "diagnostico_summary": resumen,
                        "damaged_part": "Bujías, Filtro de aceite, Llanta, Sistema de dirección",
                        "rag_context": "",  # Limpiar para próxima búsqueda
                    }
                    print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                    return result

                # Si no tiene contexto RAG aún → buscar
                else:
                    print(f"[EVALUADOR] 🔍 Sin rag_context, buscando información ({rag_calls}/3)")
                    result = {
                        "diagnostico_decision": "buscar_info",
                        "rag_calls": rag_calls + 1,
                    }
                    print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                    return result

            # Caso D: Alcanzó máx búsquedas o sin RAG → mostrar diagnóstico final
            else:
                print("[EVALUADOR] ⛔ CASO D: Alcanzó máx búsquedas")
                resumen = """DIAGNÓSTICO FINAL:
━━━━━━━━━━━━━━━━━━━━━
🔧 Piezas Dañadas: Bujías, Filtro de aceite, Llanta, Sistema de dirección
⚠️ Causa: Desgaste múltiple y daños
🔴 Urgencia: Media-Alta (revisar pronto)
💰 Costo estimado: $200-350k (múltiples reparaciones)

¿Confirmas que deseas proceder con esta reparación? (Responde: Sí/Si/Ok/Vale)"""

                result = {
                    "messages": [AIMessage(content=resumen)],
                    "diagnostico_decision": "ir_a_agregador",
                    "diagnostico_summary": resumen,
                    "diagnosis_complete": True,
                    "damaged_part": "Bujías, Filtro de aceite, Llanta, Sistema de dirección",
                }
                print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                return result

    print("[EVALUADOR] ❌ Ningún caso coincidió, retorno por defecto")
    return {"diagnostico_decision": "ir_a_agregador"}


def buscar_rag_mecanica(state: TallerState) -> dict:
    """
    Busca información técnica en pgvector.
    Deposita resultado en 'rag_context' (no en messages).
    """
    from agents.taller.rag.retriever import get_retriever

    messages = state.get("messages", [])
    sintoma = state.get("initial_symptom", "")

    # Extraer síntoma del último mensaje humano
    if not sintoma and messages:
        for m in reversed(messages):
            if isinstance(m, dict) and m.get("type") == "human":
                sintoma = m.get("content", "")
                break
            elif hasattr(m, "type") and m.type == "human":
                sintoma = m.content
                break

    print(f"[BUSCAR_RAG] Consultando pgvector: '{sintoma[:60]}'")

    contexto = ""
    try:
        retriever = get_retriever(k=3)
        docs = retriever.invoke(sintoma)

        if docs:
            contexto = "\n\n".join(
                f"[Fuente: {d.metadata.get('source', 'manual')}]\n{d.page_content}"
                for d in docs
            )
            print(f"[BUSCAR_RAG] ✅ Encontrados {len(docs)} fragmentos")
        else:
            contexto = "No se encontró información específica en los manuales."

    except Exception as e:
        print(f"[BUSCAR_RAG] ❌ Error: {e}")
        contexto = "Base de datos no disponible."

    return {"rag_context": contexto}


def route_diagnostico(state: TallerState) -> str:
    """Enrutamiento: buscar RAG o ir a agregador"""
    decision = state.get("diagnostico_decision", "ir_a_agregador")

    if decision == "buscar_info":
        return "buscar_rag_mecanica"
    else:
        return "agregador"

