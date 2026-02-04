"""
Service for interacting with LLMs (Gemini, OpenAI, and Claude)
"""

import os
import asyncio
from typing import Optional, Dict, Any, List, Literal
import google.generativeai as genai
from openai import AsyncOpenAI
import anthropic
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

    async def _generate_content_openai(self, prompt: str, api_key: str, model: str = "gpt-4o") -> str:
        """Generate content using OpenAI with specific API key"""
        try:
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional film director and cinematographer expert in scene breakdown and cinematic analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Return a fallback response if OpenAI fails
            return '{"scenes": [{"id": 1, "description": "Scene generated (API error - using fallback)", "actions": [], "duration": 10, "mood": "neutral"}]}'

    async def _generate_content_claude(self, prompt: str, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> str:
        """Generate content using Claude with specific API key"""
        try:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            response = await client.messages.create(
                model=model,
                max_tokens=8192,
                system="""You are a Hollywood-level visual effects supervisor and AI video prompt engineer with expertise in:
- Blockbuster cinematography and visual language
- Production-ready VFX breakdown and specifications
- Professional color theory and grading techniques
- AI video generation systems (Runway, Pika, Sora, Kling)
- Technical camera equipment and lens characteristics
- Sound design and audio post-production integration

Your outputs must be production-ready, specific, and technically precise. Use professional cinematography vocabulary and avoid generic descriptions.""",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API error: {e}")
            # Return a fallback response if Claude fails
            return '{"scene_prompts": [{"scene_id": 1, "image_prompts": [{"time": "0-5s", "prompt": "Cinematic scene"}]}]}'

    async def analyze_scenario(
        self,
        scenario: str,
        project_type: str,
        constraints: Dict[str, Any],
        api_key: str,
        use_openai: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze scenario and break down into scenes using cinematography principles

        Args:
            scenario: The scenario text to analyze
            project_type: Type of project (trailer, scene, etc.)
            constraints: Project constraints
            api_key: API key for the LLM service
            use_openai: If True, use OpenAI; if False, use Gemini
        """

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

        prompt = f"""You are a Hollywood-level film director and cinematographer specializing in blockbuster trailers and high-concept visual storytelling. Analyze this scenario for a {project_type}.

SCENARIO: {scenario}

PROFESSIONAL CINEMATOGRAPHY FRAMEWORK:

=== SHOT TYPES & TERMINOLOGY ===
Specify EXACT shot types for each scene:
- ESTABLISHING SHOT (СУПЕР-ТОТАЛ): Extreme wide, sets context/location
- SUPER-WIDE: Grand scale, multiple subjects/environment
- WIDE SHOT (ОБЩИЙ ПЛАН): Full body + environment
- MEDIUM SHOT (СРЕДНИЙ ПЛАН): Waist up, shows interaction
- CLOSE-UP (КРУПНЫЙ ПЛАН): Face detail, emotional intensity
- EXTREME CLOSE-UP: Eyes, mouth, specific detail
- POV (СУБЪЕКТИВНАЯ КАМЕРА): Character's perspective
- OVER-THE-SHOULDER: Conversation framing
- TRACKING SHOT: Camera follows subject movement
- CRANE SHOT: Camera rises/lowers for dramatic effect
- DOLLY: Toward (intimacy/tension) or away (reveal/distance)
- PAN: Reveals what's to the side
- TILT: Reveals above/below (power dynamics)
- HANDHELD: Documentary realism, unease
- STROBE/FLASH FRAME: Jarring cut for impact
- RACK FOCUS: Shift focus between foreground/background

=== CAMERA MOVEMENT LANGUAGE ===
- "Slow orbit" - camera circles subject
- "Track with" - follow alongside
- "Push in" - increase tension
- "Pull back" - reveal context
- "Whip pan" - sudden disorienting reveal
- "Crane up" - diminish subject power
- "Float" - dreamlike quality

=== VISUAL EFFECTS SPECIFICATIONS ===
Describe VFX with technical precision:
- GLITCH EFFECTS: "Texture z-fighting", "vertices overlapping", "shimmering existence"
- PHYSICS ANOMALIES: "Rain falling upward", "ocean frozen like glass", "smoke returning to source"
- REALITY DISTORTION: "Gel lens refraction", "chromatic aberration", "holographic interference"
- COLOR ANOMALIES: "Electric blue dome", "violet compression", "flat CGI overlay appearance"
- MATERIAL PROPERTIES: "Solid plastic water", "liquid metal", "crystalline structures"

=== TIMING & PACING ===
- FAST CUTS: Action, excitement, chaos (0.5-2 seconds per shot)
- SLOW CUTS: Contemplation, sadness, epic scale (5-15 seconds)
- STROBING: Staccato rhythm for chaos (0.3-0.5 second flashes)
- MATCH CUTS: Visual similarities between shots
- HOLD: Extended shot for tension build

=== SOUND DESIGN INTEGRATION ===
Each scene should suggest:
- DIEGETIC SOUNDS: What characters hear
- NON-DIEGETIC: Score, atmosphere
- SILENCE AS WEAPON: Create unease with absence of sound
- AUDIO TRANSITIONS: Hard cuts, crossfades, sound bridges
- SPECIFIC SFX: "Digital VZHUH (TV off)", "low frequency rumble", "piercing screech"

=== COLOR THEORY & LIGHTING ===
- THREE-POINT LIGHTING: Key, fill, back separation
- LOW KEY: High contrast shadows (mystery, tension)
- HIGH KEY: Even illumination (comedy, light mood)
- PRACTICAL LIGHTS: Lamps, windows within scene
- MOTIVATED LIGHTING: Light sources that make sense
- COLOR PALETTES:
  * TEAL & ORANGE: Classic cinematic contrast
  * MONOCHROMATIC: Unified mood (blue isolation, red danger)
  * COMPLEMENTARY: Opposite colors (tension/conflict)
  * WARM: Nostalgia, comfort
  * COOL: Detachment, sadness, mystery
  * ELECTRIC/NEON: Synthetic, artificial, futuristic
  * DESATURATED: Bleak, post-apocalyptic

=== TRANSITIONS ===
- CUT: Direct, jarring
- DISSOLVE: Passage of time
- FADE: Beginnings/endings
- WIPE: Comic book style, temporal shifts
- GLITCH CUT: Digital disruption, reality break
- HARD CUT: Sudden, shocking
- MATCH CUT: Thematic connection

CONSTRAINTS:
- Total duration: {constraints.get('total_duration', 'N/A')} seconds
- Scene count: {scene_count_target if scene_count_target else 'AI decide based on complexity (typically ' + str(constraints.get('scene_count_target', 3)) + ' scenes)'}
- Pacing approach: {pacing_guidance}

{scene_guidance}. For EACH scene, provide:

1. ID: Scene number
2. SHOT TYPE: Specific shot type (from terminology above)
3. DESCRIPTION: Cinematic description with clear visual action and emotional subtext
4. ACTIONS: 4-5 specific, visceral events using strong verbs
5. DURATION: Precise timing in seconds
6. CAMERA: Exact movement + technical approach
7. LIGHTING: Specific setup + mood
8. COLOR: Color palette + grading approach
9. VFX: Specific visual effects if any
10. SOUND: Key sound elements + transitions
11. TIMING: Timestamp (e.g., "0:00-0:15")

Think like a Hollywood director: Each scene must have:
- VISUAL IMPACT: Memorable imagery
- EMOTIONAL RESONANCE: Clear feeling
- TECHNICAL PRECISION: Shootable specs
- PACING RHYTHM: Fit within trailer structure

Return ONLY valid JSON:
{{
  "scenes": [
    {{
      "id": 1,
      "shot_type": "ESTABLISHING SHOT",
      "description": "Cinematic description with subtext and visual impact",
      "actions": ["visceral action 1", "visceral action 2", "visceral action 3", "visceral action 4"],
      "duration": 15,
      "camera": "Slow orbit followed by tracking shot",
      "lighting": "Low key blue rim light with deep shadows",
      "color": "Monochromatic blue with electric blue accents",
      "vfx": "Glitch effects on edges, chromatic aberration",
      "sound": "Low frequency build to sharp digital cutoff",
      "timing": "0:00-0:15"
    }}
  ],
  "total_duration": {constraints.get('total_duration', 30)},
  "pacing_notes": "Brief pacing description for overall trailer"
}}
"""

        response = await self._generate_content_openai(prompt, api_key) if use_openai else await self._generate_content(prompt, api_key)

        # Try to parse JSON from the response
        try:
            # Find JSON in the response
            json_match = self._extract_json(response)
            if json_match:
                data = json.loads(json_match)
                return data
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")

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

        prompt = f"""You are a Hollywood casting director working on a blockbuster production. Assign the PERFECT celebrity/character matches to each scene based on:
1. Scene mood and emotional requirements
2. Character archetypes and star power
3. Visual storytelling impact
4. Narrative coherence and character consistency

AVAILABLE CELEBRITIES/CHARACTERS:
{chr(10).join(char_descriptions)}

CHARACTERS THAT MUST BE INCLUDED: {must_include_str}

SCENES TO CAST:
{chr(10).join(scene_descriptions)}

=== CASTING DIRECTOR FRAMEWORK ===

CASTING PRINCIPLES:
- STAR POWER: Recognizable faces create instant audience connection
- ARCHETYPE MATCHING: Cast against type or deliberately subvert it
- VISURAL DIVERSITY: Mix of ages, ethnicities, body types for visual interest
- EMOTIONAL RANGE: Can the actor convey the required emotion?
- ACTION CAPABILITY: For stunts, fight scenes, physical performance
- SCENE CHEMISTRY: How characters interact visually

CHARACTER EXPRESSION DIRECTION:
For each character in each scene, specify:
- EYES: The window to emotion - focus, direction, pupils, lids, tears
- SUBTEXT: What they're really feeling vs. what they show
- MICRO-EXPRESSIONS: Brief flashes of true emotion
- STILLNESS POWER: When lack of movement is more powerful
- REACTION SHOTS: How they respond to other characters/events

POSE & BODY LANGUAGE:
- STANCE: Confident (square shoulders), uncertain (hunched), guarded (closed off)
- HANDS: What they do with hands (fidget, clench, hide, expressive)
- BREATHING: Heavy (exertion/anxiety), shallow (fear/controlled), held (tension)
- WEIGHT: How gravity affects them (light/airy, heavy/grounded, dragging)
- ORIENTATION: Open to world, closed off, turned away/away

ACTION SPECIFICS:
- VERBS: Use strong, specific action verbs (not generic "walks", "looks")
- TIMING: When the action occurs within the scene
- MOTIVATION: Why they're doing this (conscious and unconscious)
- OBSTACLES: What's preventing them from getting what they want

COSTUME & APPEARANCE CONSISTENCY:
- BASE LOOK: Core costume elements that identify the character
- EVOLUTION: How costume changes/appears across scenes (damage, dirt, changes)
- CONTINUITY: Elements that must remain consistent
- SCENE-SPECIFIC: Weathering, accessories appropriate to each scene

CASTING DECISIONS:
For each scene, assign 0-3 characters based on:
- DRAMATIC FUNCTION: What role does this character serve in the story beat?
- VISUAL COMPOSITION: How do they fit the frame and lighting?
- PACING: More characters = slower, fewer = more intimate
- POWER DYNAMICS: Who has agency in this scene?

For each character assignment, provide:
- name: Celebrity/character name
- shot_type: How to frame them (CLOSE-UP, MEDIUM, WIDE)
- expression: Specific eye/mouth/facial direction (e.g., "eyes narrow in calculation, mouth slight smile")
- pose: Body language with specific stance (e.g., "warrior stance - feet shoulder-width, knees bent, weight forward")
- action: Precise action verb + object/context (e.g., "drawing sword from scabbard slowly, blade catching light")
- micro_expression: Subtle detail (e.g., "left eye twitches - concealed fear")
- subtext: What they're really feeling (e.g., "confident exterior hiding terror")
- costume_notes: Appearance details (e.g., "battle-worn armor with fresh slash marks on chest piece")
- continuity: What must match other appearances (e.g., "same red cape as scene 1, now torn at hem")

CONSISTENCY MAP tracks:
- base_appearance: Core visual signature
- costume_progression: How look evolves
- emotional_arc: Character's journey
- scenes_appearing: Where they appear

Return ONLY valid JSON:
{{
  "assignments": [
    {{
      "scene_id": 1,
      "cast_reasoning": "This scene requires [X] to create [emotional effect]",
      "characters": [
        {{
          "name": "CharacterName",
          "shot_type": "CLOSE-UP (eyes)",
          "expression": "eyes wide with terror, pupils pinpricks, mouth slightly open",
          "pose": "crouched low, hands protecting head, shoulders up to ears",
          "action": "scanning horizon frantically, head whipping left-right",
          "micro_expression": "lower lip trembles for 0.5s - suppressed panic",
          "subtext": "trying to maintain soldier composure while internally terrified",
          "costume_notes": "tactical gear dust-covered, fresh scratch on left cheekpiece",
          "lighting_note": "harsh side lighting creates deep shadow across face - half in shadow"
        }}
      ]
    }}
  ],
  "consistency_map": {{
    "CharacterName": {{
      "base_appearance": "battle-worn soldier with tousled dark hair and haunted eyes",
      "costume_progression": "Scene 1: Clean uniform → Scene 3: Dusty, torn at collar → Scene 5: Bloodied",
      "emotional_arc": "Confident → Terrified → Desperate → Resigned",
      "scenes_appearing": [1, 3, 5],
      "recognizable_features": ["small scar above right eyebrow", "worn leather boots"]
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
        api_key: str,
        use_claude: bool = False
    ) -> Dict[str, Any]:
        """
        Generate professional image and video prompts using cinematography principles

        Args:
            use_claude: If True, use Claude; if False, use Gemini
        """

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

        prompt = f"""You are a Hollywood visual effects supervisor and AI video prompt engineer. Generate production-ready prompts for AI video generation systems (Runway, Pika, Sora, Kling).

SCENES TO GENERATE PROMPTS FOR:
{json.dumps(scenes_data, indent=2)}

=== IMAGE PROMPT SPECIFICATIONS ===

For EACH scene, generate 1-2 detailed image prompts with:

TECHNICAL LAYER:
- Resolution: "8K", "16K", or "IMAX quality" for cinematic scope
- Style: "Photorealistic", "Hyperrealistic", or "CGI feature film quality"
- Render: "Ray-traced", "Path-traced", "Volumetric rendering"
- Color Space: "ACES", "Rec.2020", "DCI-P3"

CAMERA SPECS:
- Camera: Specify from [RED V-Raptor 8K, Sony Venice 2, ARRI Alexa 35, ARRI Alexa 65, IMAX MSM II]
- Lens: Specify from [Panavision Ultra Speed, Panavision C-Series, ARRI Signature Prime, Cooke S4, Zeiss Supreme, Angénieux Optimo]
- Focal Length: [8mm ultra-wide, 14mm wide, 35mm normal, 50mm normal, 85mm portrait, 135mm telephoto]
- Aperture: [f/1.2 ultra-shallow DOF, f/2.8 shallow DOF, f/4 medium DOF, f/11 deep focus]
- Format: [2.39:1 anamorphic, 16:9, 2.35:1, IMAX 1.43:1]

SUBJECT DESCRIPTION:
- Primary subject with specific details (clothing, expression, pose, action)
- Secondary elements (background, supporting characters, environmental details)
- Textures and materials (fabric types, metal finishes, skin quality)
- Scale indicators (for depth perception)

LIGHTING SPECIFICATION:
- Type: [Three-point, Natural light, Practical only, Motivated, Mixed]
- Key Light: Source type, position, intensity, color temperature
- Fill Light: Softness ratio, color tint (if any)
- Back Light: Separation, rim effect, kickers
- Special: [Volumetric fog, God rays, Lens flares, Caustics, Bioluminescence]

COLOR GRADING:
- Primary Palette: [Teal/Orange, Monochromatic blue, Desaturated war grade, Electric neon, Warm gold]
- Secondary Color: Accent color for visual interest
- Contrast: [Low key moody, High key bright, Crushing blacks, Blown highlights for effect]
- Saturation: [Desaturated bleak, Oversaturated surreal, Natural, Selective color]
- Treatment: [Bleach bypass, Day for night, Cross-processed, Color flash]

VFX & POST:
- Visual effects: [Glitch artifacts, Chromatic aberration, Lens distortion, Motion blur, Particle systems]
- Atmosphere: [Fog, Smoke, Dust motes, Rain, Snow, Debris]
- Quality enhancers: [Subsurface scattering, Ambient occlusion, Global illumination]

COMPOSITION:
- Rule: [Rule of thirds, Center frame dominance, Golden ratio, Symmetric balance]
- Depth: [Foreground elements, Multiple planes, Shallow focus, Deep focus]
- Framing: [Tight, Loose, Dutch angle, Canted frame, Foreground obstruction]
- Negative space: Use for isolation, emptiness, anticipation

NEGATIVE PROMPT:
Technical: blurry, low quality, low resolution, pixelated, artifacts, compression, distorted
Aesthetic: cartoon, anime, illustration, painting, drawing, sketch, 3D render, plastic, wax
Lighting: flat lighting, even lighting, overexposed, underexposed, harsh shadows without purpose

=== VIDEO PROMPT SPECIFICATIONS ===

For EACH scene, generate 1-2 video prompts with:

CAMERA MOVEMENT:
- Type: [Static, Dolly in/out, Tracking, Crane up/down, Pan, Tilt, Whip pan, Handheld, Gimbal, FPV drone]
- Speed: [Imperceptible slow, Slow push, Medium pace, Fast push, Whip rapid]
- Acceleration: [Constant, Ease-in, Ease-out, Ease-in-out, Jerky/staccato]
- Duration: Exact length in seconds

SUBJECT ACTION:
- Primary action: What main subject does (specific verbs)
- Secondary action: Background/environmental movement
- Reaction: How subject responds or changes
- Timing: When actions occur within the shot

CAMERA OPERAUTION:
- Focus pulls: [Single rack, Multiple racks, Follow focus, Rack focus during action]
- Exposure: [Consistent, Changing during shot, Exposure compensation]
- White balance: [Consistent, Shift for effect]
- Frame rate: [24fps cinematic, 48fps slow-mo, 60fps action, 120fps ultra slow-mo]

TECHNICAL:
- Motion blur: [Natural 24°, Reduced for staccato, Excessive for dreamlike]
- Shutter angle: [180° normal, 90° reduced, 45° staccato, 360° motion blur heavy]
- Stabilization: [Tripod locked, Gimbal smooth, Handheld organic, Intentional shake]

TRANSITIONS:
- In: [Cut in, Dissolve, Fade in, Wipe, Glitch cut, Flash frame]
- Out: [Cut out, Dissolve, Fade out, Wipe, Glitch cut, Flash frame]
- Bridge: [Sound bridge, Visual match, Color grade match, Action match]

TIMELINE INTEGRATION:
- Timecode: Exact position in overall sequence (e.g., "0:15-0:20")
- Rhythm: How this fits in overall pacing (build, release, pause)

Return ONLY valid JSON:
{{
  "scene_prompts": [
    {{
      "scene_id": 1,
      "image_prompts": [
        {{
          "time": "0-5s",
          "prompt": "[Full detailed prompt with all specifications]",
          "negative_prompt": "[Negative prompt]",
          "technical_specs": {{
            "camera": "ARRI Alexa 35",
            "lens": "Panavision C-Series 50mm",
            "focal_length": "50mm",
            "aperture": "f/2.8",
            "format": "2.39:1"
          }},
          "lighting": "Three-point with warm key (3200K) and cool fill (5600K)",
          "color_grade": "Teal shadows with warm skin tones, crushing blacks",
          "vfx": "Subtle chromatic aberration in highlights, volumetric fog",
          "composition": "Rule of thirds, shallow depth of field"
        }}
      ],
      "video_prompts": [
        {{
          "time": "0-5s",
          "prompt": "Slow dolly in toward subject while camera floats upward (compound movement)",
          "camera_movement": "Dolly in + Crane up",
          "speed": "Very slow push (5 seconds to move 2 meters)",
          "subject_action": "Main subject turns slowly toward camera with micro-expressions changing",
          "focus": "Single rack focus from background to subject's eyes",
          "motion_blur": "Natural 24° shutter at 24fps",
          "duration": "5 seconds",
          "transition_out": "Cut to next scene",
          "technical": {{
            "camera": "ARRI Alexa 35",
            "lens": "Panavision C-Series 50mm",
            "stabilization": "Gimbal smooth"
          }}
        }}
      ]
    }}
  ]
}}
"""

        response = await self._generate_content_claude(prompt, api_key) if use_claude else await self._generate_content(prompt, api_key)

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
        """Generate simple sound suggestions for scenes"""

        # Build scenes with mood information
        scenes_data = []
        for scene in scenes:
            scene_info = {
                "id": scene.get("id", scene.get("scene_number", 1)),
                "description": scene.get("description", ""),
                "mood": scene.get("mood", ""),
                "duration": scene.get("duration", 10)
            }
            scenes_data.append(scene_info)

        prompt = f"""You are a Hollywood supervising sound editor and Foley artist. Create professional sound design for these scenes.

SCENES:
{json.dumps(scenes_data, indent=2)}

=== PROFESSIONAL SOUND DESIGN FRAMEWORK ===

For EACH scene, provide:

1. TIMELINE BREAKDOWN:
   - Exact timestamps for key audio events
   - Duration of each sound element
   - Fade in/out timing (e.g., "0:00-0:02 from silence")

2. MUSIC COMPOSITION:
   - Style: Specific genre (e.g., "glitch electronic + orchestral dissonance", "minimalist horror synth", "epic orchestral with choir")
   - Tempo: Exact BPM with pacing notes
   - Instruments: Detailed instrumentation (specific instruments, not generic "strings")
   - Key/Scale: Musical key for emotional effect (e.g., "D minor for tension", "E major for resolution")
   - Energy level: 1-10 scale with emotional justification
   - Arc: How music evolves during the scene (e.g., "starts at 60 BPM, stutters to 0, resumes at 120 BPM")
   - Layering: What instruments play when
   - Reference: Similar music for search (e.g., "Hans Zimmer Dunkirk", "Johann Johannsson Arrival", "Aphex Twin Windowlicker")

3. SOUND EFFECTS (SPECIFIC & LAYERED):
   For each SFX, provide:
   - Timestamp: Exact moment (e.g., "0:02:150")
   - Sound type: Specific, descriptive (e.g., "digital VZHUH like old TV turning off", "low frequency oscillator sweep 20-80Hz")
   - Duration: Precise length (e.g., "0.5s sharp burst")
   - Frequency: Low (20-200Hz), Mid (200-2000Hz), High (2kHz+), Full spectrum
   - Volume: With context (e.g., "low under dialogue", "medium building", "hard hit at -3dB")
   - Layering: What sounds work together
   - Variation: Performance note (e.g., "slow release with trailing tail", "sharp attack with immediate cutoff")
   - Processing: Effects applied (reverb, delay, distortion, filter)

4. DIEGETIC SOUND (What characters hear):
   - On-screen actions: Foley for what's visible
   - Off-screen: Sounds from outside frame but within scene
   - Room tone: Base ambient of the space

5. NON-DIEGETIC SOUND (Score/atmosphere):
   - Music underscore
   - Atmosphere/Bed: Environmental base
   - Synthetic elements: Electronic/atmospheric

6. SILENCE AS WEAPON:
   - When absence of sound creates tension
   - Duration of silence before/after key moments
   - What returns to break the silence

7. AUDIO CUES (Transitional):
   - Timestamp: Exact moment
   - Type: fade_in_music, fade_out_music, transition_hit, accent, stinger, swell, cutoff
   - Description: What this accomplishes narratively

8. STEREO FIELD:
   - Placement: Center, L/R, Surround, Height (Atmos)
   - Movement: Static, Pan, Sweep

9. FREQUENCY SPECTRUM:
   - Low (20-200Hz): Sub, impact, rumble
   - Low-Mid (200-500Hz): Warmth, body
   - Mid (500-2kHz): Intelligibility, presence
   - High-Mid (2kHz-6kHz): Definition, attack
   - High (6kHz-20kHz): Air, sparkle, sibilance

Return ONLY valid JSON:
{{
  "sound_design": [
    {{
      "scene_id": 1,
      "timeline": {{
        "duration": 10,
        "key_moments": [
          {{"time": "0:00", "event": "Silence begins", "type": "silence"}},
          {{"time": "0:02", "event": "Digital glitch sound", "type": "sfx"}},
          {{"time": "0:05", "event": "Music enters", "type": "music_in"}}
        ]
      }},
      "music": {{
        "style": "Glitch electronic + orchestral dissonance",
        "tempo_bpm": 60,
        "key_scale": "D minor",
        "instruments": ["synth bass (distorted)", "low frequency oscillator", "detuned strings", "digital artifact samples", "sub-bass drops"],
        "energy_level": 3,
        "energy_arc": "starts sparse, glitches at 0:05, builds to 7/10 at 0:08, sudden cutoff at 0:09",
        "layering": "Bass and drone constant, glitches layer in mid-scene, strings swell toward end",
        "fade_in": "0:05-0:07 gradual from silence",
        "fade_out": "hard cutoff at 0:09 with digital artifact tail",
        "reference": ["Hans Zimmer Dunkirk build", "Aphex Twin Windowlicker glitch elements"]
      }},
      "sound_effects": [
        {{
          "timestamp": "0:02.150",
          "sound_type": "Digital VZHUH - like old TV power off, sharp and sudden",
          "duration": "0.15s",
          "frequency": "Full spectrum with emphasis on 2-8kHz",
          "volume": "Medium-hard (-6dB)",
          "variation": "Immediate attack, zero decay, hard cutoff",
          "layering": "Plays in isolation with surrounding silence"
        }},
        {{
          "timestamp": "0:05.000",
          "sound_type": "Low frequency oscillator sweep, 20Hz to 80Hz over 2 seconds",
          "duration": "2s",
          "frequency": "Sub-bass (20-80Hz)",
          "volume": "Building from -30dB to -12dB",
          "variation": "Slow sweep with slight distortion"
        }}
      ],
      "ambience": {{
        "base": "Absolute silence - no room tone (creates unease/vacuum)",
        "elements": ["no ambient until 0:05", "digital hum (rare) after music starts"],
        "intensity": "Low (creates vacuum of sound)",
        "stereo": "Center (monophonic unease)"
      }},
      "audio_cues": [
        {{
          "timestamp": "0:05",
          "cue_type": "music_entry",
          "description": "Music enters abruptly after silence, breaking the vacuum"
        }},
        {{
          "timestamp": "0:09",
          "cue_type": "hard_cutoff",
          "description": "All sound cuts to silence for impact into next scene"
        }}
      ]
    }}
  ],
  "overall_audio_arc": {{
    "energy_curve": "Builds through scenes 1-3, drops at scene 4, builds to climax at scene 5",
    "key_moments": [
      {{"time": "0:00", "scene": 1, "event": "Silence establishes unease", "energy": 0}},
      {{"time": "0:15", "scene": 2, "event": "Glitch dome appears", "energy": 8}},
      {{"time": "0:45", "scene": 4, "event": "Time periods merge", "energy": 10}}
    ],
    "themes": ["Isolation", "Technology failure", "Time collapse", "Primal vs Modern conflict"]
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

        # Fallback
        return {
            "sound_suggestions": [
                {
                    "scene_id": 1,
                    "music": "cinematic tension",
                    "sound_effects": ["ambient drone"],
                    "ambience": "atmospheric"
                }
            ]
        }


# Singleton instance
llm_service = LLMService()
