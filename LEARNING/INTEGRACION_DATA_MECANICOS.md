# 🔧 Integración de Data Mock de Mecánicos

## ¿QUÉ SE AGREGÓ?

Nuevo archivo: **`src/agents/taller/data_mecanicos.py`**

Contiene:
- ✅ **5 mecánicos** con información completa (nombre, teléfono, experiencia, especialidades, procesos)
- ✅ **Festivos 2026** actualizados (todos los de Colombia)
- ✅ **Información del taller** (misión, visión, contacto, servicios)
- ✅ **Funciones helper** para buscar y filtrar

---

## 📋 ESTRUCTURA DE UN MECÁNICO

```python
{
    "id": "MEX001",
    "nombre": "Juan García",
    "numero": "300-555-0101",
    "experiencia_anos": 15,
    "tiempo_empresa_anos": 8,
    "especialidad_principal": "Motor y Transmisión",
    "especialidades": ["Motor", "Transmisión", "Suspensión"],
    
    "bio": "Especialista en diagnóstico de motor...",
    
    "procesos_generales": [
        "Revisión visual",
        "Diagnóstico con escáner",
        ...
    ],
    
    "procesos_especializados": {
        "Motor": ["Cambio de bujías", ...],
        "Transmisión": ["Cambio de aceite", ...],
    },
    
    "diagnosticos_rag_relacionados": [
        "vibra al frenar",
        "no acelera bien",
        ...
    ],
    
    "horarios_disponibles": {
        "lunes": ["09:00", "10:00", ...],
        ...
    }
}
```

---

## 🔗 CÓMO USAR EN LOS NODOS

### 1. EN NODO_FAQ (Preguntas sobre mecánicos)

```python
from agents.taller.data_mecanicos import (
    get_mecanicos,
    get_mecanico_por_nombre,
    get_mecanicos_por_especialidad,
    TALLER_INFO
)

def responder_pregunta_mecanico(pregunta):
    """Responde preguntas sobre el equipo"""
    
    # Ejemplo: "¿Quién es el mejor para motor?"
    if "motor" in pregunta.lower():
        mecanicos = get_mecanicos_por_especialidad("Motor")
        respuesta = f"Tenemos {len(mecanicos)} especialistas en motor:\n"
        for m in mecanicos:
            respuesta += f"- {m['nombre']}: {m['bio'][:100]}...\n"
        return respuesta
    
    # Ejemplo: "¿Quién es María?"
    mecanico = get_mecanico_por_nombre("María")
    if mecanico:
        return f"{mecanico['nombre']}\n{mecanico['bio']}"
```

### 2. EN RAMA_AGENDAMIENTO (Selección de mecánico)

```python
from agents.taller.data_mecanicos import get_mecanicos

def pedir_datos_faltantes(state):
    """Mostrar lista de mecánicos con info"""
    
    if "select_mechanic" in missing_fields:
        mecanicos = get_mecanicos()
        
        mecanicos_text = "\n".join([
            f"   {i}. {m['nombre']} ({m['especialidad_principal']})"
            f" - {m['experiencia_anos']} años"
            for i, m in enumerate(mecanicos, 1)
        ])
        
        ask_msg = f"""¿Con cuál mecánico prefieres trabajar?

{mecanicos_text}

Responde con el número (1-5) o di "cualquiera" """
```

### 3. EN VALIDACIÓN DE FESTIVOS

```python
from agents.taller.data_mecanicos import is_holiday_2026, get_holiday_name

def _check_holiday(date_str):
    """Verificar si es festivo"""
    
    if is_holiday_2026(date_str):
        holiday_name = get_holiday_name(date_str)
        return (True, holiday_name)
    return (False, "")
```

---

## 📊 INFORMACIÓN POR MECÁNICO

### 1. Juan García - Motor y Transmisión
```
Experiencia: 15 años
En empresa: 8 años
Especialidades: Motor, Transmisión, Suspensión
Teléfono: 300-555-0101
Procesos: 15+ especializados

Diagnósticos detecta:
- vibra al frenar
- no acelera bien
- pierde potencia
- consume mucho aceite
- hace ruido en motor
```

