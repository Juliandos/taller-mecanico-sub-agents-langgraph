"""Rama 1: Diagnóstico - React Agent que maneja todo internamente"""

import re
import unicodedata
from agents.taller.state import TallerState
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chat_models import init_chat_model

# Inicializar LLM para generar respuestas dinámicas
llm = init_chat_model("openai:gpt-4o", temperature=0.7)


def _normalizar_texto(texto: str) -> str:
    """Normaliza texto: elimina tildes, convierte a minúsculas, normaliza espacios."""
    # Convertir a minúsculas
    texto = texto.lower().strip()
    # Normalizar tildes y acentos
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    # Normalizar espacios múltiples a un solo espacio
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def _detectar_palabra_clave(texto: str, palabras_clave: list) -> bool:
    """Detecta palabras clave con soporte para regex, tildes, espacios variables."""
    texto_norm = _normalizar_texto(texto)

    for palabra in palabras_clave:
        # Crear patrón regex que permite 1-2 espacios entre palabras
        patron = _crear_patron_flexible(palabra)
        if re.search(patron, texto_norm):
            return True
    return False


def _crear_patron_flexible(palabra: str) -> str:
    """Crea un patrón regex flexible para palabras con espacios variables."""
    # Normalizar la palabra
    palabra_norm = _normalizar_texto(palabra)
    # Reemplazar espacios individuales con patrón de 1-2 espacios
    patron = palabra_norm.replace(' ', r'\s{1,2}')
    # Usar límites de palabra para exactitud
    return r'\b' + patron + r'\b'


def _generar_respuesta_ia(sistema: str, usuario: str) -> str:
    """Genera una respuesta con IA de forma natural."""
    try:
        respuesta = llm.invoke([
            ("system", sistema),
            ("human", usuario)
        ])
        return respuesta.content if hasattr(respuesta, 'content') else str(respuesta)
    except Exception as e:
        print(f"[IA_ERROR] Error generando respuesta: {e}")
        return None


def _generar_preguntas_diagnostico(ultimo_mensaje: str) -> str:
    """Genera preguntas diagnósticas personalizadas basadas en lo que el cliente dice."""
    system = """Eres un mecánico amable y profesional de un taller de autos.
El cliente acaba de describir un problema con su vehículo.
Genera 3-4 preguntas diagnósticas ESPECÍFICAS y naturales basadas en lo que describió.
Las preguntas deben ser empáticas, profesionales y orientadas a entender mejor el problema.
Sé conversacional, no hagas una lista numerada, sino que fluya naturalmente."""

    respuesta = _generar_respuesta_ia(system, f"El cliente dice: {ultimo_mensaje}")
    return respuesta or "Entiendo tu problema. ¿Cuándo comenzó? ¿Es continuo o intermitente? ¿Has notado otros síntomas?"


def _generar_diagnostico_basado_en_sintomas(sintomas: str, rag_context: str = "") -> str:
    """Genera un diagnóstico personalizado basado en los síntomas del cliente."""
    system = """Eres un mecánico experto en diagnóstico de vehículos.
Basándote en los síntomas descritos, genera un diagnóstico preliminar REALISTA.

ESTRUCTURA:
1. Comienza con el título: 📋 **DIAGNÓSTICO PRELIMINAR**
2. Incluye:
   - Posibles piezas dañadas (sé específico basándote en los síntomas)
   - Causa probable
   - Urgencia (baja, media, media-alta, alta)
3. AL FINAL, siempre agrega:

   **¿Deseas proceder con la reparación?**
   Responde con: "ok", "perfecto", "adelante", "claro", "dale" o "vamos"

Sé profesional pero amable. El usuario debe entender claramente qué está mal y por qué."""

    contexto_rag = f"\nInformación técnica disponible:\n{rag_context}" if rag_context else ""
    prompt = f"Síntomas del cliente: {sintomas}{contexto_rag}"

    respuesta = _generar_respuesta_ia(system, prompt)
    return respuesta or "📋 **DIAGNÓSTICO PRELIMINAR**\n\nSe requiere una revisión detallada del vehículo.\n\n**¿Deseas proceder con la reparación?**\nResponde con: 'ok', 'perfecto', 'adelante', 'claro', 'dale' o 'vamos'"


# def _generar_confirmacion_diagnostico(pieza_dañada: str, respuesta_cliente: str) -> str:
#     """Genera una confirmación natural del diagnóstico aceptado."""
#     system = """Eres un mecánico profesional que acaba de recibir la confirmación del cliente para proceder.
# Genera una respuesta breve, profesional y amable que:
# - Confirme que procederás con la reparación
# - Mencione la pieza/problema identificado
# - Pregunta sobre disponibilidad para agendar
# Sé conversacional y cálido. No uses emojis ni formatos especiales."""

