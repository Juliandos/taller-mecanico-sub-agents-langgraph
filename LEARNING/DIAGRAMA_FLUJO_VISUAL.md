# 🎨 Diagrama de Flujo Visual - Sistema Completo

## 1. FLUJO GENERAL DEL AGENTE

```
                        ┌─────────────────────────────┐
                        │   USUARIO INICIA CHAT       │
                        └──────────────┬──────────────┘
                                       │
                                       ↓
                        ┌─────────────────────────────┐
                        │  MENSAJE INICIAL BIENVENIDA │
                        │                             │
                        │ 🔧 Diagnóstico             │
                        │ 📅 Agendar cita            │
                        │ 👨‍🔧 Elegir mecánico        │
                        │ ❓ Preguntas taller        │
                        │ 📞 Transferencia humana    │
                        └──────────────┬──────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │     USUARIO RESPONDE        │
                        └──────────────┬──────────────┘
                                       │
                                       ↓
                    ╔══════════════════════════════════╗
                    ║   ORQUESTADOR: ANALIZA INTENCIÓN ║
                    ╚════╤═════════════╤════════════╤═══╝
                         │             │            │
            ┌────────────┴──┐   ┌─────┴──────┐   ┌─┴─────────────┐
            │                │   │            │   │               │
            ↓                ↓   ↓            ↓   ↓               ↓
        ¿PREGUNTA?      ¿SÍNTOMA?      ¿AGENDAR?  ¿CAMBIO?   ¿TRANSFERENCIA?
            │                │               │       │            │
            ↓                │               │       │            │
    ┌──────────────┐        │               │       │            │
    │  NODO_FAQ    │        │               │       │            │
    └──────┬───────┘        │               │       │            │
           │                ↓               │       │            │
           │         ┌────────────────┐    │       │            │
           │         │RAMA DIAGNÓSTICO│    │       │            │
           │         └────────┬───────┘    │       │            │
           │                  │            │       │            │
           │    ┌─────────────┴──────────┐ │       │            │
           │    │ Hacer preguntas        │ │       │            │
           │    │ Generar diagnóstico    │ │       │            │
           │    │ Pedir confirmación     │ │       │            │
           │    └──────────┬─────────────┘ │       │            │
           │               │               │       │            │
           │    ┌──────────┴──────────┐    │       │            │
           │    │ ¿Confirmó?         │    │       │            │
           │    └──┬──────────────┬──┘    │       │            │
           │       │ SÍ       NO │        │       │            │
           │       │           └─┼────→ Repite  │       │            │
           │       │                     │       │            │
           │       └──────────┬──────────┘       │            │
           │                  ↓                  │            │
           │         ┌────────────────┐          │            │
           │         │RAMA AGENDAMIENTO           │            │
           │         └────────┬───────┘          │            │
           │                  │                  │            │
           ├─ RESPONDE ────→ VALIDA DATOS ←─────┴────────┐   │
           │  PREGUNTA         │                          │   │
           │                   ↓                          │   │
           ├─ VUELVE A ─→ SOLICITA DATOS FALTANTES       │   │
           │  MENÚ             │                          │   │
           │  ↑                ↓                          │   │
           │  └─ CONFIRMA ─→ RESUMEN CITA               │   │
           │      DATOS       │                          │   │
           │  ┌───────────────┴──────────┐               │   │
           │  │ ¿CORRECCIONES?           │               │   │
           │  └───┬───────────────┬──────┘               │   │
           │      │ SÍ            │ NO                   │   │
           │      │               │                      │   │
           │      ↓               ↓                      │   │
           │  ┌─────────┐   ┌──────────────┐            │   │
           │  │ EDITAR  │   │ AGENDAR CITA │            │   │
           │  │CAMPO    │   └────────┬─────┘            │   │
           │  └──┬──────┘            │                  │   │
           │     │ Vuelve a resumen  │                  │   │
           │     └────────┬──────────┘                  │   │
           │              │                            │   │
           │              ↓                            │   │
           │         ┌──────────────┐                  │   │
           │         │CONFIRMACIÓN  │                  │   │
           │         │EXITOSA ✅    │                  │   │
           │         └──────────────┘                  │   │
           │                                            │   │
           └────────────────────────────────────────────┘   │
                                                            │
                                              ┌─────────────┘
                                              │
                                              ↓
                                    ┌──────────────────┐
                                    │TRANSFERENCIA A   │
                                    │HUMANO 📞         │
                                    └──────────────────┘
```

---

## 2. DETALLE: NODO ORQUESTADOR CON DECISIONES

