"""
Test script for the full video generation pipeline
"""
import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set MOCK_MODE before importing any app modules
os.environ['MOCK_MODE'] = 'true'

from app.agents.orchestrator import orchestrator
from app.services.supabase_service import is_using_mock, MockClient
from app.services.mock_storage import mock_projects
from app.services.llm_service import llm_service
from uuid import uuid4


async def test_llm_direct():
    """Test each LLM service directly before running the full pipeline"""
    print("=" * 60)
    print("Testing LLM Services Directly")
    print("=" * 60)

    from app.utils.config import settings

    # Test OpenAI (Scenario Agent)
    print("\n1. Testing OpenAI (Scenario Agent)...")
    try:
        result = await llm_service.analyze_scenario(
            scenario="A person walks into a room and finds a treasure chest.",
            project_type="trailer",
            constraints={"total_duration": 30, "scene_count_target": 2, "pacing": "mixed"},
            api_key=settings.openai_scenario_agent_api_key,
            use_openai=True
        )
        print(f"   ✓ OpenAI response received")
        print(f"   Scenes: {len(result.get('scenes', []))}")
    except Exception as e:
        print(f"   ✗ OpenAI failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Gemini (Character Agent)
    print("\n2. Testing Gemini (Character Agent)...")
    try:
        result = await llm_service.analyze_characters(
            scenes=[{"id": 1, "description": "A tense scene", "mood": "dramatic", "actions": []}],
            characters=[{"name": "Hero", "traits": ["brave", "strong"], "typical_roles": ["action"], "style": "tactical"}],
            api_key=settings.gemini_character_agent_api_key
        )
        print(f"   ✓ Gemini response received")
        print(f"   Assignments: {len(result.get('assignments', []))}")
    except Exception as e:
        print(f"   ✗ Gemini failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Claude (Prompt Agent)
    print("\n3. Testing Claude (Prompt Agent)...")
    try:
        result = await llm_service.generate_prompts(
            scenes=[{"id": 1, "description": "A dramatic scene", "mood": "tense", "actions": [], "camera": "", "lighting": ""}],
            characters=[],
            instructions=[],
            style_guide={"visual_style": "cinematic"},
            api_key=settings.claude_prompt_agent_api_key,
            use_claude=True
        )
        print(f"   ✓ Claude response received")
        print(f"   Scene prompts: {len(result.get('scene_prompts', []))}")
    except Exception as e:
        print(f"   ✗ Claude failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Gemini (Sound Design Agent)
    print("\n4. Testing Gemini (Sound Design Agent)...")
    try:
        result = await llm_service.generate_sound_design(
            scenes=[{"id": 1, "description": "A tense scene", "mood": "dramatic", "duration": 10, "actions": []}],
            instructions=[],
            api_key=settings.gemini_sound_design_agent_api_key
        )
        print(f"   ✓ Gemini Sound Design response received")
        print(f"   Sound suggestions: {len(result.get('sound_suggestions', []))}")
    except Exception as e:
        print(f"   ✗ Gemini Sound Design failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n✓ All LLM services are working!")
    return True


async def test_full_pipeline():
    """Test the full generation pipeline"""

    # Test scenario
    test_scenario = """
    A mysterious hooded figure walks through an ancient stone temple at night.
    Torches flicker on the walls as the figure approaches a glowing artifact on a pedestal.
    The figure reaches out, and the artifact pulses with blue light.
    Suddenly, shadows move in the corners - someone is watching.
    The figure grabs the artifact and turns to face the threat.
    """

    # Create mock project
    project_id = str(uuid4())
    mock_projects[project_id] = {
        "id": project_id,
        "type": "trailer",
        "total_duration": 30,
        "created_at": "2024-01-01T00:00:00Z"
    }

    print(f"Testing pipeline with project ID: {project_id}")
    print(f"MOCK_MODE: {is_using_mock()}")
    print(f"\nScenario: {test_scenario[:100]}...\n")

    # Character config for testing
    character_config = {
        "mode": "ai_decides",
        "pool": [],
        "must_include": []
    }

    # Constraints for scenario analysis
    constraints = {
        "type": "trailer",
        "total_duration": 30,
        "scene_count_target": 3,
        "pacing": "mixed"
    }

    print("=" * 60)
    print("STEP 1: Scenario Analysis (OpenAI GPT-4o)")
    print("=" * 60)

    try:
        from app.agents.scenario_agent import scenario_agent
        scenario_result = await scenario_agent.process(project_id, test_scenario, constraints)
        print(f"✓ Scenario analysis completed")
        print(f"  - Scenes generated: {len(scenario_result.get('scenes', []))}")
        for scene in scenario_result.get('scenes', []):
            print(f"    Scene {scene.get('id')}: {scene.get('description', '')[:60]}...")
        print(f"  - Total duration: {scenario_result.get('total_duration', 0)}s")
    except Exception as e:
        print(f"✗ Scenario analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("STEP 2: Character Analysis (Gemini)")
    print("=" * 60)

    # Prepare scenes for character agent
    scenes = []
    for i, scene in enumerate(scenario_result.get('scenes', [])):
        scenes.append({
            "id": scene.get('id', i + 1),
            "scene_number": i + 1,
            "description": scene.get('description', ''),
            "duration": scene.get('duration', 10),
            "mood": scene.get('mood', ''),
            "actions": scene.get('actions', [])
        })

    try:
        from app.agents.character_agent import character_agent
        character_result = await character_agent.process(project_id, scenes, character_config)
        print(f"✓ Character analysis completed")
        print(f"  - Assignments: {len(character_result.get('assignments', []))}")
    except Exception as e:
        print(f"✗ Character analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("STEP 3: Prompt Generation (Claude)")
    print("=" * 60)

    try:
        from app.agents.prompt_agent import prompt_agent
        prompt_result = await prompt_agent.process(project_id, scenes)
        print(f"✓ Prompt generation completed")
        print(f"  - Scene prompts: {len(prompt_result.get('scene_prompts', []))}")
        if prompt_result.get('scene_prompts'):
            for sp in prompt_result['scene_prompts'][:2]:  # Show first 2
                print(f"    Scene {sp.get('scene_id')}: {len(sp.get('image_prompts', []))} image prompts, {len(sp.get('video_prompts', []))} video prompts")
    except Exception as e:
        print(f"✗ Prompt generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("STEP 4: Sound Design (Gemini)")
    print("=" * 60)

    try:
        from app.agents.sound_design_agent import sound_design_agent
        sound_result = await sound_design_agent.process(project_id, scenes)
        print(f"✓ Sound design completed")
        suggestions = sound_result.get('sound_suggestions', [])
        print(f"  - Sound suggestions: {len(suggestions)}")
        for s in suggestions[:2]:  # Show first 2
            print(f"    Scene {s.get('scene_id')}: {s.get('music', 'N/A')[:50]}...")
    except Exception as e:
        print(f"✗ Sound design failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)

    # Show summary
    print(f"\nSummary:")
    print(f"  - Project ID: {project_id}")
    print(f"  - Scenes: {len(scenes)}")
    print(f"  - Scenario Agent: OpenAI GPT-4o ✓")
    print(f"  - Character Agent: Gemini ✓")
    print(f"  - Prompt Agent: Claude ✓")
    print(f"  - Sound Design Agent: Gemini ✓")


async def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("AI VIDEO GENERATION PLATFORM - PIPELINE TEST")
    print("=" * 60)

    # First test LLM services directly
    if not await test_llm_direct():
        print("\n✗ LLM service tests failed. Please check API keys.")
        return

    print("\n")

    # Then run full pipeline
    await test_full_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