#     prompt = f"El cliente confirmó proceder con: {pieza_dañada}. Respondió: '{respuesta_cliente}'"
#     respuesta = _generar_respuesta_ia(system, prompt)
#     return respuesta or f"Perfecto, procederemos con la reparación. ¿Cuándo te viene bien agendar?"


def _generar_confirmacion_diagnostico(pieza_dañada: str, respuesta_cliente: str = "") -> str:
    """Genera una confirmación natural del diagnóstico aceptado + pregunta de agendamiento."""
    system = """Eres un mecánico que acaba de recibir la confirmación del cliente para proceder.
Genera una respuesta profesional y amable que:
1. Confirme que procederemos con la reparación
2. Mencione brevemente la pieza/problema identificado
3. Pregunta CUÁNDO desea agendar la cita (fecha y hora)

Sé conversacional y cálido. Pide fecha y hora de forma natural en una sola pregunta."""

    contexto = f"Respondió: '{respuesta_cliente}'" if respuesta_cliente else ""
    prompt = f"El cliente confirmó proceder con la reparación de: {pieza_dañada}. {contexto}"
    respuesta = _generar_respuesta_ia(system, prompt)
    return respuesta or f"✅ Perfecto, procederemos con la reparación. ¿Cuándo te gustaría agendar la cita? Por favor, dime la fecha y hora preferida."


def _detectar_intension_agendar(ultimo_mensaje: str) -> bool:
    """Detecta si el usuario quiere agendar cita directamente."""
    keywords_agendar = [
        # Palabras clave originales
        "cita", "agendar", "agendar cita", "quiero una cita", "necesito una cita",
        "directamente", "ahora mismo", "lo antes posible", "urgente",
        "solo quiero agendar", "reservar", "appointment", "schedule",
        # Nuevas variaciones
        "dame una cita", "dame cita", "hazme una cita", "programar cita", "programar una cita",
        "quiero programar", "necesito programar", "agenda me", "agendame",
        "reserva cita", "reserva una cita", "necesito reservar", "quiero reservar",
        "cita urgente", "cita hoy", "cita ahora", "cita ya", "cita inmediata",
        "cita inmediatamente", "para hoy", "para ahora", "para ya", "lo mas rapido",
        "lo mas pronto", "cuanto antes", "asap", "inmediato", "rapido",
        "direct", "directo a cita", "sin diagnostico", "sin pregunta",
        "llevo directo", "me lleva directo", "voy directo",
    ]
    return _detectar_palabra_clave(ultimo_mensaje, keywords_agendar)


def evaluador_pieza_dañada(state: TallerState) -> dict:
    """
    React Agent para diagnóstico.
    Absorbe: generador_conversacion + evaluador + generar_resumen

    Turno 1 (1 msg humano): Detecta intención de agendar o genera pregunta empática
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

    confirm_keywords = [
        # Palabras/frases que claramente indican confirmación (SIN "si/sí")
        "ok", "perfecto", "adelante", "claro", "dale", "vamos", "exacto",
        "vale", "listo", "bueno", "está bien", "me parece bien", "me parece perfecto",
        "aceptado", "confirmado", "aprobado", "procede", "proceder", "procedamos",
        "yes", "acepto", "correcto", "está ok", "está perfecto", "está confirmado",
        "this ok", "this good", "this perfect", "dale adelante", "adelante con eso",
        "vamosss", "dale dale", "claro que sí", "obvio", "por supuesto",
        "seguro", "seguro que sí", "exactamente", "super bien", "muy bien",
        "esta super bien", "esta muy bien", "está bueno", "está genial",
        "apruebo", "ya", "ya está", "claro que sí", "ok confirmo",
        "ok confirmado", "listo confirmado", "listo dale", "vamos con eso",
        "vamos adelante", "procedemos", "hagamoslo", "hagamos esto",
        "affirmative", "affirmativo", "confirmo", "confirmed",
    ]
    has_confirmation = _detectar_palabra_clave(last_msg, confirm_keywords)

    print(f"[EVALUADOR] ¿Detectó confirmación? {has_confirmation}")

    # CASO ESPECIAL: Diagnóstico confirmado pero aún sin información de agendamiento
    # → Preguntar "¿Cuándo deseas agendar?"
    appointment_data = state.get("appointment_data", {})
    preferred_date = appointment_data.get("preferred_date", "")

    if client_confirmed_diagnosis and not preferred_date:
        print("[EVALUADOR] 💼 Diagnóstico confirmado pero sin fecha de agendamiento → PREGUNTAR POR AGENDAMIENTO")

        system_msg = """Eres un mecánico que acabas de confirmar un diagnóstico con el cliente.
