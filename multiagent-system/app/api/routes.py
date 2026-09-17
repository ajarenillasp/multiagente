"""
API Routes para el sistema multi-agente
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import asyncio
import os
from datetime import datetime

from ..models.ollama_client import OllamaClient, RECOMMENDED_MODELS
from ..documents.parser import DocumentParser, parse_uploaded_file
from ..agents.architect import ArchitectAgent
from ..agents.specialist import SpecialistAgent
from ..agents.verifier import VerifierAgent
from ..agents.editor import EditorAgent


router = APIRouter()

# Estado global de las ejecuciones (en producción usar Redis o similar)
active_projects: Dict[str, Dict[str, Any]] = {}


@router.get("/health")
async def health_check():
    """Verifica que el servicio esté funcionando"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.get("/models")
async def list_models():
    """Lista los modelos disponibles en Ollama"""
    client = OllamaClient()
    try:
        models = await client.list_models()
        return {
            "available_models": models,
            "recommended": RECOMMENDED_MODELS
        }
    except Exception as e:
        # Devolver recomendados aunque no se pueda conectar
        return {
            "available_models": [],
            "recommended": RECOMMENDED_MODELS,
            "note": "Ollama no disponible, usando recomendados por defecto"
        }


@router.post("/analyze")
async def analyze_project(
    objective: str = Form(...),
    project_type: str = Form("proposal"),
    uploaded_files: List[UploadFile] = File(None)
):
    """
    Analiza un proyecto y genera el diseño de agentes
    
    Args:
        objective: Descripción del objetivo principal
        project_type: "proposal" o "code"
        uploaded_files: Archivos opcionales con requisitos
        
    Returns:
        Diseño del equipo de agentes
    """
    # Parsear documentos subidos si existen
    documents_context = ""
    
    if uploaded_files:
        parser = DocumentParser()
        for file in uploaded_files:
            try:
                content = await file.read()
                parsed = await parse_uploaded_file(content, file.filename)
                documents_context += f"\n\n--- DOCUMENTO: {file.filename} ---\n"
                documents_context += parsed["content"][:2000]  # Limitar longitud
            except Exception as e:
                print(f"Error parsing {file.filename}: {e}")
    
    # Crear cliente y arquitecto
    client = OllamaClient()
    architect = ArchitectAgent(client)
    
    try:
        # Analizar proyecto
        result = await architect.analyze_project(
            objective=objective,
            documents_context=documents_context if documents_context else None,
            project_type=project_type
        )
        
        # Añadir modelos recomendados a cada agente
        for agent in result.get("agents", []):
            if "model" not in agent or not agent["model"]:
                task_type = "analysis" if "analysis" in agent.get("role", "").lower() else "simple"
                agent["model"] = RECOMMENDED_MODELS.get(task_type, "mistral:7b")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        await client.close()


@router.post("/execute/{project_id}")
async def execute_project(
    project_id: str,
    agent_configs: Dict[str, Any],
    context: str
):
    """
    Ejecuta el proyecto con los agentes configurados
    
    Args:
        project_id: ID único del proyecto
        agent_configs: Configuración de cada agente
        context: Contexto completo del proyecto
        
    Returns:
        Estado de la ejecución
    """
    # Guardar estado inicial
    active_projects[project_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "agent_configs": agent_configs,
        "context": context,
        "results": {},
        "current_phase": "specialists"
    }
    
    # Ejecutar en background
    asyncio.create_task(run_project_pipeline(project_id))
    
    return {
        "project_id": project_id,
        "status": "started",
        "message": "Project execution started in background"
    }


