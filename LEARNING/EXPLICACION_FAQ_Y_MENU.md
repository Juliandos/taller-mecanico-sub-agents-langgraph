# 🎯 Nodo FAQ y Sistema de Menú - Explicación Completa

## ¿QUÉ ES EL MENÚ?

El **MENÚ** es el **mensaje inicial** que aparece al cargar el chat:

```
┌────────────────────────────────────────────────────┐
│  ¡Hola! 👋 **Bienvenido a Taller Mecánico**      │
│                                                    │
│  Soy tu asistente inteligente y puedo            │
│  ayudarte con:                                    │
│                                                    │
│  🔧 DIAGNÓSTICO DE FALLAS                        │
│     Describe el problema y te ayudaré a          │
│     identificar qué está mal                     │
│                                                    │
│  📅 AGENDAR CITA                                 │
│     Elige fecha, hora y mecánico especializado   │
│                                                    │
│  👨‍🔧 ELEGIR MECÁNICO                             │
│     Conoce nuestro equipo de expertos            │
│                                                    │
│  ❓ PREGUNTAS SOBRE EL TALLER                    │
│     Información, horarios, ubicación             │
│                                                    │
│  📞 TRANSFERENCIA A HUMANO                       │
│     Si prefieres hablar con un asesor            │
│                                                    │
│  ¿Por dónde quieres empezar?                     │
└────────────────────────────────────────────────────┘
```

---

## FUNCIONES DEL NODO FAQ

El nodo FAQ no solo responde preguntas. Tiene **6 funciones principales**:

### 1️⃣ RESPONDER PREGUNTAS SOBRE EL TALLER

```
USER: "¿A qué hora abren?"
       │
       ↓
NODO_FAQ: Busca en base de conocimiento
       │
       ↓
BOT: "Abrimos:
     • Lunes a Viernes: 08:00 - 18:00
     • Sábado: 09:00 - 14:00
     • Domingo: CERRADO"
       │
       ↓
¿SIGUIENTE ACCIÓN?
├─ "Otro pregunta" → FAQ nuevamente
├─ "Quiero agendar" → RAMA_AGENDAMIENTO
└─ Sin respuesta → Vuelve a MENÚ
```

**Preguntas que responde:**
- "¿A qué hora abren?"
- "¿Dónde están?"
- "¿Cuál es su misión?"
- "¿Teléfono?"
- "¿Email?"
- "¿Garantía?"

---

### 2️⃣ RESPONDER PREGUNTAS SOBRE EL EQUIPO (Mecánicos)

```
USER: "¿Quién es el mejor para motor?"
       │
       ↓
NODO_FAQ: Busca especialidades
       │
       ↓
BOT: "Juan García es nuestro especialista en motor.
     Tiene 15 años de experiencia.
     
     ¿Te gustaría agendar con Juan?"
       │
       ↓
RETORNA: {
  "siguiente_accion": "consultar_mecanico",
  "mecanico_sugerido": "Juan García"
}
       │
       ↓
ESTADO: selected_mechanic = "Juan García"
       │
       ↓
Si usuario dice "sí" → Va directo a AGENDAMIENTO
                       con Juan preseleccionado
```

**Preguntas que responde:**
- "¿Quién atiende de motor?"
- "¿Quién es María López?"
- "¿Cuáles son las especialidades?"
- "¿Quién es el mejor para X?"
- "¿Disponibilidad de Juan?"

---

### 3️⃣ RESPONDER PREGUNTAS DE MECÁNICA

```
USER: "¿Qué es un cambio de bujías?"
       │
       ↓
NODO_FAQ: Busca en conocimiento de mecánica
       │
       ↓
BOT: "Las bujías son componentes que generan
     chispas para encender la mezcla en el motor.
     Duran típicamente 10,000-30,000 km.
     
     ¿Crees que tu auto necesita cambio de bujías?
     ¿Qué síntomas tiene?"
       │
       ↓
RETORNA: {
  "siguiente_accion": "diagnostico",
  "hint": "Interesado en diagnóstico de bujías"
}
       │
       ↓
RAMA_DIAGNOSTICO: Comienza diagnóstico
```

