# 🔄 Flujo Completo del Agente con Nodo FAQ

## 📊 Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│          USUARIO INICIA CONVERSACIÓN                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │  BIENVENIDA INICIAL    │
        │  (Menú de opciones)    │
        └────────────┬───────────┘
                     │
        ┌────────────┴────────────────────────────┐
        │                                         │
        ↓                                         ↓
   ¿ES PREGUNTA?               ¿ACCIÓN ESPECÍFICA?
        │                                │
    ╔═══╩════════════════════════════╗  │
    ║  FAQ (Preguntas & Respuestas)  ║  │
    ╚═══╤════════════════════════════╝  │
        │                                │
    ┌───┴──────────────────────────────┬─┴────────────┐
    │                                  │              │
    ↓                                  ↓              ↓
RESPONDE              DIAGNÓSTICO   AGENDAMIENTO
PREGUNTA              (Rama 1)        (Rama 2)
    │
    └──→ ¿Vuelve al Menú o Continúa?
         ├─ "Sí, quiero diagnosticar" → DIAGNÓSTICO
         ├─ "Quiero agendar" → AGENDAMIENTO
         └─ "Otra pregunta" → FAQ
```

---

## 🎯 Escenario 1: Pregunta sobre el Taller → Menú

```
┌─ INICIO ──────────────────────────────────────────┐
│  BOT: [Mensaje de bienvenida con 5 opciones]    │
└───────────────────────────────────────────────────┘

USER: "¿A qué hora abren?"
  │
  ├─ ORQUESTADOR: "Es pregunta FAQ"
  │
  ├─ NODO_FAQ: Busca "horarios"
  │
  ├─ RETORNA:
  │   {
  │     "tipo": "faq",
  │     "categoria": "taller",
  │     "respuesta": "Abrimos L-V de 08:00-18:00, Sábado 09:00-14:00",
  │     "siguiente_accion": "menu"
  │   }
  │
  └─ AGREGADOR: Muestra respuesta + vuelve a menú

┌─ RESPUESTA ────────────────────────────────────────┐
│  BOT: "Abrimos:                                   │
│       • Lunes a Viernes: 08:00 - 18:00           │
│       • Sábado: 09:00 - 14:00                    │
│       • Domingo: CERRADO                         │
│                                                  │
│       ¿Hay algo más que pueda ayudarte?"         │
└───────────────────────────────────────────────────┘

USER: "Sí, quiero agendar una cita"
  │
  ├─ ORQUESTADOR: Detecta "agendar"
  └─ ROUTE → RAMA_AGENDAMIENTO ✅
```

---

## 🔧 Escenario 2: Pregunta sobre Mecánico → Agendamiento

```
┌─ INICIO ──────────────────────────────────────────┐
│  BOT: [Mensaje de bienvenida]                    │
└───────────────────────────────────────────────────┘

USER: "¿Quién es el mejor para problemas de motor?"
  │
  ├─ ORQUESTADOR: "Es pregunta FAQ sobre equipo"
  │
  ├─ NODO_FAQ: Busca mecánicos con especialidad motor
  │
  ├─ RETORNA:
  │   {
  │     "tipo": "faq",
  │     "categoria": "equipo",
  │     "respuesta": "Juan García es nuestro especialista...",
  │     "siguiente_accion": "consultar_mecanico",
  │     "mecanico_sugerido": "Juan García"
  │   }
  │
  └─ AGREGADOR: Muestra info del mecánico

┌─ RESPUESTA ────────────────────────────────────────┐
│  BOT: "👨‍🔧 Juan García es nuestro especialista   │
│       en motor, suspensión y transmisión.        │
│       Tiene 15 años de experiencia y es muy      │
│       confiable en diagnósticos.                 │
│                                                  │
│       ¿Te gustaría agendar una cita con Juan?   │
└───────────────────────────────────────────────────┘

USER: "Sí, quiero agendar con Juan"
  │
  ├─ ESTADO: selected_mechanic = "Juan García"
  ├─ ORQUESTADOR: Detecta "agendar"
  └─ ROUTE → RAMA_AGENDAMIENTO (con mecánico preseleccionado) ✅
```

---

## 📋 Escenario 3: Diagnóstico Completo con Correcciones

```
┌─ INICIO ──────────────────────────────────────────┐
│  BOT: [Mensaje de bienvenida]                    │
│  "¿Cuéntame qué problema tiene tu vehículo?"    │
└───────────────────────────────────────────────────┘

USER: "Mi auto vibra al frenar"
  │
  ├─ RAMA_DIAGNOSTICO: Busca RAG
  ├─ Genera diagnóstico
  │
  └─ BOT: "📋 DIAGNÓSTICO PRELIMINAR
          Posible causa: Pastillas de freno desgastadas
          Urgencia: Media
          
          ¿Deseas proceder con la reparación?"

