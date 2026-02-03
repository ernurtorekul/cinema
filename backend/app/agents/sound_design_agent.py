from typing import Dict, Any, List
from app.services.llm_service import llm_service


class SoundDesignAgent:
    """Agent for generating sound design recommendations"""

    async def process(
        self,
        project_id: str,
        scenes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate sound effects and music recommendations

        Args:
            project_id: Project UUID
            scenes: List of scene data with instructions

        Returns:
            Audio design result
        """
        # Prepare scenes for LLM
        enriched_scenes = []
        for scene in scenes:
            enriched_scenes.append({
                "id": scene.get("scene_number", 1),
                "description": scene.get("description", ""),
                "duration": scene.get("duration", 10),
                "mood": scene.get("mood", ""),
                "actions": scene.get("actions", [])
            })

        # Run LLM for sound design (CALLS GEMINI)
        result = await llm_service.generate_sound_design(
            scenes=enriched_scenes,
            instructions=[]
        )

        # Return result without DB storage in mock mode
        return result


# Singleton instance
sound_design_agent = SoundDesignAgent()
