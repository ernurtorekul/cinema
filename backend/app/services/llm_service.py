"""
Service for interacting with Gemini AI
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
import google.generativeai as genai
import json
from app.utils.config import settings

# Available Gemini models (using latest stable)
GEMINI_MODEL = "gemini-2.0-flash-lite"  # Using lite variant for better quota
GEMINI_PRO_MODEL = "gemini-2.5-flash"  # Pro model (if available)


class LLMService:
    """Service for interacting with Gemini AI"""

    # Cinematography Reference Material (from books folder)
    # Based on: "In the Blink of an Eye" by Walter Murch, cinematography guides
    CINEMATOGRAPHY_REFERENCE = """
    CINEMATOGRAPHY PRINCIPLES:

    1. ESTABLISHING SHOTS: Start with wide shot to establish location/context
    2. THE RULE OF SIX: (per Walter Murch) Emotion, Story, Rhythm, Eye-trace, 2D Plane, 3D Space
    3. CUTTING ON ACTION: Cut during movement to hide the edit
    4. SHOT REVERSE SHOT: For dialogue and confrontation
    5. 180-DEGREE RULE: Maintain spatial relationship between characters
    6. RACK FOCUS: Shift focus between foreground/background to reveal information

    CAMERA MOVEMENTS:
    - DOLLY IN: Moves closer to subject (increasing intensity/intimacy)
    - DOLLY OUT: Moves away (revealing context, decreasing intensity)
    - TRACKING: Follows subject movement (parallel to action)
    - CRANE UP/DOWN: Reveals or diminishes subject's power
    - PAN: Reveals what's to the side (discovery)
    - TILT: Reveals what's above/below (power dynamics)
    - HANDHELD: Creates documentary realism, unease

    LIGHTING PRINCIPLES:
    - THREE-POINT LIGHTING: Key (main), Fill (softens shadows), Back (separation)
    - LOW KEY: High contrast, dramatic shadows (mystery, tension)
    - HIGH KEY: Even illumination (comedy, light mood)
    - PRACTICAL LIGHTS: Lights within the scene (lamps, windows)
    - MOTIVATED LIGHTING: Light sources that make sense in the scene

    COLOR THEORY:
    - TEAL & ORANGE: Classic cinematic contrast (cool shadows, warm skin tones)
    - MONOCHROMATIC: Single color family (unified mood)
    - COMPLEMENTARY: Opposite colors (tension, conflict)
    - WARM TONES: Comfort, nostalgia, happiness
    - COOL TONES: Detachment, sadness, mystery

    PACING RHYTHMS:
    - FAST CUTS: Action, excitement, chaos
    - SLOW CUTS: Contemplation, sadness, epic scale
    - MIXED: Build tension then release
    - MATCH CUTS: Visual similarities between shots for thematic connection

    COMPOSITION:
    - RULE OF THIRDS: Place subject on intersection points
    - CENTER FRAME: Power, focus, confrontation
    - FOREGROUND ELEMENTS: Create depth
    - NEGATIVE SPACE: Isolation, emptiness, anticipation
    """

    # Character Acting Reference
    ACTING_REFERENCE = """
    CHARACTER EXPRESSION & BODY LANGUAGE:

    1. EYES ARE KEY: The window to emotion - focus on eye contact and direction
    2. SUBTEXT: What the character really feels vs. what they show
    3. PHYSICAL ACTION: "Show, don't tell" - behavior reveals character
    4. STILLNESS: Powerful moments often have no movement
    5. REACTION SHOTS: How others respond reveals context

    EMOTIONAL CONTINUUM:
    - RESTRAINED: Subtle, internal emotion (close-ups needed)
    - EXPRESSED: Clear outward emotion
    - OVERWHELMING: Cannot be contained (physical expression)
    - CONFLICTED: Mixed emotions create dramatic tension
    """

    # Camera parameters
    CAMERAS = [
        "RED V-Raptor",
        "Sony Venice",
        "Max Film Camera",
        "ARRI Alexa 35",
        "Arriflex 16SR",
        "Panavision Millennium DXL 2"
    ]

    LENSES = [
        "Lensbaby",
        "Hawk V-Lite",
        "Laowa Macro",
        "Canon K-35",
        "Panavision C-Series",
        "ARRI Signature Prime",
        "Cooke S4",
        "Petzval",
        "Helios",
        "JDC Xtal Xpress",
        "Zeiss Ultra Prime"
    ]

    FOCAL_LENGTHS = ["8mm", "14mm", "35mm", "50mm"]
    APERTURES = ["f/1.4", "f/4", "f/11"]

    def _get_camera_params(self) -> Dict[str, str]:
        """Get random camera parameters"""
        import random
        return {
            "camera": random.choice(self.CAMERAS),
            "lens": random.choice(self.LENSES),
            "focal_length": random.choice(self.FOCAL_LENGTHS),
            "aperture": random.choice(self.APERTURES)
        }

    async def _generate_content(self, prompt: str, api_key: str) -> str:
        """Generate content using Gemini with specific API key"""
        try:
            # Configure with the specific API key for this call
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(GEMINI_MODEL)

            def call_gemini():
                return model.generate_content(prompt)

            response = await asyncio.to_thread(call_gemini)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Return a fallback response if Gemini fails
            return '{"scenes": [{"id": 1, "description": "Scene generated (API error - using fallback)", "actions": [], "duration": 10, "mood": "neutral"}]}'

    async def analyze_scenario(
        self,
        scenario: str,
        project_type: str,
        constraints: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Analyze scenario and break down into scenes using cinematography principles"""

        # Determine scene count guidance
        scene_count_target = constraints.get('scene_count_target')
        if scene_count_target:
            scene_guidance = f"Break down into exactly {scene_count_target} scenes"
        else:
            scene_guidance = "Break down into an appropriate number of scenes based on the scenario complexity (typically 2-5 scenes)"

        pacing = constraints.get('pacing', 'mixed')
        pacing_guidance = {
            "fast": "Use quick cuts, dynamic camera movements, high energy",
            "slow": "Use longer takes, measured pacing, contemplative mood",
            "mixed": "Vary pacing - build tension then release"
        }.get(pacing, "Mixed pacing with variation")

        prompt = f"""You are a professional film director and cinematographer. Analyze this scenario for a {project_type}.

SCENARIO: {scenario}

{self.CINEMATOGRAPHY_REFERENCE}

CONSTRAINTS:
- Total duration: {constraints.get('total_duration', 'N/A')} seconds
- Scene count: {'AI decide based on scenario complexity' if not scene_count_target else scene_count_target}
- Pacing approach: {pacing_guidance}

{scene_guidance}. For each scene provide:

1. DESCRIPTION: Vivid, cinematic description of what happens
2. ACTIONS: 3-4 specific, actionable events (use strong verbs)
3. DURATION: Appropriate length in seconds (considering total duration)
4. MOOD: Primary emotional tone (e.g., "tense, mysterious with underlying threat")
5. CAMERA: Suggested camera approach (e.g., "wide establishing shot, slow dolly in")
6. LIGHTING: Lighting style (e.g., "low key blue moonlight for mystery")
7. ENHANCEMENTS: Visual effects or color notes

Think like a director: Each scene should advance the story, create emotional impact, and use cinematic language.

Return ONLY valid JSON:
{{
  "scenes": [
    {{
      "id": 1,
      "description": "Cinematic description with clear visual and action",
      "actions": ["specific action 1", "specific action 2", "specific action 3"],
      "duration": 10,
      "mood": "primary emotion, secondary feeling",
      "camera": "camera movement and positioning",
      "lighting": "lighting setup and mood",
      "enhancements": "color, effects, visual notes"
    }}
  ],
  "total_duration": 30
}}
"""

        response = await self._generate_content(prompt, api_key)

        # Try to parse JSON from the response
        try:
            # Find JSON in the response
            json_match = self._extract_json(response)
            if json_match:
                data = json.loads(json_match)
                return data
        except Exception as e:
            print(f"Failed to parse Gemini response: {e}")

        # Fallback if parsing fails
        return {
            "scenes": [
                {
                    "id": 1,
                    "description": scenario[:100] + "...",
                    "actions": ["main action"],
                    "duration": 10,
                    "mood": "dramatic"
                }
            ],
            "total_duration": constraints.get('total_duration', 15)
        }

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from Gemini response (handles markdown code blocks)"""
        import re

        # First, try to extract from markdown code blocks (```json ... ```)
        code_block_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
        code_blocks = re.findall(code_block_pattern, text)
        for block in code_blocks:
            block = block.strip()
            try:
                json.loads(block)  # Validate it's valid JSON
                return block
            except:
                continue

        # Try to find JSON object in the response
        matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
        for match in matches:
            try:
                json.loads(match)  # Validate it's valid JSON
                return match
            except:
                continue
        # Try with outer braces for nested structures
        json_match = re.search(r'\{[\s\S]*\}', text, re.DOTALL)
        if json_match:
            try:
                json.loads(json_match.group())
                return json_match.group()
            except:
                pass
        return None

    async def analyze_characters(
        self,
        scenes: List[Dict[str, Any]],
        characters: List[Dict[str, Any]],
        api_key: str
    ) -> Dict[str, Any]:
        """Intelligently assign characters to scenes based on traits, roles, and scene requirements"""

        if not characters:
            return {"assignments": [], "consistency_map": {}}

        # Build character descriptions for the prompt
        char_descriptions = []
        must_include_names = set()

        for char in characters:
            name = char.get("name", "Unknown")
            traits = char.get("traits", [])
            typical_roles = char.get("typical_roles", [])
            style = char.get("style", "")
            priority = char.get("priority", "pool")

            if priority == "must_include":
                must_include_names.add(name)

            desc = f"- {name}: Traits [{', '.join(traits)}]"
            if typical_roles:
                desc += f", Typical Roles [{', '.join(typical_roles)}]"
            if style:
                desc += f", Style: {style}"
            if priority == "must_include":
                desc += " (MUST INCLUDE)"
            char_descriptions.append(desc)

        # Build scene descriptions
        scene_descriptions = []
        for scene in scenes:
            desc = scene.get("description", "")
            mood = scene.get("mood", "")
            actions = scene.get("actions", [])
            scene_desc = f"Scene {scene.get('id', scene.get('scene_number', '?'))}: {desc}"
            if mood:
                scene_desc += f" (Mood: {mood})"
            if actions:
                scene_desc += f" - Actions: {', '.join(actions[:3])}"
            scene_descriptions.append(scene_desc)

        must_include_str = f", ".join(must_include_names) if must_include_names else "None - AI decides"

        prompt = f"""You are a casting director AI. Assign the BEST characters to each scene based on what makes narrative sense.

