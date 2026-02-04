from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.utils.config import settings


class CharacterAgent:
    """Agent for assigning characters to scenes"""

    async def process(
        self,
        project_id: str,
        scenes: List[Dict[str, Any]],
        character_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Assign characters to scenes and ensure consistency

        Args:
            project_id: Project UUID
            scenes: List of scene data
            character_config: Character configuration from frontend
                - mode: "ai_decides" or "manual"
                - pool: (optional) Full celebrity pool when ai_decides
                - must_include: (optional) Characters to prioritize
                - characters: (optional) Characters for manual mode

        Returns:
            Character assignment result
        """
        if not character_config:
            return {"assignments": [], "consistency_map": {}}

        mode = character_config.get("mode", "ai_decides")

        if mode == "ai_decides":
            # AI decides which characters fit each scene
            return await self._ai_assign_characters(scenes, character_config)
        else:
            # Manual mode - use provided characters directly
            characters = character_config.get("characters", [])
            if not characters:
                return {"assignments": [], "consistency_map": {}}
            return await self._manual_assign_characters(scenes, characters)

    async def _ai_assign_characters(
        self,
        scenes: List[Dict[str, Any]],
        character_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI analyzes scenes and assigns the most suitable characters
        """
        pool = character_config.get("pool", [])
        must_include = character_config.get("must_include", [])

        # Build character list for LLM
        characters_for_llm = []

        # Add must_include characters first
        for char in must_include:
            characters_for_llm.append({
                "name": char.get("name"),
                "traits": char.get("traits", []),
                "style": char.get("style", ""),
                "typical_roles": char.get("typical_roles", []),
                "priority": "must_include"
            })

        # Add rest of pool
        for char in pool:
            name = char.get("name")
            # Skip if already in must_include
            if any(c.get("name") == name for c in must_include):
                continue
            characters_for_llm.append({
                "name": name,
                "traits": char.get("traits", []),
                "style": char.get("style", ""),
                "typical_roles": char.get("typical_roles", []),
                "priority": "pool"
            })

        if not characters_for_llm:
            return {"assignments": [], "consistency_map": {}}

        # Run LLM analysis for intelligent character assignment
        result = await llm_service.analyze_characters(
            scenes=scenes,
            characters=characters_for_llm,
            api_key=settings.gemini_character_agent_api_key
        )

        return result

    async def _manual_assign_characters(
        self,
        scenes: List[Dict[str, Any]],
        characters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Manual mode - assign provided characters to scenes based on simple rules
        """
        assignments = []
        consistency_map = {}

        # Build consistency map
        for char in characters:
            consistency_map[char.get("name", "")] = {
                "base_traits": char.get("traits", []),
                "costume": char.get("style", ""),
                "appearances": []
            }

        # Assign characters to scenes (simple round-robin for manual mode)
        for idx, scene in enumerate(scenes):
            scene_chars = []
            for char_idx, char in enumerate(characters):
                # Distribute characters across scenes (max 2-3 per scene)
                if (idx + char_idx) % len(characters) < min(2, len(characters)):
                    scene_chars.append({
                        "name": char.get("name"),
                        "expression": "focused",
                        "pose": "standing",
                        "action": "observing",
                        "costume_notes": char.get("style", "")
                    })
                    if char.get("name") in consistency_map:
                        consistency_map[char.get("name")]["appearances"].append(scene.get("id", idx + 1))

            if scene_chars:
                assignments.append({
                    "scene_id": scene.get("id", idx + 1),
                    "characters": scene_chars
                })

        return {
            "assignments": assignments,
            "consistency_map": consistency_map
        }


# Singleton instance
character_agent = CharacterAgent()