### 2. María López - Frenos y Dirección
```
Experiencia: 12 años
En empresa: 6 años
Especialidades: Frenos, Dirección, Suspensión
Teléfono: 300-555-0102
Procesos: 16+ especializados

Diagnósticos detecta:
- vibra al frenar
- frenos blandos
- dirección dura
- hace ruido al girar
- auto se va a un lado
```

### 3. Carlos Ruiz - Eléctrica y Diagnóstico
```
Experiencia: 18 años
En empresa: 10 años
Especialidades: Eléctrica, Diagnóstico, Motor
Teléfono: 300-555-0103
Procesos: 14+ especializados

Diagnósticos detecta:
- no enciende
- luces parpadean
- batería muere
- alternador falla
- códigos de error
```

### 4. Ana Martínez - Llantas y Alineación
```
Experiencia: 10 años
En empresa: 5 años
Especialidades: Llantas, Alineación, Balanceo
Teléfono: 300-555-0104
Procesos: 12+ especializados

Diagnósticos detecta:
- auto se va a un lado
- llanta pinchada
- vibra en carretera
- desgaste irregular
- ruido en llantas
```

### 5. Roberto Sánchez - Transmisión Automática
```
Experiencia: 16 años
En empresa: 9 años
Especialidades: Transmisión, Caja Automática, Embrague
Teléfono: 300-555-0105
Procesos: 14+ especializados

Diagnósticos detecta:
- cambios duros
- pierde velocidades
- retraso en cambio
- resbalon de embrague
- fluido de transmisión oscuro
```

---

## 🗓️ FESTIVOS 2026 ACTUALIZADOS

```python
Enero:    1 (Año Nuevo), 12 (Reyes)
Marzo:    30 (Lunes Santo), 31 (Martes Santo)
Abril:    1 (Miércoles Santo)
Mayo:     1 (Día Trabajo), 14 (Ascensión), 25 (Corpus Christi)
Junio:    1 (Sagrado Corazón), 8 (Pentecostés), 29 (San Pedro)
Julio:    1 (San Pedro trasladado)
Agosto:   7 (Batalla Boyacá), 15 (Asunción), 17 (Asunción trasladado)
Octubre:  12 (Día Raza), 19 (Día Raza trasladado)
Noviembre: 1 (Todos Santos), 2 (Todos Santos trasladado),
           11 (Independencia Cartagena), 16 (Independencia trasladado)
Diciembre: 8 (Inmaculada), 25 (Navidad), 28 (Navidad trasladado)
```

---

## 🔄 FLUJOS QUE UTILIZAN DATA_MECANICOS

### FAQ → Preguntas sobre Mecánico
```
USER: "¿Quién es mejor para motor?"
      ↓
FAQ: get_mecanicos_por_especialidad("Motor")
      ↓
Retorna Juan García y Carlos Ruiz
      ↓
BOT: Muestra bio + experiencia + procesos
      ↓
Si user selecciona → selected_mechanic = "Juan García"
```

### Agendamiento → Selección Mecánico
```
EXTRACTOR: Recopila nombre, teléfono, fecha, hora
      ↓
CONSULTAR DISPONIBILIDAD: get_mecanicos()
      ↓
Muestra lista con experiencia + especialidad
      ↓
User selecciona: "2" → María López
      ↓
ESTADO: selected_mechanic = "María López"
        selected_area = "Frenos, Dirección"
```

### Validación → Festivos
```
USER: "Miércoles 20 de mayo"
      ↓
EXTRACTOR: Parsea fecha → "2026-05-20"
      ↓
_check_holiday(): is_holiday_2026("2026-05-20")
      ↓
Festivo: "Ascensión del Señor"
      ↓
BOT: "Lo siento, ese día estamos cerrados"
```

---

## 🚀 PRÓXIMAS MEJORAS

1. **Integrar con RAG**: Los procesos especializados se pueden usar para enriquecer respuestas de diagnóstico
2. **Horarios dinámicos**: Usar horarios_disponibles para filtrar citas
3. **Búsqueda semántica**: Embeddings de procesos para diagnóstico automático
4. **Base de datos**: Migrar data_mecanicos.py a PostgreSQL

---

**Documento generado:** 14 de Mayo 2026  
**Versión:** 1.0  
**Estado:** Archivo creado e integración lista
