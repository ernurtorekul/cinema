from typing import Dict, Any, List, Optional
from app.services.llm_service import llm_service
from app.services.supabase_service import get_supabase_admin, is_using_mock
from app.utils.config import settings


class PromptAgent:
    """Agent for generating image and video prompts"""

    async def process(
        self,
        project_id: str,
        scenes: List[Dict[str, Any]],
        style_guide: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate image and video prompts for all scenes

        Args:
            project_id: Project UUID
            scenes: List of scene data with related info
            style_guide: Optional style guide JSON

        Returns:
            Generated prompts result
        """
        # Prepare scenes for LLM (in mock mode, no DB queries)
        enriched_scenes = []
        for scene in scenes:
            enriched_scenes.append({
                "id": scene.get("scene_number", 1),
                "description": scene.get("description", ""),
                "duration": scene.get("duration", 10),
                "mood": scene.get("mood", ""),
                "characters": [],  # Would be populated from DB in real mode
                "instructions": None  # Would be populated from DB in real mode
            })

        # Default style guide
        if style_guide is None:
            style_guide = {
                "visual_style": "cinematic, dramatic lighting",
                "color_grading": "teal and orange, high contrast",
                "base_prompts": {
                    "quality": "8K, ultra detailed, photorealistic",
                    "lighting": "dramatic lighting, volumetric fog"
                }
            }

        # Run LLM for prompt generation (CALLS CLAUDE)
        result = await llm_service.generate_prompts(
            scenes=enriched_scenes,
            characters=[],
            instructions=[],
            style_guide=style_guide,
            api_key=settings.claude_prompt_agent_api_key,
            use_claude=True
        )

        # In mock mode, just return the result without DB storage
        return result


# Singleton instance
prompt_agent = PromptAgent()