**Preguntas que responde:**
- "¿Qué es una transmisión?"
- "¿Cuánto cuesta un cambio de aceite?"
- "¿Cuánto tarda una reparación?"
- "¿Qué es diagnóstico completo?"

---

### 4️⃣ GUARDAR INFORMACIÓN EN EL ESTADO

El FAQ no solo responde, **almacena información** para facilitar agendamiento:

```
USER: "¿Quién es la mejor para frenos?"
       │
       ↓
NODO_FAQ: Responde "María López"
       │
       ↓
ALMACENA EN ESTADO:
{
  "selected_mechanic": "María López",
  "selected_area": "Frenos",
  "mecanico_hint": "Usuario preguntó por ella"
}
       │
       ↓
Si usuario después dice "agendar":
→ RAMA_AGENDAMIENTO YA SABE QUE QUIERE A MARÍA
→ No pregunta "¿Con cuál mecánico?"
→ Más rápido y eficiente ✅
```

---

### 5️⃣ DETECTAR INTENCIÓN OCULTA

El FAQ es **inteligente** en detectar lo que realmente quiere el usuario:

```
CASO 1:
USER: "¿Cuánto cuesta una reparación?"
       │
       ↓
FAQ: Responde precio, pero TAMBIÉN:
     "¿Quieres agendar una cita?"
       │
       ↓
ESTADO: "probablemente_quiere_agendar" = True
```

```
CASO 2:
USER: "¿Atienden sábado?"
       │
       ↓
FAQ: Responde "Sí, 09:00-14:00", pero TAMBIÉN:
     "¿Quieres agendar para el sábado?"
       │
       ↓
ESTADO: preferred_date_hint = "Sábado"
```

```
CASO 3:
USER: "¿Qué síntomas tiene motor enfermo?"
       │
       ↓
FAQ: Responde, pero RECONOCE:
     "Este usuario probablemente tiene problema de motor"
       │
       ↓
ESTADO: potential_damaged_part = "Motor"
```

---

### 6️⃣ REDIRIGIR A LOS OBJETIVOS PRINCIPALES

El FAQ decide dónde llevar al usuario:

```
┌─────────────────────────────────────────────────────┐
│ NODO_FAQ RETORNA (siguiente_accion):                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│ │   "menu"    │  │"diagnostico" │  │"agendamiento"│
│ │             │  │              │  │            │ │
│ │ Vuelve a    │  │ Inicia        │  │ Va directo │ │
│ │ menú si:    │  │ diagnóstico   │  │ a agendar  │ │
│ │             │  │ si:           │  │ si:        │ │
│ │ • Solo      │  │               │  │            │ │
│ │   responde  │  │ • Usuario     │  │ • Usuario  │ │
│ │ • No hay    │  │   pregunta    │  │   pregunta │ │
│ │   intención │  │   síntomas    │  │ sobre      │ │
│ │   clara     │  │ • O FAQ       │  │ agendamiento
│ │             │  │   sugiere     │  │ • O FAQ    │ │
│ │             │  │   diagnóstico │  │   sugiere  │ │
│ │             │  │               │  │   agendar  │ │
│ └─────────────┘  └──────────────┘  └────────────┘ │
│                                                     │
│ ┌──────────────────────────────────┐              │
│ │   "consultar_mecanico"          │              │
│ │                                  │              │
│ │ Va a AGENDAMIENTO con mecánico  │              │
│ │ preseleccionado si:              │              │
│ │ • Usuario pregunta por específico│              │
│ │ • FAQ identifica cuál quiere     │              │
│ └──────────────────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

---

## FLUJO COMPLETO: FAQ EN CONTEXTO

```
┌─────────────────────────────────────────────────────────────────┐
│                     USUARIO ENTRA AL CHAT                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────┐
        │  MUESTRA MENÚ INICIAL           │
        │                                 │
        │  🔧 Diagnóstico                │
        │  📅 Agendar                    │
        │  👨‍🔧 Elegir mecánico            │
        │  ❓ Preguntas                  │  ← AQUÍ ESTÁ EL MENÚ
        │  📞 Transferencia              │
        └────────────┬────────────────────┘
                     │
                     ↓
              USUARIO ELIGE
              UNA OPCIÓN
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
        ↓            ↓            ↓              ↓
    PREGUNTA    SÍNTOMA       AGENDAR    TRANSFERENCIA
    ("¿Qué...")  ("Vibra...")  ("Cita")   ("Hablar...")
        │            │            │              │
        ↓            ↓            ↓              ↓
    NODO_FAQ   RAMA_DIAG    RAMA_AGEND      HANDOFF
        │            │            │              │
        ├─────────────────────────┼──────────────┘
        │                         │
        ↓                         ↓
    ┌──────────┐         ┌────────────────┐
    │RESPONDE  │         │RECOPILA DATOS  │
    │PREGUNTA  │         │VALIDA          │
    │          │         │LISTA MECÁNICOS │
    └────┬─────┘         └────────┬───────┘
         │                        │
         ├─ ¿Vuelve a preguntar?  ├─ ¿Más datos?
         │  → FAQ nuevamente      │  → Solicita
         │                        │
         ├─ ¿Quiere diagnosticar? ├─ Resumen
         │  → RAMA_DIAGNOSTICO    │  ↓
         │                        │ Confirmación
         ├─ ¿Quiere agendar?      │  ↓
         │  → RAMA_AGENDAMIENTO   │ CITA ✅
         │                        │
         └─ ¿Otra pregunta?
            → VUELVE A MENÚ
               (para elegir
                otra opción)
