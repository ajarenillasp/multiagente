"""
Agente Arquitecto - Analiza proyectos y diseña equipos de agentes especializados
"""
from typing import List, Dict, Any, Optional
import json
from ..models.ollama_client import OllamaClient, RECOMMENDED_MODELS


class ArchitectAgent:
    """
    Agente responsable de:
    1. Analizar el proyecto/objetivo principal
    2. Identificar tareas necesarias
    3. Diseñar equipo de agentes especializados
    4. Definir roles, herramientas y modelos para cada agente
    """
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.model = RECOMMENDED_MODELS["analysis"]  # llama3:70b para análisis complejo
        
        self.system_prompt = """Eres un Arquitecto de Sistemas Multi-Agente experto en generar propuestas europeas y código de alta calidad.

TU RESPONSABILIDAD:
1. Analizar exhaustivamente el objetivo del proyecto
2. Identificar TODAS las tareas necesarias para completarlo con excelencia
3. Diseñar un equipo de agentes especializados óptimo
4. Para cada agente, definir:
   - Rol específico y especializado
   - Herramientas que necesita
   - Modelo de IA más adecuado (de los disponibles)
   - Tareas concretas que realizará
   - Criterios de calidad exigentes

REQUISITOS DE CALIDAD:
- Descomponer el proyecto en tareas atómicas y manejables
- Cada agente debe tener UN rol muy específico (no generalista)
- Priorizar calidad sobre velocidad
- Considerar verificación exhaustiva en múltiples iteraciones
- Incluir agente verificador y editor final

FORMATO DE SALIDA (JSON estricto):
{
    "project_analysis": "Análisis detallado del proyecto...",
    "complexity_score": 1-10,
    "estimated_tasks": número,
    "agents": [
        {
            "id": "agent_1",
            "name": "Nombre descriptivo",
            "role": "Rol específico",
            "description": "Descripción detallada de responsabilidades",
            "model": "modelo_recomendado",
            "tools": ["herramienta1", "herramienta2"],
            "tasks": ["tarea1", "tarea2"],
            "dependencies": [],
            "quality_criteria": ["criterio1", "criterio2"]
        }
    ],
    "workflow": ["agent_1 -> agent_2", "agent_3 -> agent_4"],
    "verification_strategy": "Descripción de estrategia de verificación"
}

IMPORTANTE: Responde SOLO con JSON válido, sin texto adicional."""

    async def analyze_project(
        self,
        objective: str,
        documents_context: Optional[str] = None,
        project_type: str = "proposal"  # "proposal" o "code"
    ) -> Dict[str, Any]:
        """
        Analiza el proyecto y genera el diseño del equipo de agentes
        
        Args:
            objective: Descripción del objetivo principal
            documents_context: Contexto extraído de documentos subidos
            project_type: Tipo de proyecto ("proposal" o "code")
            
        Returns:
            Diccionario con el análisis y diseño de agentes
        """
        # Construir prompt completo
        prompt = self._build_prompt(objective, documents_context, project_type)
        
        try:
            # Llamar al modelo
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                system=self.system_prompt,
                options={
                    "temperature": 0.3,  # Bajo para respuestas más deterministas
                    "top_p": 0.9,
                }
            )
            
            # Parsear respuesta JSON
            return self._parse_response(response)
            
        except Exception as e:
            raise Exception(f"Architect agent failed: {str(e)}")
    
    def _build_prompt(
        self,
        objective: str,
        documents_context: Optional[str],
        project_type: str
    ) -> str:
        """Construye el prompt completo para el análisis"""
        
        prompt = f"""OBJETIVO DEL PROYECTO:
{objective}

TIPO DE PROYECTO: {project_type.upper()}
"""
        
        if documents_context:
            prompt += f"""
DOCUMENTOS DE REFERENCIA:
{documents_context}
"""
        
        if project_type == "proposal":
            prompt += """
CONTEXTO: Propuesta para convocatoria europea
REQUISITOS ESPECIALES:
- Excelencia científica extrema
- Impacto medible y significativo
- Implementación realista
- Consorcio internacional (si aplica)
- Presupuesto justificado
- Ética y género transversales
"""
        elif project_type == "code":
            prompt += """
CONTEXTO: Desarrollo de software/código
REQUISITOS ESPECIALES:
- Código limpio y mantenible
- Testing exhaustivo
- Documentación completa
- Mejores prácticas y patrones
- Sin errores de sintaxis
- Optimizado y eficiente
"""
        
        prompt += """
GENERA AHORA EL DISEÑO COMPLETO DEL EQUIPO DE AGENTES.
Recuerda: Calidad EXTREMA es la prioridad máxima."""
        
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parsea la respuesta JSON del modelo"""
        try:
            # Intentar extraer JSON si hay texto adicional
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validar estructura básica
                if "agents" not in result:
                    result["agents"] = []
                if "project_analysis" not in result:
                    result["project_analysis"] = "Analysis completed."
                    
                return result
            else:
                # Si no hay JSON, crear estructura básica
                return {
                    "project_analysis": response,
                    "complexity_score": 5,
                    "estimated_tasks": 3,
                    "agents": [],
                    "workflow": [],
                    "verification_strategy": "Standard verification"
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response[:500]}...")
            return {
                "project_analysis": "Analysis completed with parsing issues.",
                "complexity_score": 5,
                "estimated_tasks": 3,
                "agents": [],
                "workflow": [],
                "verification_strategy": "Standard verification",
                "raw_response": response
            }
    
    async def refine_agent_config(
        self,
        agent_config: Dict[str, Any],
        user_feedback: str
    ) -> Dict[str, Any]:
        """
        Refina la configuración de un agente basado en feedback del usuario
        
        Args:
            agent_config: Configuración actual del agente
            user_feedback: Feedback del usuario para mejorar
            
        Returns:
            Configuración refinada
        """
        prompt = f"""Configuración actual del agente:
{json.dumps(agent_config, indent=2)}

Feedback del usuario para mejorar:
{user_feedback}

Mejora la configuración manteniendo el formato JSON original.
Responde SOLO con el JSON mejorado."""
        
        response = await self.client.generate(
            model=self.model,
            prompt=prompt,
            system="Eres un experto optimizando configuraciones de agentes IA.",
            options={"temperature": 0.3}
        )
        
        return self._parse_response(response)
