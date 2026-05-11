# Taller Mecánico - Agente de Diagnóstico y Agendamiento

Un agente inteligente basado en LangGraph que maneja diagnóstico de vehículos y agendamiento de citas en un taller mecánico. Utiliza un arquitectura de dos ramas independientes con React Agents internos.

## 🎯 Características

- **Rama 1 - Diagnóstico**: React Agent que realiza diagnóstico basado en síntomas del cliente
  - Realiza preguntas empáticas
  - Busca información técnica en una base de datos RAG (pgvector)
  - Genera diagnóstico preliminar
  - Valida confirmación del cliente

- **Rama 2 - Agendamiento**: React Agent con tools para agendar citas
  - Extrae datos del cliente (nombre, teléfono, fecha, hora)
  - Consulta disponibilidad del taller (API simulada)
  - Valida información completa
  - Crea cita confirmada con ID único

## 📋 Requisitos Previos

- **Python 3.12+**
- **Git**
- **uv** (gestor de paquetes Python) o **pip**
- **Clave API de OpenAI** (para LLM)
- **WSL2** (opcional, recomendado en Windows)

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/Juliandos/taller-mecanico-sub-agents-langgraph.git
cd taller-mecanico-sub-agents-langgraph
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
OPENAI_API_KEY=sk-your-api-key-here
```

**Obtener tu API key:**
1. Ve a https://platform.openai.com/account/api-keys
2. Copia tu clave
3. Pégala en el archivo `.env`

### 3. Crear ambiente virtual

**Opción A: Con uv (recomendado)**
```bash
uv venv
source .venv/bin/activate  # En Linux/Mac/WSL
# o en PowerShell (Windows):
.\.venv\Scripts\Activate.ps1
```

**Opción B: Con pip**
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac/WSL
# o en PowerShell (Windows):
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```bash
uv pip install -r requirements.txt
# o
pip install -r requirements.txt
```

## 🎬 Ejecutar el Sistema Completo

El sistema tiene 3 componentes que deben estar corriendo:

### 1. LangGraph Dev (Puerto 2024)

**En Linux/Mac/WSL:**
```bash
cd /ruta/a/taller-mecanico-agent
source .venv/bin/activate
langgraph dev
```

**En PowerShell (Windows):**
```powershell
cd "C:\ruta\a\taller-mecanico-agent"
.\.venv\Scripts\Activate.ps1
langgraph dev
```

Verás:
```
🚀 API: http://127.0.0.1:2024
🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### 2. Servidor Web (Puerto 8080)

**En otra terminal (con venv activado):**
```bash
uv run python server.py
```

Verás:
```
✅ Servidor corriendo en http://127.0.0.1:8080
🔗 Conectando a LangGraph: http://127.0.0.1:2024
```

### 3. Chat Web - Acceso Local

- **Local:** http://127.0.0.1:8080
- **Con ngrok:** https://osmosis-earthling-bridged.ngrok-free.dev

### 4. (Opcional) ngrok para Acceso Público

```bash
ngrok http 8080
```

Obtendrás un link público (ej: `https://xxx-xxx-xxx.ngrok-free.dev`)

## 💬 Ejemplos de Conversación para Probar

### Ejemplo 1: Flujo Completo (Diagnóstico + Agendamiento)

```
Usuario: Hola, mi auto hace un ruido extraño en el motor

Agent: [Realiza preguntas empáticas sobre el síntoma]

Usuario: Comenzó hace una semana, es continuo

Agent: [Genera diagnóstico preliminar: Bujías y/o Filtro de aceite]

Usuario: Sí, está correcto, procede

Agent: [Acepta diagnóstico y transiciona a agendamiento]

Usuario: Mi nombre es Juan Mendoza, teléfono 3125478965, quiero mañana por la tarde

Agent: [Consulta disponibilidad, muestra mecánicos disponibles]

Usuario: Confirmado, adelante

Agent: ✅ CITA AGENDADA
Confirmación: TM-35012
Fecha: 2026-05-15
Hora: 15:00
Mecánico: Juan García
```

### Ejemplo 2: Con Datos Incompletos (Loop interno)

