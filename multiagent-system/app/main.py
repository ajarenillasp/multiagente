"""
Main FastAPI Application - Sistema Multi-Agente para Jetson Thor
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Starting Multi-Agent System for Jetson Thor...")
    print(f"📁 Input directory: {os.getenv('INPUT_DIR', '/app/input_docs')}")
    print(f"📁 Output directory: {os.getenv('OUTPUT_DIR', '/app/output_docs')}")
    print(f"🤖 Ollama host: {os.getenv('OLLAMA_HOST', 'http://ollama:11434')}")
    
    # Asegurar que los directorios existen
    os.makedirs(os.getenv('INPUT_DIR', '/app/input_docs'), exist_ok=True)
    os.makedirs(os.getenv('OUTPUT_DIR', '/app/output_docs'), exist_ok=True)
    
    yield
    
    # Shutdown
    print("👋 Shutting down Multi-Agent System...")


app = FastAPI(
    title="Multi-Agent System for Jetson Thor",
    description="""
    Sistema avanzado de generación de propuestas europeas y código mediante agentes especializados.
    
    ## Características principales:
    
    * **Análisis inteligente**: Agente arquitecto diseña equipos de agentes personalizados
    * **Ejecución asíncrona**: Múltiples agentes trabajando en paralelo
    * **Verificación exhaustiva**: 5 iteraciones de verificación de calidad
    * **100% local**: Todo se ejecuta en tu Jetson Thor con Ollama
    * **Acceso remoto**: Interfaz web accesible vía Cloudflare Tunnel
    
    ## Flujo de trabajo:
    
    1. Subir documentos de requisitos (PDF, DOCX, MD, imágenes)
    2. Describir el objetivo del proyecto
    3. Revisar y configurar el equipo de agentes propuesto
    4. Ejecutar el pipeline de generación
    5. Obtener resultado de calidad extrema
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios concretos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router, prefix="/api/v1", tags=["multi-agent-system"])


@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "message": "Multi-Agent System for Jetson Thor",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health():
    """Endpoint de salud (sin prefijo)"""
    return {"status": "healthy"}
