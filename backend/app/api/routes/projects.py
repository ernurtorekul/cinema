from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from uuid import uuid4
import logging
import os
from app.models.schemas import (
    ProjectCreate,
    ProjectResponse,
    ScenarioCreate,
    ScenarioResponse,
    GenerationResults
)
from app.services.supabase_service import get_supabase, is_using_mock, MockClient
from app.services.mock_storage import mock_projects, mock_scenarios
from app.agents.orchestrator import orchestrator
from app.services.characters_service import characters_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter(tags=["projects"])


def is_mock_client(supabase) -> bool:
    """Check if the client is a mock"""
    return isinstance(supabase, MockClient) or MOCK_MODE


@router.post("")
async def create_project(project: ProjectCreate, supabase=Depends(get_supabase)):
    """Create a new project"""
    style_prefs = project.style_preferences or {}
    data = {
        "type": project.type,
        "total_duration": project.total_duration,
        "style_preferences": {
            **style_prefs,
            "scene_count": project.scene_count_target,
            "pacing": project.pacing
        }
    }

    if is_mock_client(supabase):
        # Mock mode - return fake data
        project_id = str(uuid4())
        mock_projects[project_id] = {
            "id": project_id,
            **data,
            "created_at": "2024-01-01T00:00:00Z"
        }
        logger.info(f"Created mock project: {project_id}")
        return JSONResponse(content=mock_projects[project_id], status_code=201)

    logger.info(f"Creating project: {data}")

    try:
        response = supabase.table("projects").insert(data).execute()
        logger.info(f"Project created: {response.data[0]}")
        return JSONResponse(content=response.data[0], status_code=201)
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project: {str(e)}. Check Supabase configuration or set MOCK_MODE=true in .env"
        )

    logger.info(f"Creating project: {data}")

    try:
        response = supabase.table("projects").insert(data).execute()
        logger.info(f"Project created: {response.data[0]}")
        return JSONResponse(content=response.data[0], status_code=201)
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project: {str(e)}. Check Supabase configuration or set MOCK_MODE=true in .env"
        )