```
Usuario: Necesito agendar una cita urgente

Agent: [Pide información inicial]

Usuario: Me llamo Carlos, soy de La Paz

Agent: [Detecta que faltan: teléfono, fecha, hora]

Agent: Veo que falta información. Necesito:
- teléfono
- fecha
- hora

Usuario: Mi teléfono es 3108765432, próxima semana lunes a las 10:00

Agent: [Consulta disponibilidad con tools]

Agent: ✅ Disponibilidad confirmada
[Muestra mecánicos y áreas de servicio]

Usuario: Sí, confirmado

Agent: ✅ CITA AGENDADA
```

### Ejemplo 3: Sin Disponibilidad

```
Usuario: Hola, quiero agendar para hoy a las 8:00 AM

Agent: [Pide datos]

Usuario: Soy María García, 3118765432, hoy 8:00 AM

Agent: ❌ No hay disponibilidad para hoy a las 8:00 AM

Horarios del taller:
- Lunes-Viernes: 08:00-18:00
- Sábado: 09:00-14:00
- Domingo: CERRADO

¿Otra fecha/hora?
```

## 📁 Estructura del Proyecto

```
taller-mecanico-agent/
├── src/
│   └── agents/
│       └── taller/
│           ├── agent.py                    # Grafo principal
│           ├── state.py                    # Definición del estado
│           ├── nodes/
│           │   ├── orquestador/            # Router inicial
│           │   ├── rama_diagnostico/       # React Agent - Diagnóstico
│           │   │   ├── node.py
│           │   │   └── rag/
│           │   ├── rama_agendamiento/      # React Agent - Agendamiento
│           │   │   ├── evaluador_agendamiento.py
│           │   │   └── tools.py            # Tools para consultar API falsa
│           │   └── agregador/              # Consolidador de respuestas
│           └── rag/                        # Retriever para búsqueda RAG
├── langgraph.json                          # Configuración de LangGraph
├── pyproject.toml                          # Dependencias del proyecto
├── .env                                    # Variables de entorno (crear)
├── .gitignore                              # Archivos a ignorar
└── README.md                               # Este archivo
```

## 🔧 Flujo del Agente

```
START
  ↓
ORQUESTADOR
  ├─────────────────────────┬──────────────────────────┐
  ↓                         ↓
RAMA 1: DIAGNÓSTICO    RAMA 2: AGENDAMIENTO
  ↓                         ↓
EVALUADOR_PIEZA        EVALUADOR_AGENDAMIENTO
  ↓                      (React Agent + Tools)
[React Loop]             ├─ Tool: Extraer datos
  ├─ Preguntas empáticas ├─ Tool: Consultar disponibilidad
  ├─ Buscar RAG          ├─ Tool: Crear cita
  └─ Generar diagnóstico └─ Loop interno si faltan datos
  ↓                         ↓
  └─────────────┬───────────┘
                ↓
            AGREGADOR
                ↓
              __END__
```

## 🛠️ Variables de Entorno

```env
# Requerida: Clave API de OpenAI
OPENAI_API_KEY=sk-...

# Opcional: Configuración de LangGraph
LANGGRAPH_API_KEY=tu-clave-opcional
```

## 📚 Dependencias Principales

- **langchain**: Framework para construir aplicaciones LLM
- **langgraph**: Librería para construir grafos de agentes
- **openai**: Cliente API de OpenAI
- **pydantic**: Validación de datos

## 🐛 Solución de Problemas

### Error: "No module named 'langchain'"

```bash
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "OPENAI_API_KEY not set"

Asegúrate de tener un archivo `.env` en la raíz con:
```
OPENAI_API_KEY=sk-your-key-here
```

### Error: "Port 8123 already in use"

Studio intenta usar puerto 8123. Si está en uso:
```bash
# Cambia el puerto
langgraph dev --port 8124
```

### El agente no responde en Studio

1. Verifica que `langgraph dev` está ejecutándose
2. Recarga la página en el navegador (F5)
3. Revisa los logs en la terminal para errores
4. Asegúrate de que tu API key es válida

## 🧪 Testing Manual

Para probar el agente directamente sin Studio:

```bash
python -c "
from src.agents.taller.agent import agent
from langchain_core.messages import HumanMessage

