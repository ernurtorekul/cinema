from typing import Dict, Any
from app.services.llm_service import llm_service
from app.services.supabase_service import get_supabase_admin, is_using_mock
from app.utils.config import settings
from uuid import uuid4


class ScenarioAgent:
    """Agent for analyzing scenario and breaking down into scenes"""

    async def process(self, project_id: str, scenario: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process scenario and generate scene breakdown

        Args:
            project_id: Project UUID
            scenario: Scenario text
            constraints: Project constraints (type, duration, etc.)

        Returns:
            Scene analysis result
        """
        # Run LLM analysis (calls OpenAI GPT)
        result = await llm_service.analyze_scenario(
            scenario=scenario,
            project_type=constraints.get("type", "trailer"),
            constraints=constraints,
            api_key=settings.openai_scenario_agent_api_key,
            use_openai=True
        )

        # LLM returns dict, extract scenes
        scenes_list = result.get("scenes", [])
        scenes_data = []

        # Only store in database if NOT in mock mode
        if not is_using_mock():
            supabase = get_supabase_admin()
            for scene in scenes_list:
                scene_data = {
                    "project_id": project_id,
                    "scene_number": scene.get("id", 1),
                    "description": scene.get("description", ""),
                    "duration": scene.get("duration", 10),
                    "mood": scene.get("mood", "")
                }
                response = supabase.table("scenes").insert(scene_data).execute()
                scenes_data.append(response.data[0])
        else:
            # Mock mode - just return the LLM result with IDs
            for scene in scenes_list:
                scenes_data.append({
                    "id": str(uuid4()),
                    "scene_number": scene.get("id", 1),
                    "description": scene.get("description", ""),
                    "duration": scene.get("duration", 10),
                    "mood": scene.get("mood", "")
                })

        return {
            "title": result.get("title", ""),
            "overall_idea": result.get("overall_idea", ""),
            "scenes": scenes_data,
            "total_duration": result.get("total_duration", 30),
            "scene_count": result.get("scene_count", len(scenes_data)),
            "raw_llm_result": result
        }


# Singleton instance
scenario_agent = ScenarioAgent()
