"""
Agente Especialista - Ejecuta tareas específicas asignadas por el arquitecto
"""
from typing import List, Dict, Any, Optional
import json
from ..models.ollama_client import OllamaClient


class SpecialistAgent:
    """
    Agente especializado que ejecuta una tarea concreta
    
    Cada instancia representa un agente con rol específico definido por el arquitecto
    """
    
    def __init__(
        self,
        ollama_client: OllamaClient,
        agent_id: str,
        role: str,
        model: str,
        tasks: List[str],
        tools: Optional[List[str]] = None,
        quality_criteria: Optional[List[str]] = None
    ):
        self.client = ollama_client
        self.agent_id = agent_id
        self.role = role
        self.model = model
        self.tasks = tasks
        self.tools = tools or []
        self.quality_criteria = quality_criteria or []
        
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Construye el prompt de sistema basado en el rol del agente"""
        
        base_prompt = f"""Eres un agente especializado con el siguiente rol: {self.role}

TU RESPONSABILIDAD PRINCIPAL:
{chr(10).join(f'- {task}' for task in self.tasks)}
"""
        
        if self.quality_criteria:
            base_prompt += f"""
CRITERIOS DE CALIDAD EXIGENTES:
{chr(10).join(f'- {criterion}' for criterion in self.quality_criteria)}
"""
        
        if "code" in self.role.lower() or "programming" in self.role.lower():
            base_prompt += """
REQUISITOS PARA CÓDIGO:
- Código limpio, legible y mantenible
- Comentarios explicativos cuando sea necesario
- Manejo adecuado de errores
- Testing incluido si es relevante
- Sin errores de sintaxis
- Optimizado para rendimiento
- Sigue mejores prácticas y patrones de diseño
"""
        
        if "proposal" in self.role.lower() or "european" in self.role.lower():
            base_prompt += """
REQUISITOS PARA PROPUESTAS EUROPEAS:
- Excelencia científica demostrable
- Impacto claro y medible
- Metodología robusta
- Implementación realista
- Consideraciones éticas incluidas
- Perspectiva de género integrada
- Lenguaje claro y persuasivo
- Evidencias y referencias actualizadas
"""
        
        if "research" in self.role.lower() or "search" in self.role.lower():
            base_prompt += """
REQUISITOS PARA BÚSQUEDA DE INFORMACIÓN:
- Fuentes verificables y confiables
- Información actualizada (últimos 5 años preferiblemente)
- Múltiples fuentes para validar datos
- NO inventar información
- Citar fuentes cuando sea posible
- Distinguir hechos de opiniones
- Identificar lagunas en la información
"""
        
        base_prompt += """
IMPORTANTE:
- Trabaja con CALIDAD EXTREMA
- No tengas prisa, prioriza precisión
- Si algo no está claro, explícitalo
- Proporciona resultados completos y detallados
"""
        
        return base_prompt
    
    async def execute(
        self,
        context: str,
        input_data: Optional[str] = None,
        documents_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta la tarea asignada
        
        Args:
            context: Contexto general del proyecto
            input_data: Datos específicos para esta tarea
            documents_context: Contexto de documentos subidos
            
        Returns:
            Diccionario con resultado y metadata
        """
        prompt = self._build_execution_prompt(context, input_data, documents_context)
        
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                system=self.system_prompt,
                options={
                    "temperature": 0.4,  # Balance entre creatividad y precisión
                    "top_p": 0.9,
                }
            )
            
            return {
                "agent_id": self.agent_id,
                "role": self.role,
                "model_used": self.model,
                "result": response,
                "status": "completed",
                "tasks_completed": self.tasks
            }
            
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "role": self.role,
                "model_used": self.model,
                "result": f"Error: {str(e)}",
                "status": "failed",
                "tasks_completed": []
            }
    
    def _build_execution_prompt(
        self,
        context: str,
        input_data: Optional[str],
        documents_context: Optional[str]
    ) -> str:
        """Construye el prompt para ejecutar la tarea"""
        
        prompt = f"""CONTEXTO DEL PROYECTO:
{context}

"""
        
        if documents_context:
            prompt += f"""DOCUMENTOS DE REFERENCIA:
{documents_context}

"""
        
        if input_data:
            prompt += f"""INFORMACIÓN ESPECÍFICA PARA ESTA TAREA:
{input_data}

"""
        
        prompt += f"""TU ROL: {self.role}

TUS TAREAS CONCRETAS:
{chr(10).join(f'{i+1}. {task}' for i, task in enumerate(self.tasks))}

EJECUTA AHORA TUS TAREAS CON LA MÁXIMA CALIDAD.
Proporciona un resultado completo, detallado y listo para ser usado por el siguiente agente."""
        
        return prompt
    
    async def refine(
        self,
        previous_result: str,
        feedback: str
    ) -> Dict[str, Any]:
        """
        Refina el resultado basado en feedback
        
        Args:
            previous_result: Resultado anterior
            feedback: Feedback para mejorar
            
        Returns:
            Resultado refinado
        """
        prompt = f"""Resultado anterior:
{previous_result}

FEEDBACK PARA MEJORAR:
{feedback}

Mejora el resultado anterior incorporando el feedback.
Mantén los mismos estándares de calidad extrema.
Proporciona el resultado completo mejorado."""
        
        response = await self.client.generate(
            model=self.model,
            prompt=prompt,
            system=self.system_prompt,
            options={"temperature": 0.3}
        )
        
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "model_used": self.model,
            "result": response,
            "status": "refined",
            "feedback_applied": feedback
        }