USER: "Sí, adelante"
  │
  ├─ diagnosis_complete = True
  ├─ client_confirmed_diagnosis = True
  │
  └─ BOT: "✅ Perfecto, procederemos.
          ¿Cuándo quieres agendar la cita?
          Fecha y hora preferida."

USER: "Miércoles 20 a las 3 PM"
  │
  ├─ EXTRACTOR: Parsea fecha/hora
  ├─ Valida: miércoles 20 mayo = correcto ✅
  │
  └─ BOT: "¿Tu nombre por favor?"

USER: "Jorge García"
  │
  ├─ customer_name = "Jorge García"
  │
  └─ BOT: "¿Tu teléfono?"

USER: "3001234567"
  │
  ├─ phone = "3001234567"
  ├─ TODOS LOS DATOS COMPLETOS
  │
  └─ BOT: "📞 Consultando disponibilidad...
          
          👨‍🔧 ¿CON CUÁL MECÁNICO QUIERES TRABAJAR?
          1. Juan García (Motor, suspensión)
          2. María López (Frenos, dirección)
          3. Carlos Ruiz (Eléctrica, diagnóstico)
          4. Ana Martínez (Llantas, alineación)
          5. Roberto Sánchez (Transmisión)
          
          Responde: número o nombre"

USER: "Prefiero a María, es mujer y más confiable"
  │
  ├─ EXTRACTOR: Detecta "María"
  ├─ selected_mechanic = "María López"
  │
  ├─ ┌─ RESUMEN ANTES DE AGENDAR (NUEVA FEATURE)
  │  │  
  │  └─ BOT: "📋 REVISEMOS TU CITA:
  │        👤 Nombre: Jorge García
  │        📱 Teléfono: 3001234567
  │        👨‍🔧 Mecánico: María López
  │        📅 Fecha: Miércoles 20 de mayo
  │        🕐 Hora: 3:00 PM
  │        🔧 Servicio: Reparación de frenos
  │        
  │        ¿Todo está correcto?"

USER: "No, quiero cambiar la hora a las 2 PM"
  │
  ├─ ESTADO: correction_field = "hora"
  ├─ PEDIR_DATOS: "¿Qué hora prefieres?"
  │
  └─ USER: "2:00 PM"
     │
     ├─ appointment_data.preferred_time = "14:00"
     │
     └─ BOT: "📋 RESUMEN ACTUALIZADO:
           👤 Nombre: Jorge García
           📱 Teléfono: 3001234567
           👨‍🔧 Mecánico: María López
           📅 Fecha: Miércoles 20 de mayo
           🕐 Hora: 2:00 PM
           🔧 Servicio: Reparación de frenos
           
           ¿Listo para agendar?"

USER: "Sí, perfecto"
  │
  ├─ BOOKING_AGENT: Crea cita
  │
  └─ BOT: "✅ ¡CITA AGENDADA!
          
          📋 Confirmación: TM-45821
          👤 Cliente: Jorge García
          📅 Fecha: Miércoles 20 de mayo
          🕐 Hora: 2:00 PM
          🔧 Servicio: Reparación de frenos
          👨‍🔧 Mecánico: María López
          💰 Costo: $180,000-350,000
          
          ✅ OBJETIVO COMPLETADO"
```

---

## ❓ Escenario 4: Pregunta de Mecánica → Diagnóstico

```
┌─ INICIO ──────────────────────────────────────────┐
│  BOT: [Mensaje de bienvenida]                    │
└───────────────────────────────────────────────────┘

USER: "¿Qué es un cambio de bujías?"
  │
  ├─ ORQUESTADOR: "Es pregunta FAQ sobre mecánica"
  │
  ├─ NODO_FAQ: Busca "bujías"
  │
  ├─ RETORNA:
  │   {
  │     "tipo": "faq",
  │     "categoria": "mecanica",
  │     "respuesta": "Las bujías son...",
  │     "siguiente_accion": "diagnostico",
  │     "hint": "¿Crees que tu auto necesita cambio de bujías?"
  │   }
  │
  └─ AGREGADOR: Muestra explicación + pregunta

┌─ RESPUESTA ────────────────────────────────────────┐
│  BOT: "Las bujías son componentes que generan  │
│       chispas para encender la mezcla de       │
│       gasolina en el motor.                    │
│                                                │
│       Típicamente duran 10,000-30,000 km      │
│       dependiendo del tipo.                   │
│                                                │
│       ¿Crees que tu auto necesita cambio      │
│       de bujías? ¿Qué síntomas tiene?"        │
└───────────────────────────────────────────────┘

