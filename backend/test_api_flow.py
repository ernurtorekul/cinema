"""
Test the full API flow - create project, submit scenario, generate
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_flow():
    """Test the complete API flow"""
    print("=" * 60)
    print("Testing Full API Flow")
    print("=" * 60)

    # 1. Test root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 2. Test health endpoint
    print("\n2. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 3. Get characters pool
    print("\n3. Testing characters pool endpoint...")
    response = requests.get(f"{BASE_URL}/api/projects/characters/pool")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Pool: {data.get('pool_name')}")
    print(f"   Characters available: {len(data.get('characters', []))}")

    # 4. Create a project
    print("\n4. Creating a new project...")
    project_data = {
        "type": "trailer",
        "total_duration": 30,
        "scene_count_target": 3,
        "pacing": "mixed",
        "style_preferences": {}
    }
    response = requests.post(
        f"{BASE_URL}/api/projects",
        json=project_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    project = response.json()
    print(f"   Project ID: {project.get('id')}")
    project_id = project.get('id')

    # 5. Submit scenario
    print("\n5. Submitting scenario...")
    scenario_data = {
        "text": """
        A mysterious hooded figure walks through an ancient stone temple at night.
        Torches flicker on the walls as the figure approaches a glowing artifact on a pedestal.
        The figure reaches out, and the artifact pulses with blue light.
        Suddenly, shadows move in the corners - someone is watching.
        The figure grabs the artifact and turns to face the threat.
        """
    }
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/scenario",
        json=scenario_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")

    # 6. Trigger full generation
    print("\n6. Triggering full generation pipeline...")
    print("   This may take 30-60 seconds as it calls multiple LLM APIs...")

    generation_data = {
        "character_config": {
            "mode": "ai_decides",
            "pool": [],
            "must_include": []
        },
        "include_sound_design": True
    }

    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/generate",
        json=generation_data,
        headers={"Content-Type": "application/json"},
        timeout=120
    )
    elapsed = time.time() - start_time

    print(f"   Status: {response.status_code}")
    print(f"   Time taken: {elapsed:.1f} seconds")

    if response.status_code == 200:
        result = response.json()

        print("\n" + "=" * 60)
        print("GENERATION RESULTS")
        print("=" * 60)

        # Scenario analysis
        scenario = result.get('scenario_analysis', {})
        scenes = scenario.get('scenes', [])
        print(f"\nScenario Analysis (OpenAI GPT-4o):")
        print(f"  - Scenes generated: {len(scenes)}")
        for i, scene in enumerate(scenes[:3], 1):
            print(f"    Scene {i}: {scene.get('description', '')[:60]}...")

        # Character analysis
        character = result.get('character_analysis', {})
        assignments = character.get('assignments', [])
        print(f"\nCharacter Analysis (Gemini):")
        print(f"  - Assignments: {len(assignments)}")

        # Prompt generation
        prompts = result.get('prompt_generation', {})
        scene_prompts = prompts.get('scene_prompts', [])
        print(f"\nPrompt Generation (Claude):")
        print(f"  - Scene prompts: {len(scene_prompts)}")
        for sp in scene_prompts[:2]:
            print(f"    Scene {sp.get('scene_id')}: {len(sp.get('image_prompts', []))} image prompts, {len(sp.get('video_prompts', []))} video prompts")

        # Sound design
        sound = result.get('sound_design', {})
        suggestions = sound.get('sound_suggestions', [])
        print(f"\nSound Design (Gemini):")
        print(f"  - Sound suggestions: {len(suggestions)}")
        for s in suggestions[:2]:
            print(f"    Scene {s.get('scene_id')}: {s.get('music', 'N/A')[:50]}...")

        print("\n" + "=" * 60)
        print("✅ FULL API TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print(f"   Error: {response.text}")

    return project_id


if __name__ == "__main__":
    try:
        test_api_flow()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the backend server.")
        print("   Please make sure the server is running:")
        print("   cd /Users/ernurtorekul/unik/automation/backend")
        print("   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
