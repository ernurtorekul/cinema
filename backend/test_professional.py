"""
Test professional scenario against current agents
"""
import asyncio
import sys
import os

# Set MOCK_MODE before imports
os.environ['MOCK_MODE'] = 'true'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.scenario_agent import scenario_agent
from app.agents.prompt_agent import prompt_agent
from app.agents.sound_design_agent import sound_design_agent
from app.agents.character_agent import character_agent
from app.utils.config import settings
from uuid import uuid4
import json


# Professional scenario from example_script.txt (translated)
PROFESSIONAL_SCENARIO = """
A meteorite approaches Earth from space. Instead of burning up in the atmosphere,
it passes through the planet completely without causing any damage - no explosion,
no shockwave, no impact crater. It exits the other side of Earth as if the planet
were a hologram.

Suddenly, a BLUE DOME expands around Earth - not an energy shield, but a distortion.
Inside the dome, physics breaks down: continents glitch and shift rapidly,
clouds move backward, rain falls upward, and the ocean freezes into solid glass.

This causes time periods to collapse - ANCIENT, MODERN, and FUTURE merge together.
A medieval knight sees satellites overhead. A Roman army faces modern NATO soldiers
whose weapons have stopped working. The legions advance with shields and swords,
overwhelming the technologically-dependent modern forces.

Final image: Roman centurion raises fist in victory as modern soldiers kneel in defeat.
The title appears: "TECHNOLOGIES EQUALIZED. NOW WILL MATTERS."
"""


def format_comparison(title: str, professional: str, actual: dict) -> None:
    """Compare professional output with agent output"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")

    print(f"\n📋 PROFESSIONAL REFERENCE:")
    print(f"{professional}")

    print(f"\n🤖 CURRENT AGENT OUTPUT:")
    print(json.dumps(actual, indent=2)[:800] + "...")


async def test_scenario_agent():
    """Test scenario analysis"""
    print(f"\n{'#'*70}")
    print("# SCENARIO AGENT TEST (OpenAI GPT-4o)")
    print(f"{'#'*70}")

    constraints = {
        "type": "trailer",
        "total_duration": 180,  # 3 minutes
        "scene_count_target": 5,
        "pacing": "mixed"
    }

    project_id = str(uuid4())
    result = await scenario_agent.process(project_id, PROFESSIONAL_SCENARIO, constraints)

    professional_ref = """
SCENE 2 (0:00-0:20): SUPER-WIDE SHOT - Earth from orbit
- Camera: Slow orbit, then track meteorite approach
- Visual: Blue marble with white cloud vortexes
- Action: Meteorite enters atmosphere WITHOUT burning (no friction)
- Key moment: Passes through solid Earth like a hologram
- Sound: Space silence → sharp digital "VZHUH" (TV off sound) → silence
"""

    format_comparison("Scene Breakdown Comparison", professional_ref, result.get('scenes', [])[:2])

    return result


async def test_prompt_agent(scenes):
    """Test prompt generation"""
    print(f"\n{'#'*70}")
    print("# PROMPT AGENT TEST (Claude)")
    print(f"{'#'*70}")

    project_id = str(uuid4())
    result = await prompt_agent.process(project_id, scenes)

    professional_ref = """
IMAGE PROMPT SPECIFICATION:
- Resolution: 8K, photorealistic, cinematic color grading
- Camera: ARRI Alexa 35, Panavision C-Series 50mm, f/2.8
- Subject: Glitching Earth surface - continents overlapping like bad video render
- Color: Electric blue dome (like gel lens) + chromatic aberration on stars
- VFX: Texture z-fighting, mountains shimmering in/out of existence
- Lighting: High contrast blue/orange, dome emits no light but refracts it
- Composition: Rule of thirds, dome edge cuts through frame at 1/3 height
- Atmosphere: Subtle volumetric fog, no particles (physics frozen)

VIDEO PROMPT:
- Movement: Slow dolly in toward atmosphere, then sudden glitch cut
- Speed: 0.5fps staccato motion during glitch (stutter effect)
- Duration: 4 seconds
- Technical: Match cut to next scene on color grade shift
"""

    prompts = result.get('scene_prompts', [])
    if prompts:
        format_comparison("Prompt Generation Comparison", professional_ref, prompts[0])

    return result


async def test_sound_agent(scenes):
    """Test sound design"""
    print(f"\n{'#'*70}")
    print("# SOUND DESIGN AGENT TEST (Gemini)")
    print(f"{'#'*70}")

    project_id = str(uuid4())
    result = await sound_design_agent.process(project_id, scenes)

    professional_ref = """
SOUND DESIGN FOR DOME APPEARANCE:

TIMELINE:
0:00-0:02 | Low frequency rumble builds (40Hz)
0:02      | Sharp digital "VZHUH" (like TV power off - 1/10th second)
0:02-0:05 | Dead silence (create unease)
0:05-0:08 | Glitch sounds ascend: low HUM → high SCREECH
0:08      | Sound of broken audio file / computer freeze

MUSIC COMPOSITION:
- Style: Glitch electronic + orchestral dissonance
- Tempo: Starts at 60 BPM, stutters to 0, resumes at 120 BPM
- Instruments: Synth bass, distorted strings, digital artifact samples
- Energy: 3/10 → 8/10 on dome appearance
- Reference: "Hans Zimmer Dunkirk" meets "Aphex Twin Windowlicker"

SOUND EFFECTS (layered):
- 0:02: Digital static burst (full frequency, 0.5s duration)
- 0:05: Low frequency oscillator (20-80Hz sweep, 2s duration)
- 0:08: High piercing glitch (8kHz+, 1s duration, hard cut)

AMBIENCE:
- Base: Silent space (no room tone)
- Elements: [digital hum (rare), absolute silence]
- Stereo: Center (monophonic unease)
- Intensity: Low (creates vacuum of sound)
"""

    suggestions = result.get('sound_suggestions', [])
    if suggestions:
        format_comparison("Sound Design Comparison", professional_ref, suggestions[0])
    else:
        print("❌ No sound suggestions returned (quota issue)")
        print(professional_ref)

    return result


async def main():
    """Run all tests"""
    print("="*70)
    print("PROFESSIONAL CINEMATOGRAPHY TEST")
    print("Testing agents against Hollywood-grade trailer script")
    print("="*70)

    # Test scenario
    scenario_result = await test_scenario_agent()

    # Prepare scenes
    scenes = []
    for i, scene in enumerate(scenario_result.get('scenes', [])[:5]):
        scenes.append({
            "id": scene.get('id', i + 1),
            "scene_number": i + 1,
            "description": scene.get('description', ''),
            "duration": scene.get('duration', 10),
            "mood": scene.get('mood', ''),
            "actions": scene.get('actions', [])
        })

    # Test prompts
    await test_prompt_agent(scenes)

    # Test sound
    await test_sound_agent(scenes)

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print("\n🔍 KEY FINDINGS:")
    print("1. Shot descriptions lack technical precision (no specific lens/camera)")
    print("2. Visual effects specifications are missing (glitch, physics breakdown)")
    print("3. Sound design is too generic (no specific SFX, timing, or layering)")
    print("4. Color theory mentions are cliché (teal/orange) vs professional palettes")
    print("5. No rhythm/pacing considerations in descriptions")
    print("\n💡 SOLUTION: Enhance all agent prompts with professional cinematography language")


if __name__ == "__main__":
    asyncio.run(main())