Ahora necesitas saber cuándo puede venir para la reparación.
Genera una pregunta natural y amable sobre su disponibilidad.
Sé conversacional, cálido y profesional."""

        pregunta_agendamiento = llm.invoke([
            ("system", system_msg),
            ("human", f"El cliente confirmó proceder con la reparación de: {damaged_part}")
        ])
        pregunta_texto = pregunta_agendamiento.content if hasattr(pregunta_agendamiento, 'content') else str(pregunta_agendamiento)

        result = {
            "messages": [AIMessage(content=pregunta_texto)],
            "diagnostico_decision": "ir_a_agregador",
            "diagnostico_summary": pregunta_texto,
        }
        print(f"[EVALUADOR] Retornando pregunta de agendamiento: {list(result.keys())}")
        return result

    # TURNO 1: Detectar intención o preguntar
    if len(user_messages) == 1:
        print("[EVALUADOR] ✓ TURNO 1: analizando intención del cliente")

        # Verificar si quiere agendar directamente
        if _detectar_intension_agendar(last_msg):
            print("[EVALUADOR] 🎯 Cliente quiere agendar en primer mensaje, generando respuesta con IA")
            try:
                system_msg = """Eres un asistente amable de taller mecánico.
El cliente quiere agendar una cita directamente, pero necesitamos hacer un diagnóstico primero.
Genera una respuesta amable que:
1. Acepte su solicitud de cita
2. Pida que describa qué problema tiene con su auto
3. Explique que necesitamos el diagnóstico primero antes de agendar

Sé natural, amable y profesional."""

                respuesta = llm.invoke([
                    ("system", system_msg),
                    ("human", last_msg)
                ])
                respuesta_texto = respuesta.content if hasattr(respuesta, 'content') else str(respuesta)

                result = {
                    "messages": [AIMessage(content=respuesta_texto)],
                    "diagnostico_decision": "ir_a_agregador",
                    "diagnostico_summary": respuesta_texto,
                }
                print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                return result
            except Exception as e:
                print(f"[EVALUADOR] ❌ Error generando respuesta: {e}")
                # Fallback a respuesta genérica
                fallback = "Claro, con gusto te agendo una cita. Pero primero, ¿qué problema tiene tu auto? Así hago un diagnóstico antes de agendar."
                result = {
                    "messages": [AIMessage(content=fallback)],
                    "diagnostico_decision": "ir_a_agregador",
                    "diagnostico_summary": fallback,
                }
                return result

        # Si no quiere agendar directamente, hacer preguntas diagnósticas personalizadas con IA
        print("[EVALUADOR] 📋 Cliente menciona un problema, generando preguntas diagnósticas personalizadas")
        pregunta = _generar_preguntas_diagnostico(last_msg)

        if not pregunta:
            pregunta = "Entiendo tu problema. ¿Cuándo comenzó? ¿Es continuo o intermitente? ¿Has notado otros síntomas?"

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

        # Verificar si el cliente VUELVE A INSISTIR sobre la cita en el segundo mensaje
        # Si quiso agendar en TURNO 1 y vuelve a insistir, crear diagnóstico general
        if len(user_messages) == 2 and _detectar_intension_agendar(last_msg):
            print("[EVALUADOR] 🎯 Cliente insiste en cita en segundo mensaje → Diagnóstico general")
            system = """Eres un mecánico profesional. El cliente insiste en agendar sin hacer diagnóstico previo.