```
                    ┌─────────────────────────┐
                    │ ÚLTIMO MENSAJE USUARIO  │
                    └────────────┬────────────┘
                                 │
                                 ↓
                    ┌─────────────────────────┐
                    │ORQUESTADOR ANALIZA:     │
                    │                         │
                    │ • Palabras clave        │
                    │ • Intención             │
                    │ • Contexto              │
                    │ • Estado anterior       │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ↓                        ↓                        ↓
  ┌──────────────┐      ┌──────────────┐      ┌─────────────────┐
  │ ¿PREGUNTA?   │      │ ¿SÍNTOMA?    │      │ ¿ACCIÓN?        │
  │              │      │              │      │                 │
  │ Keywords:    │      │ Keywords:    │      │ Keywords:       │
  │ ¿            │      │ vibra        │      │ agendar         │
  │ cuándo       │      │ ruido        │      │ reservar        │
  │ quién        │      │ no enciende  │      │ cita            │
  │ dónde        │      │ falla        │      │ turno           │
  │ horario      │      │ problema     │      │ fecha           │
  │ precio       │      │ síntomas     │      │ hora            │
  └──────┬───────┘      └──────┬───────┘      └────────┬────────┘
         │                     │                       │
         ↓                     ↓                       ↓
    NODO_FAQ          RAMA_DIAGNOSTICO      RAMA_AGENDAMIENTO
         │                     │                       │
         ├─ Taller ────────┐   │                       │
         ├─ Equipo ────────┤   │                       │
         ├─ Mecánica ──────┤   │                       │
         │                 │   │                       │
         │ RESPONDE        │   │ DIAGNÓSTICO          │ RECOPILA
         │ PREGUNTA        │   │ • Preguntas          │ DATOS
         │                 │   │ • Genera             │ • Nombre
         └──→ ¿Siguiente?  │   │   diagnóstico        │ • Teléfono
             │             │   │ • Pide confirmación  │ • Fecha
        ┌────┴────┐        │   │                      │ • Hora
        ↓         ↓        │   └──→ CONFIRMA?         │ • Mecánico
      MENÚ    DIAGNÓSTICO  │       │                  │
        │         │        │       ├─ SÍ ─────┐      │
        │         │        │       │           │      │
        │         └────────┘       └─ NO ──────┤      │
        │                                      │      │
        │          ┌────────────────────────────┴──────┤
        │          │                                   │
        └──────────┤                                   │
                   ↓                                   ↓
            FLUJO NORMAL                      VALIDACIÓN
            ACTUALIZADO                       • Festivos
                                              • Horarios
                                              • Datos
                                              
                                                   │
                                                   ↓
                                         TODOS DATOS
                                         CORRECTOS?
                                         │
                                    ┌────┴────┐
                                    ↓         ↓
                                  SÍ        NO
                                    │         │
                                    │    SOLICITA
                                    │    DATOS
                                    │    FALTANTES
                                    │
                                    ↓
                            RESUMEN + CONFIRMACIÓN
                            
                            ¿Correcciones?
                            │
                       ┌────┴────┐
                       ↓         ↓
                      SÍ        NO
                       │         │
                       │    AGENDAR
                    EDITAR   CITA ✅
                    │
                    └──→ Vuelve a RESUMEN
```

---

## 3. FLUJO FAQ DETALLADO

```
                    USUARIO HACE PREGUNTA
                            │
                            ↓
                    ┌────────────────────┐
                    │   NODO_FAQ         │
                    │                    │
                    │ Busca en:          │
                    │ • Taller (horarios)│
                    │ • Equipo (mecánico)│
                    │ • Mecánica (ej)    │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ↓                   ↓
            ┌──────────────┐    ┌──────────────┐
            │ ENCONTRÓ     │    │ NO ENCONTRÓ  │
            │ RESPUESTA    │    │              │
            └──────┬───────┘    └──────┬───────┘
                   │                   │
                   ↓                   ↓
            ┌──────────────┐    ┌─────────────────┐
            │ GENERA       │    │ REDIRIGE A      │
            │ RESPUESTA    │    │ DIAGNÓSTICO O   │
            │              │    │ AGENDAMIENTO    │
            └──────┬───────┘    └────────┬────────┘
                   │                     │
                   ├─────────────┬───────┘
                   │             │
                   ↓             ↓
            ┌──────────────────────────┐
            │ RETORNA:                 │
            │ {                        │
            │  tipo: "faq",            │
            │  categoria: "taller",    │
            │  respuesta: "...",       │
            │  siguiente_accion:       │
            │    "menu" |              │
            │    "diagnostico" |       │
            │    "agendamiento"        │
            │ }                        │
            └──────────┬───────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ↓            ↓            ↓
    ┌──────────┐ ┌──────────┐ ┌─────────────┐
    │ RESPONDE │ │ DIAGNÓS- │ │ AGENDAMIENTO│
    │ Y VUELVE │ │ TICO     │ │             │
    │ A MENÚ   │ │          │ │             │
    └──────────┘ └──────────┘ └─────────────┘
```

