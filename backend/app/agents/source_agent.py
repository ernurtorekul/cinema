from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.utils.config import settings


class SourceAgent:
    """Agent for processing source materials and mapping to scenes"""

    async def process(
        self,
        project_id: str,
        scenes: List[Dict[str, Any]],
        source_rules: str
    ) -> Dict[str, Any]:
        """
        Process source materials and generate scene instructions

        Args:
            project_id: Project UUID
            scenes: List of scene data
            source_rules: Extracted rules from source files

        Returns:
            Scene instructions result
        """
        # Run LLM analysis for source material mapping (CALLS GEMINI)
        result = await llm_service.analyze_source_material(
            scenes=scenes,
            source_rules=source_rules,
            api_key=settings.gemini_source_agent_api_key
        )

        # Return result without DB storage in mock mode
        return result


# Singleton instance
source_agent = SourceAgent()