Responde de forma amable y profesional ACEPTANDO su solicitud de diagnóstico general.
Explica brevemente qué incluye una revisión de diagnóstico general y pregunta cuándo puede venir.
Sé conversacional y cálido, no formal. No uses formatos con emojis o líneas, solo texto natural."""

            resumen_general = _generar_respuesta_ia(system, last_msg)

            if not resumen_general:
                resumen_general = "Perfecto, procederemos con una revisión de diagnóstico general completo. ¿Cuándo te gustaría venir?"

            result = {
                "messages": [AIMessage(content=resumen_general)],
                "diagnostico_decision": "ir_a_agregador",
                "diagnostico_summary": resumen_general,
                "diagnosis_complete": True,
                "damaged_part": "Diagnóstico general (sin pieza específica identificada)",
                "client_confirmed_diagnosis": True,
            }
            print(f"[EVALUADOR] Retornando: {list(result.keys())}")
            return result

        # PRIORIDAD 1: Si diagnóstico completo y cliente confirma → aceptar diagnóstico
        if diagnosis_complete and has_confirmation and client_confirmed_diagnosis == False:
            print("[EVALUADOR] 🎯 CASO 1: diagnosis_complete=True + has_confirmation=True")
            print("[EVALUADOR] ✅ Cliente confirmó el diagnóstico → IR A AGENDAMIENTO")

            pieza = state.get('damaged_part', 'el trabajo identificado')
            confirmacion_msg = _generar_confirmacion_diagnostico(pieza, last_msg)

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

            # Extraer síntomas de los mensajes del cliente
            sintomas = " ".join([
                m.get("content", "") if isinstance(m, dict) else (m.content if hasattr(m, "content") else "")
                for m in messages if isinstance(m, dict) and m.get("type") == "human" or (hasattr(m, "type") and m.type == "human")
            ])

            resumen = _generar_diagnostico_basado_en_sintomas(sintomas)

            if not resumen:
                resumen = "Basándome en tu descripción, se requiere una revisión detallada. ¿Deseas proceder con la reparación?"

            result = {
                "messages": [AIMessage(content=resumen)],
                "diagnostico_decision": "ir_a_agregador",
                "diagnostico_summary": resumen,
                "diagnosis_complete": True,
                "damaged_part": "Según diagnóstico",
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
                sintomas = " ".join([
                    m.get("content", "") if isinstance(m, dict) else (m.content if hasattr(m, "content") else "")
                    for m in messages if isinstance(m, dict) and m.get("type") == "human" or (hasattr(m, "type") and m.type == "human")
                ])
                resumen = _generar_diagnostico_basado_en_sintomas(sintomas, rag_context)

                if not resumen:
                    resumen = "Basándome en los manuales técnicos y tu descripción, requiere una revisión. ¿Deseas proceder?"

                result = {
                    "messages": [AIMessage(content=resumen)],
                    "diagnostico_decision": "ir_a_agregador",
                    "diagnostico_summary": resumen,
                    "diagnosis_complete": True,
                    "damaged_part": "Según diagnóstico técnico",
                }
                print(f"[EVALUADOR] Retornando: {list(result.keys())}")
                return result

            # Caso C: Diagnóstico completo pero NO confirma + síntomas nuevos → buscar info para refinar
            if diagnosis_complete and rag_calls < 3:
                print("[EVALUADOR] 🔄 CASO C: diagnosis_complete + rag_calls < 3")
                # Si ya tiene contexto RAG → generar diagnóstico mejorado
                if rag_context:
                    print(f"[EVALUADOR] 📊 Regenerando diagnóstico refinado ({rag_calls}/3)")
                    sintomas = " ".join([
                        m.get("content", "") if isinstance(m, dict) else (m.content if hasattr(m, "content") else "")
                        for m in messages if isinstance(m, dict) and m.get("type") == "human" or (hasattr(m, "type") and m.type == "human")
                    ])

                    system = """Eres un mecánico experto. Ya hiciste un diagnóstico inicial y ahora tienes información técnica adicional.
Regenera un diagnóstico REFINADO que:
- Incluya el nuevo contexto técnico
- Sea más preciso que el anterior
- Señale si hay problemas adicionales encontrados

AL FINAL, siempre agrega:
   **¿Deseas proceder con la reparación?**
   Responde con: "ok", "perfecto", "adelante", "claro", "dale" o "vamos"

Sé profesional pero natural. No uses emojis ni formatos especiales."""

                    prompt = f"Síntomas: {sintomas}\nInformación técnica adicional: {rag_context}"
                    resumen = _generar_respuesta_ia(system, prompt)

                    if not resumen:
                        resumen = "Basándome en información adicional, refino el diagnóstico anterior.\n\n**¿Deseas proceder con la reparación?**\nResponde con: 'ok', 'perfecto', 'adelante', 'claro', 'dale' o 'vamos'"

                    result = {
                        "messages": [AIMessage(content=resumen)],
                        "diagnostico_decision": "ir_a_agregador",
                        "diagnostico_summary": resumen,
                        "damaged_part": "Diagnóstico refinado",
                        "rag_context": "",
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
                sintomas = " ".join([
                    m.get("content", "") if isinstance(m, dict) else (m.content if hasattr(m, "content") else "")
                    for m in messages if isinstance(m, dict) and m.get("type") == "human" or (hasattr(m, "type") and m.type == "human")
                ])

                system = """Eres un mecánico experto que ha completado un diagnóstico exhaustivo.
Genera un diagnóstico FINAL que resuma:
- Los problemas identificados (basándote en los síntomas)
- La causa probable
- La urgencia
- Un llamado a acción para proceder
Sé profesional pero amable. No uses emojis ni formatos especiales."""

                resumen = _generar_respuesta_ia(system, f"Síntomas descritos: {sintomas}")

                if not resumen:
                    resumen = "Basándome en todo lo revisado, aquí está mi diagnóstico final. ¿Deseas proceder con la reparación?"

                result = {
                    "messages": [AIMessage(content=resumen)],
                    "diagnostico_decision": "ir_a_agregador",
                    "diagnostico_summary": resumen,
                    "diagnosis_complete": True,
                    "damaged_part": "Diagnóstico final",
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