```

---

## DETALLE: ¿QUÉ SIGNIFICA "VUELVE A MENÚ"?

**"Vuelve a menú"** significa que después de responder una pregunta FAQ, el usuario puede:

### Opción A: Hacer otra pregunta
```
USER: "¿A qué hora abren?"
FAQ: "Abrimos de 08:00 a 18:00..."

USER: "¿Y quién atiende de frenos?"
FAQ: "María López atiende frenos..."

USER: "¿Cuánto cuesta?"
FAQ: "Entre $150,000 y $350,000..."
```

### Opción B: Elegir una acción del menú
```
USER: "¿A qué hora abren?"
FAQ: "Abrimos de 08:00 a 18:00..."

USER: "Listo, quiero agendar una cita"
ORQUESTADOR: Detecta "agendar"
             → RAMA_AGENDAMIENTO

O:

USER: "Mi auto vibra"
ORQUESTADOR: Detecta síntoma
             → RAMA_DIAGNOSTICO
```

### Opción C: Volver a ver el menú explícitamente
```
USER: "¿A qué hora abren?"
FAQ: "Abrimos de 08:00 a 18:00...

     ¿Hay algo más que pueda ayudarte?"

USER: "Muéstrame el menú otra vez"
SISTEMA: Muestra el menú inicial
         Usuario puede elegir cualquier opción