@router.get("/{project_id}")
async def get_project(project_id: str, supabase=Depends(get_supabase)):
    """Get project details"""
    if is_mock_client(supabase):
        if project_id not in mock_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        return JSONResponse(content=mock_projects[project_id])

    try:
        response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return JSONResponse(content=response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/scenario")
async def submit_scenario(
    project_id: str,
    scenario: ScenarioCreate,
    supabase=Depends(get_supabase)
):
    """Submit scenario for a project"""
    if is_mock_client(supabase):
        if project_id not in mock_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        scenario_id = str(uuid4())
        scenario_data = {
            "id": scenario_id,
            "project_id": project_id,
            "text": scenario.text,
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_scenarios[scenario_id] = scenario_data
        # Also link scenario to project for easy retrieval
        mock_projects[project_id]["scenario_id"] = scenario_id
        logger.info(f"Saved mock scenario: {scenario_id}")
        return JSONResponse(content=scenario_data)

    try:
        # Verify project exists
        project_response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).execute()

        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        data = {
            "project_id": project_id,
            "text": scenario.text
        }
        response = supabase.table("scenarios").insert(data).execute()
        return JSONResponse(content=response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving scenario: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save scenario: {str(e)}")


@router.post("/{project_id}/generate")
async def trigger_generation(
    project_id: str,
    character_config: Optional[dict] = None,
    source_rules: Optional[str] = None,
    style_guide: Optional[dict] = None,
    include_sound_design: bool = True,
    supabase=Depends(get_supabase)
):
    """Trigger the full generation pipeline"""
    try:
        # Get scenario text from mock storage if needed
        scenario_text = None
        if is_mock_client(supabase):
            # Find the scenario in mock storage
            for scenario_id, scenario_data in mock_scenarios.items():
                if scenario_data.get("project_id") == project_id:
                    scenario_text = scenario_data.get("text")
                    break
            if not scenario_text:
                # Also check if scenario_id is stored in project
                scenario_id = mock_projects.get(project_id, {}).get("scenario_id")
                if scenario_id and scenario_id in mock_scenarios:
                    scenario_text = mock_scenarios[scenario_id].get("text")

            if not scenario_text:
                raise HTTPException(
                    status_code=400,
                    detail="No scenario found for this project. Please submit a scenario first."
                )
            logger.info(f"Found scenario for mock project {project_id}: {scenario_text[:50]}...")
        else:
            scenario_response = supabase.table("scenarios").select("*").eq(
                "project_id", project_id
            ).execute()

            if not scenario_response.data:
                raise HTTPException(
                    status_code=400,
                    detail="No scenario found for this project"
                )
            scenario_text = scenario_response.data[0]["text"]

        # Run pipeline with orchestrator (calls Gemini)
        logger.info(f"Starting generation pipeline for project {project_id}...")
        result = await orchestrator.run_full_pipeline(
            project_id=project_id,
            scenario=scenario_text,
            characters=character_config,
            source_rules=source_rules,
            style_guide=style_guide,
            include_sound_design=include_sound_design
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/status")
async def get_generation_status(project_id: str, supabase=Depends(get_supabase)):
    """Check generation status"""
    if is_mock_client(supabase):
        if project_id not in mock_projects:
            return JSONResponse(
                content={"project_id": project_id, "status": "not_found"},
                status_code=404
            )
        return JSONResponse(content={
            "project_id": project_id,
            "status": "pending"
        })

    try:
        project_response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).execute()

        if not project_response.data:
            return JSONResponse(
                content={"project_id": project_id, "status": "not_found"},
                status_code=404
            )

        project = project_response.data[0]
        style_prefs = project.get("style_preferences") or {}
        status = style_prefs.get("generation_status", "pending")

        return JSONResponse(content={
            "project_id": project_id,
            "status": status
        })
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@router.get("/{project_id}/results")
async def get_results(project_id: str, supabase=Depends(get_supabase)):
    """Get all generation results"""
    if is_mock_client(supabase):
        return {
            "project_id": project_id,
            "scenes": [],
            "prompts": [],
            "audio_design": []
        }

    # Get all scenes for project
    scenes_response = supabase.table("scenes").select("*").eq(
        "project_id", project_id
    ).order("scene_number").execute()

    if not scenes_response.data:
        return {
            "project_id": project_id,
            "scenes": [],
            "prompts": [],
            "audio_design": []
        }

    scene_ids = [s["id"] for s in scenes_response.data]

    # Get prompts
    prompts_response = supabase.table("generated_prompts").select("*").in_(
        "scene_id", scene_ids
    ).execute() if scene_ids else {"data": []}

    # Get audio design
    audio_response = supabase.table("audio_design").select(
        "*",
        "sound_effects(*)",
        "audio_cues(*)"
    ).in_("scene_id", scene_ids).execute() if scene_ids else {"data": []}

    return {
        "project_id": project_id,
        "scenes": scenes_response.data,
        "prompts": prompts_response.data,
        "audio_design": audio_response.data
    }


@router.post("/{project_id}/step/{step}")
async def run_generation_step(
    project_id: str,
    step: str,
    data: Optional[dict] = None
):
    """Run a single generation step"""
    try:
        data = data or {}
        result = await orchestrator.run_step(
            step=step,
            project_id=project_id,
            **data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in step {step}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/characters/pool")
async def get_characters_pool():
    """Get the character pool from characters.txt"""
    try:
        characters = characters_service.load_characters_from_file()
        return JSONResponse(content={
            "pool_name": "Characters from characters.txt",
            "description": "AI will choose from these characters based on scene requirements",
            "characters": characters
        })
    except Exception as e:
        logger.error(f"Error loading characters: {str(e)}", exc_info=True)
        # Return default pool on error
        default_pool = characters_service.get_default_celebrity_pool()
        return JSONResponse(content={
            "pool_name": "Default Celebrity Pool",
            "description": "Default celebrity pool (characters.txt not available)",
            "characters": default_pool
        })

