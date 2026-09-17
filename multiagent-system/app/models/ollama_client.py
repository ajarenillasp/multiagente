"""
Cliente para Ollama - Modelos locales en Jetson Thor
"""
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class OllamaClient:
    """Cliente asíncrono para interactuar con Ollama API"""
    
    def __init__(self, base_url: str = "http://ollama:11434", timeout: int = 300):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generar respuesta usando un modelo específico
        
        Args:
            model: Nombre del modelo (ej: 'llama3:70b', 'codellama:34b')
            prompt: Prompt del usuario
            system: Prompt de sistema opcional
            stream: Si True, devuelve streaming (no implementado aún)
            options: Opciones adicionales para el modelo
            
        Returns:
            Respuesta generada por el modelo
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
            
        if options:
            payload["options"] = options
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            if stream:
                return response.text
            else:
                result = response.json()
                return result.get("response", "")
                
        except httpx.HTTPError as e:
            raise Exception(f"Error calling Ollama: {str(e)}")
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Conversación tipo chat con historial
        
        Args:
            model: Nombre del modelo
            messages: Lista de mensajes [{role: 'user'|'assistant', content: '...'}]
            stream: Si True, devuelve streaming
            options: Opciones adicionales
            
        Returns:
            Respuesta del modelo
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if options:
            payload["options"] = options
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except httpx.HTTPError as e:
            raise Exception(f"Error calling Ollama chat: {str(e)}")
    
    async def list_models(self) -> List[str]:
        """Lista todos los modelos disponibles"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            result = response.json()
            return [model["name"] for model in result.get("models", [])]
        except httpx.HTTPError as e:
            raise Exception(f"Error listing models: {str(e)}")
    
    async def is_model_available(self, model: str) -> bool:
        """Verifica si un modelo está disponible"""
        models = await self.list_models()
        return model in models
    
    async def pull_model(self, model: str):
        """Descarga un modelo (operación larga)"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                timeout=None  # Sin timeout para descargas largas
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Error pulling model: {str(e)}")
    
    async def close(self):
        """Cerrar el cliente HTTP"""
        await self.client.aclose()


# Modelos recomendados por tipo de tarea
RECOMMENDED_MODELS = {
    "analysis": "llama3:70b",      # Análisis complejo
    "coding": "codellama:34b",     # Generación de código
    "simple": "mistral:7b",        # Tareas simples
    "vision": "llava:13b",         # Análisis de imágenes
    "verification": "llama3:70b",  # Verificación exhaustiva
    "editing": "mistral:7b",       # Edición y formateo
}


async def get_recommended_model(task_type: str) -> str:
    """Obtiene el modelo recomendado para un tipo de tarea"""
    return RECOMMENDED_MODELS.get(task_type, "mistral:7b")