result = agent.invoke({
    'messages': [HumanMessage(content='Hola, mi auto vibra al frenar')]
})
print(result['messages'][-1].content)
"
```

## 📖 Documentación Adicional

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [LangChain Docs](https://python.langchain.com/)

## 🤝 Contribuciones

Para reportar bugs o sugerir mejoras:
1. Abre un issue en GitHub
2. Describe el problema o feature
3. Incluye pasos para reproducir

## 📝 Notas Importantes

- ⚠️ El archivo `.env` contiene tu API key - **NUNCA lo commits a Git**
- El archivo `.gitignore` ya está configurado para protegerlo
- La base de datos de disponibilidad es simulada (API falsa)
- Los diagnósticos usan RAG con pgvector (requiere configuración de DB)

## ✨ Nuevas Características (Mayo 2026)

### Frontend Web con Chat
- **chat.html**: Interfaz web responsive con chat en tiempo real
- **server.py**: Servidor Python que conecta con LangGraph
- Soporte multimodal: Acepta entrada en múltiples formatos
- URL dinámica: Funciona con localhost y ngrok automáticamente

### Selección de Mecánico
- Mecánicos especializados con áreas de servicio
- Selección por número, nombre o aceptar recomendado
- Asignación automática según especialidad

### Validaciones Inteligentes
- **Festivos**: Detecta 18 de mayo (Pentecostés) y otros
- **Horarios**: 08:00-18:00 (L-V), 09:00-14:00 (sábado)
- **Fechas**: Rechazo de domingos, fechas pasadas
- **Teléfono**: Validación de 10+ dígitos
- **Períodos**: "por la mañana", "por la tarde" → horas automáticas

### Manejo de Mensajes Multimodales
- Detecta mecánico por número (1-5), nombre o aceptación
- Extrae datos de múltiples formatos de entrada
- Recuperación automática de errores
- Búsqueda sin LLM para mecánicos (eficiente)

## 📚 Documentación Ejecutiva

### EXPLICACION_AGENTE.md
Documentación completa para jefes/stakeholders:
- Arquitectura del sistema
- 5 fases del flujo completo
- Todas las opciones de respuesta con ejemplos
- Validaciones de negocio
- Casos de uso reales
- Métricas y ventajas

**Audiencia:** Directivos, Project Managers, Stakeholders

### EXPLICACION_CORTA.md
Guía rápida de 1 página:
- Flujo en 5 pasos simples
- Qué acepta / Qué rechaza
- Ejemplo rápido (2 min)
- Link directo para probar

**Audiencia:** Tu jefe, clientes, usuarios

## 🔄 Sesiones de Chat

### Sin Persistencia en localStorage
- **Cada recarga (F5)** = Conversación nueva
- Dentro de la sesión = Continúa el mismo thread
- No requiere limpiar localStorage manualmente
- Ideal para prototipos y demos

### Extracción de Mensajes Mejorada
- Filtra últimos 10 mensajes (evita acumulación)
- Selecciona el mensaje más reciente del asistente
- Maneja correctamente threads con estado acumulado

## 🧪 Flujo Completo de Usuario

```
1. Usuario: "Tengo un problema"
   ↓
2. Sistema: Diagnóstico automático (RAG + LLM)
   ↓
3. Usuario: "Ok" / "Sí"
   ↓
4. Sistema: Solicita datos
   Usuario: "Mañana 10:00, Juan García, 300555"
   ↓
5. Sistema: Pide mecánico
   Usuario: "1" / "María" / "Cualquiera"
   ↓
6. Sistema: ✅ CITA AGENDADA
```

## 🚀 Próximos Pasos

1. Clona el repositorio
2. Configura el archivo `.env`
3. Instala dependencias
4. En Terminal 1: `langgraph dev`
5. En Terminal 2: `uv run python server.py`
6. Abre: **http://127.0.0.1:8080**
7. Prueba el chat completo

**Para acceso público:**
```bash
ngrok http 8080
```

¡Listo! Ya puedes probar el agente 🎉

---

**Última actualización:** 11 de Mayo 2026  
**Versión:** 1.1.0 (con Web UI, Mechanic Selection, Validations)  
**Autor:** Julian David Ortega Solarte