async def run_project_pipeline(project_id: str):
    """Ejecuta el pipeline completo del proyecto"""
    
    project = active_projects[project_id]
    client = OllamaClient()
    
    try:
        # Fase 1: Ejecutar agentes especializados en paralelo
        project["current_phase"] = "specialists"
        specialists_results = await run_specialists_parallel(
            client,
            project["agent_configs"],
            project["context"]
        )
        project["results"]["specialists"] = specialists_results
        
        # Fase 2: Recopilar resultados
        project["current_phase"] = "compilation"
        compiled_content = compile_results(specialists_results)
        project["results"]["compiled"] = compiled_content
        
        # Fase 3: Verificación (5 iteraciones)
        project["current_phase"] = "verification"
        verifier = VerifierAgent(client)
        verification_result = await verifier.verify_full_cycle(
            compiled_content,
            project["context"],
            progress_callback=lambda iter, total: update_progress(project_id, iter, total)
        )
        project["results"]["verified"] = verification_result["final_content"]
        project["results"]["verification_details"] = verification_result
        
        # Fase 4: Edición final
        project["current_phase"] = "editing"
        output_type = "code" if "code" in project["context"].lower() else "document"
        editor = EditorAgent(client, output_type=output_type)
        edit_result = await editor.edit(
            verification_result["final_content"],
            project["context"]
        )
        project["results"]["final"] = edit_result["content"]
        
        # Completado
        project["status"] = "completed"
        project["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        project["status"] = "failed"
        project["error"] = str(e)
    
    finally:
        await client.close()


async def run_specialists_parallel(
    client: OllamaClient,
    agent_configs: Dict,
    context: str
) -> List[Dict]:
    """Ejecuta todos los agentes especializados en paralelo"""
    
    agents = []
    tasks = []
    
    # Crear agentes
    for agent_config in agent_configs.get("agents", []):
        specialist = SpecialistAgent(
            ollama_client=client,
            agent_id=agent_config.get("id", "unknown"),
            role=agent_config.get("role", "Specialist"),
            model=agent_config.get("model", "mistral:7b"),
            tasks=agent_config.get("tasks", []),
            tools=agent_config.get("tools", []),
            quality_criteria=agent_config.get("quality_criteria", [])
        )
        agents.append(specialist)
    
    # Ejecutar en paralelo
    for agent in agents:
        task = agent.execute(context=context)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Procesar resultados
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "agent_id": agents[i].agent_id,
                "status": "error",
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    return processed_results


def compile_results(specialists_results: List[Dict]) -> str:
    """Recopila los resultados de los agentes especializados"""
    
    compiled_parts = []
    
    for result in specialists_results:
        if result.get("status") == "completed":
            compiled_parts.append(f"""
## {result.get('role', 'Unknown Role')}

{result.get('result', '')}
""")
    
    return "\n\n---\n\n".join(compiled_parts)


def update_progress(project_id: str, iteration: int, total: int):
    """Actualiza el progreso de verificación"""
    if project_id in active_projects:
        active_projects[project_id]["verification_progress"] = {
            "iteration": iteration,
            "total": total,
            "percentage": (iteration / total) * 100
        }


@router.get("/status/{project_id}")
async def get_project_status(project_id: str):
    """Obtiene el estado de un proyecto"""
    if project_id not in active_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return active_projects[project_id]


@router.get("/result/{project_id}")
async def get_project_result(project_id: str):
    """Obtiene el resultado final de un proyecto completado"""
    if project_id not in active_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = active_projects[project_id]
    
    if project["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Project not completed yet. Status: {project['status']}"
        )
    
    return {
        "project_id": project_id,
        "content": project["results"].get("final", ""),
        "metadata": {
            "started_at": project["started_at"],
            "completed_at": project["completed_at"],
            "verification_iterations": project["results"].get("verification_details", {}).get("iterations_completed", 0),
            "issues_found": project["results"].get("verification_details", {}).get("total_issues_found", 0)
        }
    }


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Sube documentos para procesamiento"""
    results = []
    
    for file in files:
        try:
            content = await file.read()
            parsed = await parse_uploaded_file(content, file.filename)
            results.append({
                "filename": file.filename,
                "status": "success",
                "type": parsed["type"],
                "size": parsed["size"],
                "content_preview": parsed["content"][:200] + "..." if len(parsed["content"]) > 200 else parsed["content"]
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {"uploaded": results}
