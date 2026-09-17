"""
Agente Verificador - Verificación exhaustiva en 5 iteraciones
Detecta información inventada, mejora calidad, incorpora información relevante
"""
from typing import List, Dict, Any, Optional
import json
from ..models.ollama_client import OllamaClient, RECOMMENDED_MODELS


class VerifierAgent:
    """
    Agente responsable de verificación exhaustiva
    
    Proceso de 5 iteraciones:
    1. Detectar información inventada o no verificada
    2. Buscar información relevante que falte
    3. Incorporar información encontrada
    4. Mejorar coherencia y consistencia
    5. Validación final de calidad
    """
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.model = RECOMMENDED_MODELS["verification"]  # llama3:70b para verificación
        self.max_iterations = 5
        
        self.system_prompt = """Eres un Verificador Experto extremadamente crítico y exigente.

TU RESPONSABILIDAD PRINCIPAL:
Verificar CADA afirmación, dato, referencia y conclusión del documento.

CRITERIOS DE VERIFICACIÓN EXTREMADAMENTE EXIGENTES:

1. DETECCIÓN DE INFORMACIÓN INVENTADA:
   - Identifica cualquier dato sin fuente clara
   - Marca estadísticas sospechosas o sin referencia
   - Detecta referencias bibliográficas inexistentes
   - Señala afirmaciones demasiado convenientes

2. BÚSQUEDA DE INFORMACIÓN RELEVANTE:
   - Identifica lagunas en el contenido
   - Detecta áreas que necesitan más profundidad
   - Señala información desactualizada
   - Identifica perspectivas faltantes

3. CONSISTENCIA Y COHERENCIA:
   - Verifica que no haya contradicciones internas
   - Confirma que la metodología sea coherente con objetivos
   - Valida que las conclusiones sigan de los argumentos

4. CALIDAD CIENTÍFICA/TÉCNICA:
   - Evalúa rigor metodológico
   - Verifica uso apropiado de terminología
   - Confirma que las afirmaciones estén justificadas

5. VALIDACIÓN FINAL:
   - Revisión exhaustiva de todo el contenido
   - Confirmación de que todos los issues fueron resueltos
   - Veredicto final sobre calidad

IMPORTANTE:
- Sé EXTREMADAMENTE crítico
- No aceptes información sin verificar
- Prioriza precisión sobre completitud
- Si algo es dudoso, MÁRCALO CLARAMENTE
- Proporciona sugerencias concretas de mejora

FORMATO DE SALIDA (JSON):
{
    "iteration": número,
    "issues_found": [
        {
            "type": "invented|missing|inconsistent|outdated",
            "location": "sección/párrafo",
            "description": "descripción del problema",
            "severity": "critical|major|minor",
            "suggestion": "cómo corregir"
        }
    ],
    "information_to_add": ["información relevante encontrada"],
    "improvements_made": ["mejoras aplicadas"],
    "quality_score": 1-10,
    "ready_for_next": true/false,
    "final_verdict": "veredicto si es última iteración"
}"""

    async def verify(
        self,
        content: str,
        context: str,
        iteration: int = 1,
        previous_issues: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Realiza una iteración de verificación
        
        Args:
            content: Contenido a verificar
            context: Contexto del proyecto
            iteration: Número de iteración (1-5)
            previous_issues: Issues de iteraciones anteriores
            
        Returns:
            Resultados de verificación
        """
        prompt = self._build_verification_prompt(
            content, context, iteration, previous_issues
        )
        
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                system=self.system_prompt,
                options={
                    "temperature": 0.2,  # Muy bajo para análisis crítico
                    "top_p": 0.8,
                }
            )
            
            return self._parse_response(response, iteration)
            
        except Exception as e:
            return {
                "iteration": iteration,
                "issues_found": [],
                "error": str(e),
                "quality_score": 0,
                "ready_for_next": False
            }
    
    def _build_verification_prompt(
        self,
        content: str,
        context: str,
        iteration: int,
        previous_issues: Optional[List[Dict]]
    ) -> str:
        """Construye el prompt para verificación"""
        
        prompt = f"""CONTEXTO DEL PROYECTO:
{context}

CONTENIDO A VERIFICAR:
{content}

ITERACIÓN ACTUAL: {iteration} de {self.max_iterations}
"""
        
        if previous_issues and len(previous_issues) > 0:
            prompt += f"""
ISSUES DE ITERACIONES ANTERIORES:
{json.dumps(previous_issues, indent=2)}

Verifica que todos estos issues hayan sido resueltos.
Si alguno persiste, MÁRCALO como crítico.
"""
        
        if iteration == 1:
            prompt += """
ENFOQUE DE ESTA ITERACIÓN (1/5):
- Detección exhaustiva de información inventada
- Identificación de lagunas principales
- Marcado de afirmaciones sin verificar
"""
        elif iteration == 2:
            prompt += """
ENFOQUE DE ESTA ITERACIÓN (2/5):
- Búsqueda de información relevante faltante
- Identificación de referencias necesarias
- Detección de información desactualizada
"""
        elif iteration == 3:
            prompt += """
ENFOQUE DE ESTA ITERACIÓN (3/5):
- Verificación de consistencia interna
- Coherencia entre secciones
- Validación de metodología
"""
        elif iteration == 4:
            prompt += """
ENFOQUE DE ESTA ITERACIÓN (4/5):
- Calidad científica/técnica
- Rigor en argumentación
- Terminología apropiada
"""
        else:  # iteration == 5
            prompt += """
ENFOQUE DE ESTA ITERACIÓN (5/5 - FINAL):
- Revisión exhaustiva completa
- Confirmación de calidad máxima
- Veredicto final
"""
        
        prompt += """
REALIZA AHORA LA VERIFICACIÓN CON EL MÁXIMO RIGOR.
Recuerda: La competencia es muy alta, solo lo MEJOR es aceptable."""
        
        return prompt
    
    def _parse_response(self, response: str, iteration: int) -> Dict[str, Any]:
        """Parsea la respuesta JSON"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                result["iteration"] = iteration
                return result
            else:
                return {
                    "iteration": iteration,
                    "issues_found": [],
                    "quality_score": 5,
                    "raw_response": response
                }
        except json.JSONDecodeError:
            return {
                "iteration": iteration,
                "issues_found": [],
                "quality_score": 5,
                "parse_error": True,
                "raw_response": response
            }
    
    async def verify_full_cycle(
        self,
        content: str,
        context: str,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Ejecuta las 5 iteraciones completas de verificación
        
        Args:
            content: Contenido inicial
            context: Contexto del proyecto
            progress_callback: Callback para reportar progreso
            
        Returns:
            Contenido verificado y mejorado después de 5 iteraciones
        """
        current_content = content
        all_issues = []
        iteration_results = []
        
        for iteration in range(1, self.max_iterations + 1):
            if progress_callback:
                await progress_callback(iteration, self.max_iterations)
            
            # Verificar
            result = await self.verify(
                current_content,
                context,
                iteration,
                all_issues[-3:] if len(all_issues) > 3 else all_issues  # Últimos 3 issues
            )
            
            iteration_results.append(result)
            
            if "issues_found" in result and result["issues_found"]:
                all_issues.extend(result["issues_found"])
            
            # Aquí se incorporaría la información encontrada
            # En implementación real, esto llamaría a un agente de búsqueda
            if "information_to_add" in result and result["information_to_add"]:
                current_content += f"\n\nINFORMACIÓN AÑADIDA (Iteración {iteration}):\n"
                current_content += "\n".join(result["information_to_add"])
            
            # Si es la última iteración, usar el veredicto final
            if iteration == self.max_iterations and "final_verdict" in result:
                break
        
        return {
            "final_content": current_content,
            "total_issues_found": len(all_issues),
            "iterations_completed": self.max_iterations,
            "iteration_results": iteration_results,
            "all_issues": all_issues
        }