AVAILABLE CELEBRITIES/CHARACTERS:
{chr(10).join(char_descriptions)}

CHARACTERS THAT MUST BE INCLUDED: {must_include_str}

SCENES TO CAST:
{chr(10).join(scene_descriptions)}

INSTRUCTIONS:
1. Analyze each scene's mood, action, and requirements
2. Match characters whose TRAITS and TYPICAL ROLES fit each scene
3. Prioritize "MUST INCLUDE" characters - give them important roles
4. For intense/action scenes: choose characters with traits like "strong", "action-hero", "fierce", "intense"
5. For mysterious/stealth scenes: choose characters with traits like "mysterious", "calculating", "cool"
6. For emotional scenes: choose characters with traits like "emotional", "expressive"
7. A scene can have 0-2 characters (don't force characters if they don't fit)
8. Keep consistent casting - the same character should look similar across scenes

For each character assigned, provide:
- Their name
- Expression: Based on scene mood and character traits
- Pose: Appropriate for the action (e.g., "crouching", "standing tall", "drawing weapon")
- Action: What they're specifically doing in this scene
- Costume notes: Based on their style + scene requirements

Return ONLY valid JSON in this format:
{{
  "assignments": [
    {{
      "scene_id": 1,
      "characters": [
        {{
          "name": "CharacterName",
          "expression": "focused, wary",
          "pose": "crouching behind cover",
          "action": "scanning area for threats",
          "costume_notes": "tactical gear matching their style, dust on clothes"
        }}
      ]
    }}
  ],
  "consistency_map": {{
    "CharacterName": {{
      "base_traits": ["trait1", "trait2"],
      "costume": "base costume description",
      "appearances": [1, 3]
    }}
  }}
}}
"""

        response = await self._generate_content(prompt, api_key)

        # Check if we got a quota error/fallback response
        if "API error" in response or "Scene generated (API error" in response:
            print("Gemini quota exceeded, using fallback character assignment")
            # Simple fallback: assign first character to first scene
            if characters:
                first_char = characters[0]
                return {
                    "assignments": [
                        {
                            "scene_id": scenes[0].get("id", scenes[0].get("scene_number", 1)),
                            "characters": [
                                {
                                    "name": first_char.get("name", "Unknown"),
                                    "expression": "determined",
                                    "pose": "standing",
                                    "action": "observing",
                                    "costume_notes": first_char.get("style", "standard attire")
                                }
                            ]
                        }
                    ],
                    "consistency_map": {
                        first_char.get("name", "Unknown"): {
                            "base_traits": first_char.get("traits", []),
                            "costume": first_char.get("style", ""),
                            "appearances": [scenes[0].get("id", scenes[0].get("scene_number", 1))]
                        }
                    }
                }

        # Parse response
        try:
            json_match = self._extract_json(response)
            if json_match:
                return json.loads(json_match)
        except Exception as e:
            print(f"Failed to parse character response: {e}")

        return {"assignments": [], "consistency_map": {}}

    async def analyze_source_material(
        self,
        scenes: List[Dict[str, Any]],
        source_rules: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Map source material rules to scenes"""

        scenes_text = json.dumps(scenes, indent=2)

        prompt = f"""Given these scenes:
{scenes_text}

And these production/cinematography rules:
{source_rules}

Provide second-by-second breakdown for each scene:
- Camera angle/movement
- Transition in/out
- Lighting notes
- Visual style cues

Return ONLY valid JSON in this format:
{{
  "scene_instructions": [
    {{
      "scene_id": 1,
      "breakdown": [
        {{
          "time": "0-2s",
          "camera": "Wide shot, slow push-in",
          "lighting": "Low key, blue moonlight",
          "action": "Alex emerges from shadows"
        }}
      ],
      "transition_in": "fade from black",
      "transition_out": "cut to scene 2"
    }}
  ]
}}
"""

        response = await self._generate_content(prompt, api_key)

        try:
            json_match = self._extract_json(response)
            if json_match:
                return json.loads(json_match)
        except Exception as e:
            print(f"Failed to parse source response: {e}")

        return {"scene_instructions": []}

    async def generate_prompts(
        self,
        scenes: List[Dict[str, Any]],
        characters: List[Dict[str, Any]],
        instructions: List[Dict[str, Any]],
        style_guide: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Generate professional image and video prompts using cinematography principles"""

        camera_params = self._get_camera_params()

        # Build scene descriptions with more detail
        scenes_data = []
        for scene in scenes:
            scene_info = {
                "id": scene.get("id", scene.get("scene_number", 1)),
                "description": scene.get("description", ""),
                "mood": scene.get("mood", ""),
                "actions": scene.get("actions", []),
                "camera": scene.get("camera", ""),
                "lighting": scene.get("lighting", "")
            }
            scenes_data.append(scene_info)

        prompt = f"""You are a professional cinematographer and visual effects artist. Generate production-ready AI image and video prompts.

{self.CINEMATOGRAPHY_REFERENCE}

SCENES TO GENERATE PROMPTS FOR:
{json.dumps(scenes_data, indent=2)}

For EACH scene, generate DETAILED prompts:

IMAGE PROMPTS must include:
1. Technical specs: 8K resolution, photorealistic, cinematic color grading
2. Camera: {camera_params['camera']} with {camera_params['lens']} at {camera_params['focal_length']} {camera_params['aperture']}
3. Subject: Detailed description of who/what is in frame
4. Action: What is happening (use active verbs)
5. Lighting: Specific lighting setup (motivated practicals, three-point, etc.)
6. Color: Color grading approach (e.g., "teal shadows with warm skin tones", "monochromatic blue for isolation")
7. Atmosphere: Environmental elements (fog, dust, particles)
8. Composition: Frame arrangement (rule of thirds, center frame for power, etc.)

VIDEO PROMPTS must include:
1. Camera movement: Specific motion (dolly in/out, tracking, crane, pan, tilt, handheld)
2. Speed: Pace of movement (slow push for intimacy, fast whip for action)
3. Subject action: What happens during the shot
4. Duration: Length in seconds
5. Technical: Camera, lens, aperture for continuity

Return ONLY valid JSON:
{{
  "scene_prompts": [
    {{
      "scene_id": 1,
      "image_prompts": [
        {{
          "time": "0-5s",
          "prompt": "8K photorealistic cinematic shot, {camera_params['camera']} with {camera_params['lens']} at {camera_params['focal_length']} {camera_params['aperture']}. [DETAILED SCENE DESCRIPTION]. Three-point lighting with warm key and cool fill. Teal and orange color grading with high contrast. Atmospheric volumetric fog. Rule of thirds composition."
        }}
      ],
      "video_prompts": [
        {{
          "time": "0-5s",
          "prompt": "Slow dolly in toward subject, increasing tension and intimacy. Camera pushes in from wide shot to medium close-up over 5 seconds.",
          "camera": "{camera_params['camera']}",
          "lens": "{camera_params['lens']}",
          "aperture": "{camera_params['aperture']}"
        }}
      ]
    }}
  ]
}}
"""

        response = await self._generate_content(prompt, api_key)

        try:
            json_match = self._extract_json(response)
            if json_match:
                return json.loads(json_match)
        except Exception as e:
            print(f"Failed to parse prompts response: {e}")

        # Fallback prompts
        return {
            "scene_prompts": [
                {
                    "scene_id": 1,
                    "image_prompts": [
                        {
                            "time": "0-5s",
                            "prompt": f"8K cinematic shot, {scenes[0].get('description', 'Scene')}, {camera_params['camera']} with {camera_params['lens']} {camera_params['focal_length']} {camera_params['aperture']}, teal and orange grading, dramatic lighting",
                            "negative_prompt": "blurry, low quality, cartoon"
                        }
                    ],
                    "video_prompts": [
                        {
                            "time": "0-5s",
                            "prompt": "Slow push-in towards subject",
                            "camera": camera_params["camera"],
                            "lens": camera_params["lens"],
                            "aperture": camera_params["aperture"]
                        }
                    ]
                }
            ]
        }

    async def generate_sound_design(
        self,
        scenes: List[Dict[str, Any]],
        instructions: List[Dict[str, Any]],
        api_key: str
    ) -> Dict[str, Any]:
        """Generate professional sound design using film audio principles"""

        # Build scenes with mood information
        scenes_data = []
        for scene in scenes:
            scene_info = {
                "id": scene.get("id", scene.get("scene_number", 1)),
                "description": scene.get("description", ""),
                "mood": scene.get("mood", ""),
                "duration": scene.get("duration", 10),
                "actions": scene.get("actions", [])
            }
            scenes_data.append(scene_info)

        prompt = f"""You are a professional sound designer and supervising sound editor. Create cinematic audio design for these scenes.

SCENES:
{json.dumps(scenes_data, indent=2)}

SOUND DESIGN PRINCIPLES:
- MUSIC EMOTIONAL ARC: Match music energy to scene emotional journey
- SONIC MOTIFS: Recurring themes for characters/ideas
- PACING SYNC: Music rhythm should match visual cutting rhythm
- SOUND BRIDGES: Use ambiences and SFX to smooth transitions
- DYNAMIC RANGE: Use quiet-to-loud contrast for impact
- FREQUENCY SPECTRUM: Balance bass, mids, and highs for clarity

For EACH scene, provide:

1. MUSIC COMPOSITION:
- Style: Specific genre (e.g., "dark cinematic orchestral with electronic elements")
- Tempo: BPM with pacing note
- Instruments: Detailed instrumentation (specific instruments, not just "strings")
- Energy level: 1-10 with emotional justification
- Arc: How music evolves during the scene
- Fade in/out: Precise timing
- Reference: Similar music for search (e.g., "Hans Zimmer Dunkirk style")

2. SOUND EFFECTS (layered, specific):
- Timestamp: Exact moment
- Sound type: Specific, descriptive (e.g., "metallic sword hiss, magical resonance")
- Duration: Precise length
- Volume: With context (e.g., "low under dialogue")
- Variation: Performance note (e.g., "slow release, trailing tail")
- Layering: What sounds work together

3. AMBIENCE/BED:
- Base: Environmental description
- Elements: 3-5 specific sounds
- Intensity: Low/Medium/High with purpose
- Stereo placement: Where in the mix

4. AUDIO CUES (transitional):
- Timestamp: Exact moment
- Type: fade_in, fade_out, transition_hit, accent, stinger, swell
- Description: What this accomplishes narratively

Return ONLY valid JSON:
{{
  "audio_design": [
    {{
      "scene_id": 1,
      "scene_duration": 10,
      "music": {{
        "style": "dark cinematic orchestral with deep synth bass",
        "tempo_bpm": 80,
        "instruments": ["solo cello melody", "low drones", "subtle percussion", "swelling strings"],
        "energy_level": 4,
        "arc": "starts quiet, builds to crest at 7s, fades to ambient",
        "fade_in": "0-2s from silence",
        "fade_out": "8-10s trailing dissonance",
        "search_prompts": ["cinematic tension underscore", "mystery drone ambient"]
      }},
      "sound_effects": [
        {{
          "timestamp": "0:00",
          "sound_type": "slow metallic resonance, magical sword awakening",
          "duration": "3s",
          "volume": "medium, building",
          "variation": "low frequency pulse with high frequency overtones"
        }}
      ],
      "ambience": {{
        "base": "ancient stone cave sub-bass with distant water drip",
        "elements": ["low 40Hz rumble", "occasional water drops (2Hz)", "subtle air movement"],
        "intensity": "low, creating unease"
      }},
      "audio_cues": [
        {{
          "timestamp": "0:00",
          "cue_type": "fade_in_music",
          "description": "Music enters with ambient drone under sword discovery"
        }}
      ]
    }}
  ],
  "overall_audio_arc": {{
    "energy_curve": "building to climax at scene 3",
    "key_moments": [{{"time": "0:00", "event": "establishing mystery", "energy": 2}}]
  }}
}}
"""

        response = await self._generate_content(prompt, api_key)

        try:
            json_match = self._extract_json(response)
            if json_match:
                return json.loads(json_match)
        except Exception as e:
            print(f"Failed to parse audio response: {e}")

        # Fallback audio design
        return {
            "audio_design": [
                {
                    "scene_id": 1,
                    "scene_duration": scenes[0].get("duration", 10),
                    "music": {
                        "style": "dark cinematic",
                        "tempo_bpm": 90,
                        "instruments": ["strings", "brass"],
                        "energy_level": 5,
                        "fade_in": "0-1s",
                        "fade_out": "-1s",
                        "search_prompts": ["cinematic tension"]
                    },
                    "sound_effects": [
                        {
                            "timestamp": "0:00",
                            "sound_type": "ambient drone",
                            "duration": "5s",
                            "volume": "low",
                            "variation": "atmospheric"
                        }
                    ],
                    "ambience": {
                        "base": scenes[0].get("mood", "dramatic") + " atmosphere",
                        "elements": [],
                        "intensity": "low"
                    },
                    "audio_cues": []
                }
            ],
            "overall_audio_arc": {
                "energy_curve": "building",
                "key_moments": []
            }
        }


# Singleton instance
llm_service = LLMService()