USER: "Sí, a veces no enciende bien, tarda"
  │
  ├─ RAMA_DIAGNOSTICO: Comienza diagnóstico
  └─ Sigue el flujo de diagnóstico completo ✅
```

---

## 🔄 Escenario 5: Cambios de Opinión & Correcciones

```
USER: "Espera, cambio de opinión sobre el mecánico"
  │
  ├─ ESTADO: Detecta "cambio de opinión"
  ├─ ORQUESTADOR: Pregunta "¿Qué quieres cambiar?"
  │
  └─ BOT: "¿Qué quieres cambiar?
         - Diagnóstico
         - Mecánico
         - Fecha
         - Hora
         - Cancelar"

USER: "El mecánico, quiero a Juan"
  │
  ├─ selected_mechanic = "Juan García"
  ├─ Vuelve a mostrar RESUMEN
  │
  └─ Continúa agendamiento ✅
```

---

## 📞 Escenario 6: Transferencia a Humano

```
USER: "Quiero hablar con un asesor, no me siento cómodo"
  │
  ├─ ORQUESTADOR: Detecta "hablar con asesor"
  ├─ human_transfer_requests = 1
  │
  ├─ AGREGADOR: Primera solicitud
  │
  └─ BOT: "Entiendo, antes de transferirte,
          ¿cuál es el problema con tu vehículo?"

USER: "Mejor transfierme, gracias"
  │
  ├─ human_transfer_requests = 2
  │
  ├─ AGREGADOR: Segunda solicitud = Handoff
  │
  └─ BOT: "De acuerdo. Un asesor se comunicará contigo pronto.
          
          🎫 Ticket: HT-7234
          ⏰ Respuesta: dentro de 24 horas
          📞 Línea: 300-AUTO-PRO
          
          ✅ TRANSFERENCIA COMPLETADA
          Recarga la página para nueva conversación"
```

---

## 🎯 Tabla de Decisiones del Orquestador

| Entrada del Usuario | Detecta | Acción | Router |
|-------------------|---------|--------|---------|
| "Mi auto vibra al frenar" | Síntoma | Diagnóstico | `rama_diagnostico` |
| "Quiero agendar cita" | Acción | Agendamiento | `rama_agendamiento` |
| "¿A qué hora abren?" | FAQ/Taller | Responde FAQ | `nodo_faq` → `menu` |
| "¿Quién es Juan?" | FAQ/Equipo | Responde FAQ | `nodo_faq` → `consultar_mecanico` |
| "¿Qué es motor?" | FAQ/Mecánica | Responde FAQ | `nodo_faq` → `diagnostico` |
| "Hablar con humano" | Transferencia | Handoff | `agregador` (handoff) |
| "Cambiar fecha" | Corrección | Pedir nuevo valor | `pedir_datos_faltantes` |
| "Ninguna opción" | No reconocido | Solicita aclaración | `rama_diagnostico` (default) |

---

## 📊 Estado del Sistema (State)

```python
# Ejemplo de estado en medio de conversación

state = {
    "messages": [
        # Historial completo de mensajes
    ],
    
    # DATOS RECOPILADOS
    "customer_name": "Jorge García",
    "phone": "3001234567",
    
    # DIAGNÓSTICO
    "damaged_part": "Pastillas de freno",
    "diagnosis_complete": True,
    "client_confirmed_diagnosis": True,
    "diagnostico_summary": "...",
    
    # AGENDAMIENTO
    "appointment_data": {
        "preferred_date": "2026-05-20",
        "preferred_time": "14:00",
        "service": "Reparación de frenos"
    },
    
    # MECÁNICO
    "mecanicos_disponibles": [...],
    "selected_mechanic": "María López",
    "selected_area": "Frenos",
    
    # CONTROL DE FLUJO
    "booking_confirmed": False,
    "requires_human": False,
    "human_transfer_requests": 0,
    "data_confirmed": False,  # NUEVA: si usuario confirmó antes de agendar
    "correction_field": "preferred_time",  # NUEVA: qué campo está editando
}
```

---

## ✨ Ventajas del Nuevo Flujo

| Antes | Ahora |
|-------|-------|
| Usuario hace pregunta → Confusión | Usuario hace pregunta → FAQ responde → Vuelve al menú |
| Citas sin confirmación | Resumen + confirmación antes de agendar |
| No se pueden cambiar datos | Permite cambiar cualquier dato antes de agendar |
| Sin opción de preguntas | Preguntas sobre taller/equipo integradas |
| Transferencia solo con insistencia | Opción clara desde el inicio |

---

**Documento generado:** 13 de Mayo 2026  
**Versión:** 1.0  
**Estado:** Propuesta de flujo completo
