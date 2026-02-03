from typing import Dict, Any, List, Optional
from app.agents.scenario_agent import scenario_agent
from app.agents.character_agent import character_agent
from app.agents.source_agent import source_agent
from app.agents.prompt_agent import prompt_agent
from app.agents.sound_design_agent import sound_design_agent
from app.services.supabase_service import get_supabase_admin, is_using_mock
from app.services.mock_storage import mock_scenarios
from uuid import uuid4


class Orchestrator:
    """Orchestrates the entire video generation pipeline"""

    async def run_full_pipeline(
        self,
        project_id: str,
        scenario: str,
        characters: Optional[Dict[str, Any]] = None,
        source_rules: Optional[str] = None,
        style_guide: Optional[Dict[str, Any]] = None,
        include_sound_design: bool = True
    ) -> Dict[str, Any]:
        """
        Run the complete generation pipeline

        Args:
            project_id: Project UUID
            scenario: Scenario text
            characters: Optional character config dict with mode, pool, must_include
            source_rules: Optional source material rules
            style_guide: Optional style guide
            include_sound_design: Whether to generate audio recommendations

        Returns:
            Complete generation results
        """
        use_mock = is_using_mock()

        results = {
            "project_id": project_id,
            "steps": []
        }

        # Get project constraints
        if use_mock:
            constraints = {
                "type": "trailer",
                "total_duration": 30,
                "scene_count_target": 3,
                "pacing": "mixed"
            }
        else:
            supabase = get_supabase_admin()
            project_response = supabase.table("projects").select(
                "*"
            ).eq("id", project_id).execute()

            if not project_response.data:
                raise ValueError(f"Project {project_id} not found")

            project = project_response.data[0]
            style_prefs = project.get("style_preferences") or {}
            constraints = {
                "type": project.get("type"),
                "total_duration": project.get("total_duration"),
                "scene_count_target": style_prefs.get("scene_count"),
                "pacing": style_prefs.get("pacing", "mixed")
            }

        # STEP 1: Scenario Analysis - ALWAYS CALLS GEMINI
        results["steps"].append({"step": "scenario_analysis", "status": "processing"})
        scenario_result = await scenario_agent.process(project_id, scenario, constraints)
        results["steps"][-1]["status"] = "completed"
        results["scenario_analysis"] = scenario_result

        # Prepare scenes for next steps
        if use_mock:
            # Create mock scene data from Gemini result
            scenes = []
            for i, scene in enumerate(scenario_result.get("scenes", [])):
                scenes.append({
                    "id": str(uuid4()),
                    "scene_number": i + 1,
                    "description": scene.get("description", ""),
                    "duration": scene.get("duration", 10),
                    "mood": scene.get("mood", "")
                })
        else:
            # Get created scenes from database
            scenes_response = supabase.table("scenes").select(
                "*"
            ).eq("project_id", project_id).order("scene_number").execute()
            scenes = scenes_response.data

        # STEP 2: Character Analysis (if characters provided)
        if characters:
            results["steps"].append({"step": "character_analysis", "status": "processing"})
            character_result = await character_agent.process(project_id, scenes, characters)
            results["steps"][-1]["status"] = "completed"
            results["character_analysis"] = character_result

        # STEP 3: Source Material Analysis (if source provided)
        if source_rules:
            results["steps"].append({"step": "source_analysis", "status": "processing"})
            if use_mock:
                results["steps"][-1]["status"] = "completed"
                results["source_analysis"] = {"scene_instructions": []}
            else:
                source_result = await source_agent.process(project_id, scenes, source_rules)
                results["steps"][-1]["status"] = "completed"
                results["source_analysis"] = source_result

        # STEP 4: Prompt Generation - ALWAYS CALLS GEMINI
        results["steps"].append({"step": "prompt_generation", "status": "processing"})
        prompt_result = await prompt_agent.process(project_id, scenes, style_guide)
        results["steps"][-1]["status"] = "completed"
        results["prompt_generation"] = prompt_result

        # STEP 5: Sound Design - ALWAYS CALLS GEMINI
        if include_sound_design:
            results["steps"].append({"step": "sound_design", "status": "processing"})
            sound_result = await sound_design_agent.process(project_id, scenes)
            results["steps"][-1]["status"] = "completed"
            results["sound_design"] = sound_result

        results["status"] = "completed"
        return results

    async def run_step(
        self,
        step: str,
        project_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a single step of the pipeline

        Args:
            step: Step name (scenario_analysis, character_analysis, etc.)
            project_id: Project UUID
            **kwargs: Step-specific arguments

        Returns:
            Step result
        """
        if step == "scenario_analysis":
            return await scenario_agent.process(
                project_id,
                kwargs.get("scenario", ""),
                kwargs.get("constraints", {})
            )

        elif step == "character_analysis":
            supabase = get_supabase_admin()
            scenes = supabase.table("scenes").select("*").eq(
                "project_id", project_id
            ).order("scene_number").execute().data
            return await character_agent.process(
                project_id,
                scenes,
                kwargs.get("character_config", {})
            )

        elif step == "source_analysis":
            supabase = get_supabase_admin()
            scenes = supabase.table("scenes").select("*").eq(
                "project_id", project_id
            ).order("scene_number").execute().data
            return await source_agent.process(
                project_id,
                scenes,
                kwargs.get("source_rules", "")
            )

        elif step == "prompt_generation":
            supabase = get_supabase_admin()
            scenes = supabase.table("scenes").select("*").eq(
                "project_id", project_id
            ).order("scene_number").execute().data
            return await prompt_agent.process(
                project_id,
                scenes,
                kwargs.get("style_guide")
            )

        elif step == "sound_design":
            supabase = get_supabase_admin()
            scenes = supabase.table("scenes").select("*").eq(
                "project_id", project_id
            ).order("scene_number").execute().data
            return await sound_design_agent.process(project_id, scenes)

        else:
            raise ValueError(f"Unknown step: {step}")


# Singleton instance
orchestrator = Orchestrator()
