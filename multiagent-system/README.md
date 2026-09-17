# Sistema Multi-Agente para Jetson Thor

Sistema avanzado de generación de propuestas europeas y código mediante agentes especializados, optimizado para ejecutarse en Jetson Thor con acceso remoto vía Cloudflare Tunnel.

## 🎯 Características Principales

- **Arquitectura Headless**: Diseñado para ejecutarse sin interfaz gráfica local
- **Acceso Remoto Seguro**: Integración nativa con Cloudflare Tunnel
- **Procesamiento Multimodal**: Soporte para múltiples archivos PDF, DOCX, MD, imágenes (OCR)
- **Agentes Especializados**: Creación dinámica de equipos de agentes según la tarea
- **Verificación Exhaustiva**: 5 iteraciones de verificación para garantizar calidad máxima
- **100% Local**: Todo se ejecuta en tu Jetson Thor usando Ollama
- **Ejecución Asíncrona**: Agentes trabajando en paralelo para maximizar eficiencia

## 📁 Estructura del Proyecto

```
multiagent-system/
├── app/                    # Backend Python (FastAPI)
│   ├── agents/            # Implementación de agentes
│   │   ├── __init__.py
│   │   ├── architect.py   # Agente arquitecto (análisis y diseño)
│   │   ├── specialist.py  # Agentes especializados
│   │   ├── verifier.py    # Agente verificador (5 iteraciones)
│   │   └── editor.py      # Agente editor final
│   ├── models/
│   │   ├── __init__.py
│   │   └── ollama_client.py  # Cliente Ollama
│   ├── documents/
│   │   ├── __init__.py
│   │   └── parser.py      # Parser multimodal
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py      # Endpoints API
│   ├── main.py            # Punto de entrada FastAPI
│   └── requirements.txt   # Dependencias Python
├── frontend/              # Interfaz Web (Vue.js + TailwindCSS)
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── components/
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── vite.config.js
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── cloudflared/
│       └── config.yml
├── input_docs/            # Directorio para documentos de entrada (múltiples archivos)
├── output_docs/           # Directorio para resultados
├── docs/
│   └── INSTALL.md         # Instrucciones de instalación
├── docker-compose.yml     # Orquestación de servicios
└── .gitignore
```

## 🚀 Instalación Rápida

### Prerrequisitos

- Jetson Thor con JetPack instalado
- Docker y Docker Compose
- Cuenta de Cloudflare (gratuita)

### Pasos de Instalación

1. **Clonar el repositorio en tu Jetson Thor**:
```bash
git clone <tu-repositorio>
cd multiagent-system
```

2. **Configurar Cloudflare Tunnel**:
```bash
# Generar token de Cloudflare Tunnel
cloudflared tunnel login
cloudflared tunnel create thor-agent
```

3. **Editar configuración**:
```bash
# Editar docker/cloudflared/config.yml con tu tunnel ID
nano docker/cloudflared/config.yml
```

4. **Iniciar servicios**:
```bash
docker compose up -d
```

5. **Acceder a la interfaz**:
- La URL será proporcionada por Cloudflare (ej: `https://thor-agent.trycloudflare.com`)

## 📖 Documentación Completa

Consulta `docs/INSTALL.md` para instrucciones detalladas de instalación, configuración y uso.

## 🔄 Flujo de Trabajo

1. **Subir Documentos**: Arrastra múltiples archivos (PDF, DOCX, MD, imágenes) al área designada
2. **Describir Proyecto**: Escribe tu objetivo o requerimiento principal
3. **Análisis del Arquitecto**: El sistema analiza y propone un equipo de agentes
4. **Supervisión y Configuración**: Revisa y ajusta roles, modelos y herramientas de cada agente
5. **Ejecución Asíncrona**: Los agentes especializados trabajan en paralelo
6. **Verificación Iterativa**: 5 ciclos de verificación exhaustiva para eliminar alucinaciones
7. **Edición Final**: Formateo y verificación de sintaxis (para código)
8. **Descarga de Resultados**: Obten tu documento o código listo para usar

## 🧠 Modelos Recomendados

El sistema recomienda automáticamente el modelo óptimo para cada agente:

- **Llama3 70B**: Análisis complejo, arquitectura de proyectos
- **CodeLlama 34B**: Generación y revisión de código
- **Mistral 7B**: Tareas simples, resumen, formateo
- **LLaVA**: Análisis de imágenes y diagramas

Todos los modelos se ejecutan localmente vía Ollama.

## ⚙️ Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Ollama
OLLAMA_HOST=ollama:11434

# Cloudflare
TUNNEL_ID=tu-tunnel-id
TUNNEL_TOKEN=tu-tunnel-token

# Sistema
MAX_CONCURRENT_AGENTS=5
VERIFICATION_ITERATIONS=5
INPUT_DIR=/app/input_docs
OUTPUT_DIR=/app/output_docs
```

### Personalización de Agentes

Puedes modificar los prompts y comportamientos de los agentes en:
- `app/agents/architect.py`
- `app/agents/specialist.py`
- `app/agents/verifier.py`
- `app/agents/editor.py`

## 📊 Monitorización

La interfaz web proporciona:
- Progress tracking en tiempo real
- Visualización del workflow de agentes
- Logs detallados de cada iteración
- Métricas de rendimiento

## 🛡️ Seguridad

- Todo el procesamiento es local (sin envío de datos a externos)
- Acceso remoto seguro vía Cloudflare Tunnel
- Aislamiento completo mediante contenedores Docker

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, lee las guías de contribución antes de enviar PRs.

## 📞 Soporte

Para issues relacionados con la instalación en Jetson Thor, abre un issue en GitHub.
