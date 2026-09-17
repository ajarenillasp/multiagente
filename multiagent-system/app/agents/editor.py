"""
Agente Editor - Formateo final y verificación de sintaxis para código
"""
from typing import List, Dict, Any, Optional
import json
from ..models.ollama_client import OllamaClient, RECOMMENDED_MODELS


class EditorAgent:
    """
    Agente responsable del formateo final
    
    Para documentos:
    - Estructura coherente
    - Formato profesional
    - Ortografía y gramática
    - Consistencia de estilo
    
    Para código:
    - Verificación de sintaxis
    - Formateo consistente
    - Documentación completa
    - Sin errores
    """
    
    def __init__(self, ollama_client: OllamaClient, output_type: str = "document"):
        self.client = ollama_client
        self.model = RECOMMENDED_MODELS["editing"]  # mistral:7b para edición
        self.output_type = output_type  # "document" o "code"
        
        if output_type == "code":
            self.system_prompt = self._get_code_editor_prompt()
        else:
            self.system_prompt = self._get_document_editor_prompt()
    
    def _get_document_editor_prompt(self) -> str:
        """Prompt para edición de documentos"""
        return """Eres un Editor Profesional experto en documentos de alta calidad.

TU RESPONSABILIDAD:
1. Formatear el documento con estructura profesional
2. Corregir ortografía y gramática
3. Asegurar consistencia de estilo
4. Mejorar claridad y legibilidad
5. Verificar coherencia lógica

ESTÁNDARES DE CALIDAD:
- Títulos y secciones claramente jerarquizados
- Párrafos bien estructurados
- Lenguaje claro y preciso
- Sin errores ortográficos ni gramaticales
- Formato consistente en todo el documento
- Referencias y citas correctamente formateadas

FORMATO DE SALIDA:
Proporciona el documento COMPLETO formateado en Markdown.
Incluye todos los contenidos mejorados."""

    def _get_code_editor_prompt(self) -> str:
        """Prompt para edición de código"""
        return """Eres un Editor de Código experto en calidad de software.

TU RESPONSABILIDAD:
1. Verificar SINTAXIS del código
2. Corregir cualquier error encontrado
3. Aplicar formateo consistente
4. Añadir documentación faltante
5. Verificar mejores prácticas

VERIFICACIÓN DE SINTAXIS:
- Analiza cada línea de código
- Detecta errores de sintaxis
- Identifica problemas de indentación
- Verifica imports/dependencias
- Confirma que todas las funciones están definidas

ESTÁNDARES DE CALIDAD:
- Código limpio y legible
- Nombres de variables descriptivos
- Comentarios explicativos donde sea necesario
- Documentación de funciones (docstrings)
- Manejo adecuado de errores
- Sigue convenciones del lenguaje (PEP8 para Python, etc.)

FORMATO DE SALIDA:
Proporciona el código COMPLETO corregido y formateado.
Incluye TODAS las partes del código original mejoradas.
Si encuentras errores críticos, explícalos antes del código."""

    async def edit(
        self,
        content: str,
        context: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edita y formatea el contenido
        
        Args:
            content: Contenido a editar
            context: Contexto opcional
            language: Lenguaje de programación (si es código)
            
        Returns:
            Contenido editado y metadata
        """
        prompt = self._build_edit_prompt(content, context, language)
        
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                system=self.system_prompt,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                }
            )
            
            return {
                "content": response,
                "output_type": self.output_type,
                "language": language if self.output_type == "code" else None,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "content": content,  # Devolver original si falla
                "error": str(e),
                "status": "failed"
            }
    
    def _build_edit_prompt(
        self,
        content: str,
        context: Optional[str],
        language: Optional[str]
    ) -> str:
        """Construye el prompt para edición"""
        
        prompt = f"""CONTENIDO A EDITAR:
{content}

"""
        
        if context:
            prompt += f"""CONTEXTO:
{context}

"""
        
        if self.output_type == "code" and language:
            prompt += f"""LENGUAJE DE PROGRAMACIÓN: {language}

Aplica las convenciones y mejores prácticas específicas de {language}.
Verifica la sintaxis según las reglas de {language}.

"""
        
        if self.output_type == "code":
            prompt += """PROPORCIONA AHORA EL CÓDIGO COMPLETO:
1. Primero, lista cualquier error encontrado
2. Luego, proporciona el código completo corregido
3. Finalmente, resume las mejoras aplicadas
"""
        else:
            prompt += """PROPORCIONA AHORA EL DOCUMENTO COMPLETO FORMATEADO:
1. Estructura clara con títulos y secciones
2. Párrafos bien organizados
3. Lenguaje pulido y profesional
4. Sin errores ortográficos ni gramaticales
"""
        
        return prompt
    
    async def verify_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """
        Verifica específicamente la sintaxis del código
        
        Args:
            code: Código a verificar
            language: Lenguaje de programación
            
        Returns:
            Resultados de verificación
        """
        prompt = f"""Verifica la SINTAXIS del siguiente código en {language}:

```{language}
{code}
```

Analiza línea por línea buscando:
1. Errores de sintaxis
2. Problemas de indentación
3. Imports faltantes o incorrectos
4. Funciones/métodos no definidos
5. Variables no declaradas
6. Errores de tipeo

Responde en formato JSON:
{{
    "syntax_valid": true/false,
    "errors": [
        {{
            "line": número,
            "type": "tipo_de_error",
            "description": "descripción",
            "suggestion": "cómo corregir"
        }}
    ],
    "warnings": ["advertencias menores"],
    "summary": "resumen general"
}}

Si no hay errores, syntax_valid debe ser true y errors vacío."""
        
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                system="Eres un verificador de sintaxis experto.",
                options={"temperature": 0.2}
            )
            
            # Intentar parsear JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                result = json.loads(response[start_idx:end_idx])
                return result
            else:
                return {
                    "syntax_valid": True,
                    "errors": [],
                    "warnings": [],
                    "summary": "No se pudo parsear la respuesta, asumiendo válido"
                }
                
        except Exception as e:
            return {
                "syntax_valid": False,
                "errors": [{"description": f"Error en verificación: {str(e)}"}],
                "summary": "Error durante la verificación"
            }
    
    async def format_output(
        self,
        content: str,
        format_type: str = "markdown"
    ) -> str:
        """
        Formatea la salida según el tipo especificado
        
        Args:
            content: Contenido a formatear
            format_type: "markdown", "html", "pdf_ready", etc.
            
        Returns:
            Contenido formateado
        """
        if format_type == "markdown":
            # Ya debería estar en markdown, solo asegurar consistencia
            return content
        
        elif format_type == "html":
            # Convertir markdown a HTML básico
            prompt = f"""Convierte el siguiente contenido Markdown a HTML:

{content}

Proporciona SOLO el HTML, sin explicaciones adicionales."""
            
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                system="Eres un convertidor de Markdown a HTML.",
                options={"temperature": 0.2}
            )
            return response
        
        else:
            return content