```

---

## MATRIZ DE COMPORTAMIENTO DEL FAQ

```
┌────────────────────────┬────────────────────┬─────────────────┐
│ TIPO DE PREGUNTA       │ RESPUESTA           │ SIGUIENTE ACCIÓN│
├────────────────────────┼────────────────────┼─────────────────┤
│ "¿A qué hora?"         │ Horarios            │ menu            │
│ "¿Dónde están?"        │ Ubicación           │ menu            │
│ "¿Teléfono?"           │ Contacto            │ menu            │
├────────────────────────┼────────────────────┼─────────────────┤
│ "¿Quién atiende X?"    │ Info mecánico       │ agendar (preslec│
│ "¿Quién es Juan?"      │ Bio de Juan         │ agendar (preslec│
├────────────────────────┼────────────────────┼─────────────────┤
│ "¿Qué es motor?"       │ Explicación técnica │ diagnostico     │
│ "¿Síntomas de X?"      │ Descripción         │ diagnostico     │
├────────────────────────┼────────────────────┼─────────────────┤
│ Cualquier otra         │ Respuesta general   │ menu            │
│ (no categorizada)      │ + sugerencia        │                 │
└────────────────────────┴────────────────────┴─────────────────┘
```

---

## DIAGRAMA: FAQ EN EL CONTEXTO GENERAL

```
                    ┌─────────────────────────────────┐
                    │    USUARIO VE MENÚ INICIAL      │
                    │                                 │
                    │ 🔧 Diagnóstico                 │
                    │ 📅 Agendar                     │
                    │ 👨‍🔧 Elegir mecánico             │
                    │ ❓ PREGUNTAS ← AQUÍ              │
                    │ 📞 Transferencia               │
                    └────────────┬────────────────────┘
                                 │
                                 ↓
        ┌────────────────────────────────────────┐
        │ USER ELIGE "PREGUNTAS SOBRE TALLER"   │
        │ (O HACE PREGUNTA DIRECTA)              │
        └────────────┬─────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────────────┐
        │  NODO_FAQ PROCESA                      │
        │                                        │
        │  • Identifica categoría                │
        │  • Busca en base de conocimiento       │
        │  • Genera respuesta                    │
        │  • Detecta intención oculta            │
        │  • Almacena en estado                  │
        └────────────┬─────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────────────┐
        │  BOT RESPONDE LA PREGUNTA              │
        │  + Pregunta de seguimiento             │
        │  + Sugerencia de acción                │
        └────────────┬─────────────────────────┘
                     │
        ┌────────────┴──────────────────────┐
        │ USUARIO PUEDE:                    │
        │                                   │
        ├─ Hacer OTRA pregunta              │
        │  → FAQ nuevamente (loop)          │
        │                                   │
        ├─ Elegir ACCIÓN del menú           │
        │  → Ir a Diagnóstico/Agendamiento  │
        │                                   │
        ├─ Decir "Menú" / "Mostrar opciones"│
        │  → Vuelve a MENÚ INICIAL          │
        │                                   │
        └─ Nada (silencio)                  │
           → Pregunta "¿Hay algo más?"      │
           → Espera nueva entrada           │
```

---

## EJEMPLO REAL: USUARIO HACE PREGUNTA Y LUEGO ELIGE

```
┌─ INICIO ─────────────────────────────────────────┐
│  BOT: [Muestra MENÚ INICIAL con 5 opciones]    │
└──────────────────────────────────────────────────┘

USER: "¿Cuándo abren mañana?"
       │
       ├─ ORQUESTADOR: "Es pregunta" → NODO_FAQ
       │
       └─ NODO_FAQ: Responde
          │
          └─ BOT: "Abrimos mañana viernes 09:00-18:00"
                   ↑
                   └─ Respuesta específica
                   
┌─ RESPUESTA ───────────────────────────────────────┐
│  BOT: "Abrimos mañana viernes de 09:00 a 18:00  │
│                                                  │
│       ¿Te gustaría agendar una cita para        │
│       mañana?"                                  │
└──────────────────────────────────────────────────┘

USER: "Sí, quiero agendar"
       │
       ├─ ORQUESTADOR: Detecta "agendar"
       │
       └─ ROUTE → RAMA_AGENDAMIENTO
          │
          ├─ ESTADO: preferred_date_hint = "Viernes 15"
          │         (FAQ pasó esta información)
          │
          └─ BOT: "Perfecto, vamos a agendar...
                   ¿Cuál es tu nombre?"
                   (Comienza agendamiento
                    con contexto de FAQ)
```

---

## RESUMEN FINAL

| Concepto | Qué es | Dónde | Función |
|----------|--------|-------|---------|
| **MENÚ** | Mensaje inicial | Se muestra al entrar | Guiar usuario a 5 opciones |
| **FAQ** | Nodo especializado | Entre menú y objetivos | Responder preguntas sin interrumpir flujo |
| **Vuelve a menú** | Opción después de FAQ | Cuando no hay intención clara | Mostrar opciones nuevamente |

---

**Documento generado:** 13 de Mayo 2026  
**Versión:** 1.0  
**Tipo:** Explicación de FAQ y Menú