---

## 4. FLUJO COMPLETO: DIAGNÓSTICO → AGENDAMIENTO

```
                    ┌──────────────────────────────────┐
                    │ USUARIO: "Mi auto vibra al frenar"│
                    └────────────┬─────────────────────┘
                                 │
                                 ↓
                    ┌──────────────────────────────────┐
                    │ RAMA_DIAGNOSTICO                 │
                    └────────────┬─────────────────────┘
                                 │
                                 ↓
                    ┌──────────────────────────────────┐
                    │ BOT: Hace 3-4 preguntas          │
                    │ "¿Cuándo comenzó?                │
                    │  ¿Continuo o intermitente?       │
                    │  ¿Otros síntomas?"               │
                    └────────────┬─────────────────────┘
                                 │
                                 ↓
                    ┌──────────────────────────────────┐
                    │ USUARIO: Responde preguntas      │
                    └────────────┬─────────────────────┘
                                 │
                                 ↓
                    ┌──────────────────────────────────┐
                    │ BUSCA EN RAG (hasta 3 veces)     │
                    │                                  │
                    │ ¿Encontró?                       │
                    └────────┬──────────────┬──────────┘
                             │              │
                         SÍ  │              │  NO
                             ↓              ↓
                    ┌─────────────┐  ┌──────────────┐
                    │ USA DOC RAG │  │ USA LLM      │
                    └────────┬────┘  └──────┬───────┘
                             │             │
                             └──────┬──────┘
                                    │
                                    ↓
                    ┌──────────────────────────────────┐
                    │ GENERA DIAGNÓSTICO:              │
                    │ 📋 DIAGNÓSTICO PRELIMINAR        │
                    │ • Posible falla: ...             │
                    │ • Causa probable: ...            │
                    │ • Urgencia: Media                │
                    │                                  │
                    │ ¿Deseas proceder?                │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ USUARIO RESPONDE        │
                    └────┬───────────────┬────┘
                         │ SÍ            │ NO
                         ↓               ↓
                    ┌──────────┐   ┌──────────────┐
                    │ diagnosis│   │ Repite       │
                    │_complete=│   │ diagnóstico  │
                    │ True     │   │              │
                    └────┬─────┘   └──────────────┘
                         │
                         ↓
                    ┌──────────────────────────────────┐
                    │ BOT: "Perfecto, procederemos.    │
                    │ ¿Cuándo quieres agendar la cita?"│
                    └────────────┬─────────────────────┘
                                 │
                                 ↓ RAMA AGENDAMIENTO
                    ┌──────────────────────────────────┐
                    │ EXTRACTOR_DATOS:                 │
                    │ • Parsea fecha                   │
                    │ • Parsea hora                    │
                    │ • Valida (festivo, horario)      │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────┴──────────────┐
                    │ TODOS DATOS?              │
                    └───┬───────────────────┬───┘
                        │ NO                │ SÍ
                        ↓                   ↓
                    ┌──────────────┐   ┌────────────────┐
                    │ SOLICITA     │   │ CONSULTA       │
                    │ DATOS        │   │ DISPONIBILIDAD │
                    │ FALTANTES    │   └────────┬───────┘
                    └────────┬─────┘            │
                             │                 ↓
                             └────→ LISTA MECÁNICOS
                                    ↓
                                ¿SELECCIONA?
                                    │
                                    ↓
                    ┌──────────────────────────────────┐
                    │ RESUMEN DE CITA:                 │
                    │ 👤 Nombre: ...                   │
                    │ 📱 Teléfono: ...                 │
                    │ 👨‍🔧 Mecánico: ...                │
                    │ 📅 Fecha: ...                    │
                    │ 🕐 Hora: ...                     │
                    │ 🔧 Servicio: ...                 │
                    │                                  │
                    │ ¿TODO CORRECTO?                  │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ USUARIO RESPONDE        │
                    └────┬───────────────┬────┘
                         │ NO            │ SÍ
                         ↓               ↓
                    ┌──────────┐   ┌──────────────┐
                    │ ¿Cambiar │   │ BOOKING_AGENT│
                    │ cuál?    │   │ CREA CITA ✅ │
                    │          │   │              │
                    │ EDITA    │   │ Confirmación:│
                    │ CAMPO    │   │ TM-XXXXX ✅  │
                    │          │   │              │
                    │ Vuelve a │   │ FIN          │
                    │ RESUMEN  │   │              │
                    └────┬─────┘   └──────────────┘
                         │
                         └─→ Vuelve a RESUMEN
                             ↓
                        ¿LISTO?
                             │
                        ┌────┴────┐
                        ↓         ↓
                       SÍ        NO
                        │         │
                        │    Vuelve a EDITAR
                        │
                        ↓
                    CITA AGENDADA ✅
```

---

## 5. TABLA DE ENRUTAMIENTO (ROUTER)

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    DECISIONES DEL ORQUESTADOR                             ║
╠═════════════════════════════════════════╦════════════════════════════════╣
║ CONDICIÓN / ENTRADA                     ║ RUTA → NODO                    ║
╠═════════════════════════════════════════╬════════════════════════════════╣
║ "¿A qué hora abren?"                    ║ → nodo_faq → menu              ║
║ "¿Quién es Juan?"                       ║ → nodo_faq → consultar_mecanico║
║ "¿Qué es un motor?"                     ║ → nodo_faq → diagnostico       ║
╠─────────────────────────────────────────╬────────────────────────────────╣
║ "Mi auto vibra"                         ║ → rama_diagnostico             ║
║ "No enciende"                           ║ → rama_diagnostico             ║
║ "Ruido en el motor"                     ║ → rama_diagnostico             ║
╠─────────────────────────────────────────╬────────────────────────────────╣
║ "Quiero agendar"                        ║ → rama_agendamiento            ║
║ "Dame una cita"                         ║ → rama_agendamiento            ║
║ (después de diagnóstico confirmado)     ║ → rama_agendamiento            ║
╠─────────────────────────────────────────╬────────────────────────────────╣
║ "Quiero hablar con un asesor"           ║ → agregador (handoff) 1ª vez   ║
║ "Transferencia a humano" (insiste)      ║ → agregador (handoff) definitivo║
╠─────────────────────────────────────────╬────────────────────────────────╣
║ "Cambiar fecha" (en agendamiento)       ║ → pedir_datos_faltantes        ║
║ "Cambiar mecánico" (en agendamiento)    ║ → pedir_datos_faltantes        ║
║ "Corregir nombre" (en agendamiento)     ║ → pedir_datos_faltantes        ║
╠─────────────────────────────────────────╬────────────────────────────────╣
║ No reconocido / Indefinido              ║ → rama_diagnostico (default)   ║
╚═════════════════════════════════════════╩════════════════════════════════╝
```

---

## 6. CICLO DE VIDA DE UN MENSAJE

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USUARIO ESCRIBE MENSAJE                                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 2. SERVIDOR RECIBE (server.py)                                  │
│    - Extrae thread_id                                           │
│    - Prepara payload                                            │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 3. LANGGRAPH API PROCESA                                        │
│    - Crea HumanMessage                                          │
│    - Invoca grafo del agente                                    │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 4. NODO ORQUESTADOR                                             │
│    - Analiza última entrada                                     │
│    - Decide ruta                                                │
└──────────────────┬──────────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        │          │          │          │
        ↓          ↓          ↓          ↓
     FAQ    DIAGNÓSTICO AGENDAMIENTO HANDOFF
        │          │          │          │
        └──────────┼──────────┼──────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 5. PROCESA EN EL NODO                                           │
│    - Ejecuta lógica                                             │
│    - Actualiza estado                                           │
│    - Genera AIMessage                                           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 6. NODO AGREGADOR                                               │
│    - Consolida mensajes                                         │
│    - Actualiza estado final                                     │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 7. RETORNA AL SERVIDOR                                          │
│    - Estado actualizado                                         │
│    - Último mensaje (respuesta)                                 │
│    - thread_id                                                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 8. SERVIDOR RESPONDE (server.py → chat.html)                    │
│    - Formatea JSON                                              │
│    - Envía al cliente                                           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────────┐
│ 9. FRONTEND RENDERIZA                                           │
│    - Muestra mensaje del bot                                    │
│    - Renderiza Markdown                                         │
│    - Listo para siguiente mensaje                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. MATRIZ DE ESTADOS

```
┌───────────────────────────────────────────────────────────────────┐
│                      FLUJOS Y ESTADOS                             │
├─────────────────────────────────────────────────────────────────┬─┤
│ FASE               │ diagnosis_complete │ booking_confirmed │ state
├─────────────────────────────────────────────────────────────────┤
│ Inicial            │ False              │ False            │ ready
│ Diagnóstico        │ True               │ False            │ diag_ok
│ Agendamiento       │ True               │ False            │ booking
│ Confirmación       │ True               │ True             │ done ✅
│ FAQ (taller)       │ False              │ False            │ faq_ok
│ Transferencia      │ (any)              │ (any)            │ transfer
└───────────────────────────────────────────────────────────────────┘
```

---

**Documento generado:** 13 de Mayo 2026  
**Versión:** 1.0  
**Tipo:** Diagramas de Flujo Visual
