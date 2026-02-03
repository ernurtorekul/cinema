# AI Video Generation Platform - Technical Breakdown

## Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (async web framework)
- **Task Queue**: Celery + Redis (async job processing)
- **AI/LLM**: Google Generative AI (Gemini Free API) via LangChain
- **Database**: Supabase (PostgreSQL) + supabase-py
- **File Storage**: Supabase Storage

### File Processing
- **PDF Parsing**: PyPDF2, pdfplumber
- **Document Parsing**: unstructured.io (multi-format support)

### Video/Image Processing (Montage Agent)
- **Python**: OpenCV, MoviePy, FFmpeg-python

### Audio Processing (Sound Design Agent)
- **Analysis**: librosa, pydub (audio analysis)
- **Generation/Integration**: ElevenLabs API (SFX), Suno AI/Udio API (music)

### Frontend
- **Framework**: Next.js 14 (React Server Components)
- **UI**: shadcn/ui + Tailwind CSS
- **State**: Zustand
- **Forms**: React Hook Form + Zod validation

### DevOps
- **Containerization**: Docker + Docker Compose
- **Process Management**: supervisord (production)
- **Monitoring**: Sentry (error tracking), Prometheus + Grafana (metrics)

---

## Complete Flow Breakdown

### FLOW 0: Project Initialization

**Input**: User starts application

**Process**:
1. Frontend displays project type selection
2. User selects: trailer / commercial / short film / TikTok / custom
3. User defines constraints:
   - Total duration
   - Scene count target
   - Style preferences
   - Pacing (fast/slow/mixed)

**Output**: Project configuration object

**Tech**:
- Frontend: Next.js form with Zod schema validation
- Backend: POST /api/projects/create
- Database: Projects table stores config

---

### FLOW 1: Scenario Input

**Input**: User submits scenario text

**Example Input**:
```
"A hero sneaks into the villain's lair and discovers a glowing artifact."
```

**Process**:
1. Frontend validates scenario text length (min 10, max 5000 chars)
2. Send to backend: POST /api/projects/{id}/scenario
3. Backend stores scenario in database
4. Trigger Scenario Analysis Agent

**Output**: Stored scenario + agent trigger

**Tech**:
- Frontend: React Hook Form with real-time validation
- Backend: FastAPI endpoint, SQLAlchemy insert
- Queue: Celery task triggers agent chain

---

### FLOW 2: Scenario Analysis Agent

**Input**:
- Scenario text
- Project configuration (type, constraints)

**Process**:
1. **LLM Call**: Send scenario + project type to Gemini via LangChain
2. **Prompt Template**:
   ```
   Analyze this scenario for a {project_type}:
   {scenario_text}

   Break down into scenes. Each scene needs:
   - Scene number
   - Description
   - Key actions
   - Suggested duration (seconds)
   - Mood/tone
   - Suggested enhancements (optional)
   ```
3. Parse LLM response into structured JSON
4. Validate scene breakdown against project constraints
5. Store in database

**Output Structure**:
```json
{
  "scenes": [
    {
      "id": 1,
      "description": "Hero approaches villain's lair entrance",
      "actions": ["sneaking", "looking around", "opening door"],
      "duration": 5,
      "mood": "tense, mysterious",
      "enhancements": ["low lighting", "fog effect"]
    }
  ],
  "total_duration": 15,
  "suggestions": ["Consider adding establishing shot"]
}
```

**Tech**:
- LangChain: ChatPromptTemplate, StructuredOutputParser
- Gemini: `gemini-pro` (free tier)
- Pydantic: Output validation models

---

### FLOW 3: Character Analysis Agent

**Input**:
- Scene breakdown (from Flow 2)
- Character database TXT file
- Project configuration

**Character Database Format** (TXT):
```
CHARACTER: Hero
NAME: Alex
TRAITS: brave, determined, athletic
STYLE: tactical gear, dark colors
EXPRESSIONS: focused, intense
POSES: crouching, running, ready stance

CHARACTER: Villain
NAME: Shadow
TRAITS: mysterious, powerful, menacing
STYLE: flowing dark robes, glowing eyes
EXPRESSIONS: sinister, calm
POSES: standing tall, gesturing
```

**Process**:
1. **Parse Character DB**: Read TXT, extract character profiles
2. **LLM Call**: Match characters to scene roles
3. **Prompt Template**:
   ```
   Given these scenes: {scenes}

   And these characters: {characters}

   Assign characters to each scene. For each assignment:
   - Which character appears
   - Their expression
   - Their pose
   - Their action
   - Costume notes
   ```
4. Build character consistency map (tracks character across scenes)
5. Store assignments in database

**Output Structure**:
```json
{
  "assignments": [
    {
      "scene_id": 1,
      "characters": [
        {
          "name": "Alex",
          "expression": "focused, wary",
          "pose": "crouching behind cover",
          "action": "scanning area",
          "costume": "tactical gear, night vision"
        }
      ]
    }
  ],
  "consistency_map": {
    "Alex": {
      "base_traits": ["brave", "determined"],
      "costume": "tactical gear",
      "appearances": [1, 2, 3]
    }
  }
}
```

**Tech**:
- File parsing: Python built-in txt parsing
- LangChain: FewShotPromptTemplate for consistent matching
- Database: Junction table for scene_character relationships

---

### FLOW 4: Source Material Agent

**Input**:
- Scene breakdown (from Flow 2)
- Source files (PDF, TXT) with production rules

**Source Material Format** (PDF/TXT):
```
CINEMATOGRAPHY RULES

- Scene 1: Use wide establishing shot
- Tension scenes: Low angle, slow push-in
- Discovery moments: Close-up, rack focus
- Action: Handheld, quick cuts

TRANSITIONS
- Scene change: Dissolve for time passage
- Action to calm: Hard cut
- Build tension: Cross-dissolve

LIGHTING
- Night scenes: Blue tint, low key
- Villain lair: Green/red accent lights
```

**Process**:
1. **Parse Source Files**:
   - PDF: PyPDF2/pdfplumber extraction
   - TXT: Direct text reading
2. **Chunk & Index**: Split content into rules by category
3. **LLM Call**: Map rules to each scene
4. **Prompt Template**:
   ```
   Scene: {scene_description}

   Production Rules: {relevant_rules}

   Provide second-by-second breakdown:
   - Camera angle/movement
   - Transition in/out
   - Lighting notes
   - Visual style cues
   ```
5. Store scene instructions in database

**Output Structure**:
```json
{
  "scene_instructions": [
    {
      "scene_id": 1,
      "breakdown": [
        {
          "time": "0-2s",
          "camera": "Wide shot, slow push-in",
          "lighting": "Low key, blue moonlight",
          "action": "Alex emerges from shadows"
        },
        {
          "time": "2-5s",
          "camera": "Medium shot, handheld",
          "lighting": "Same, with green glow ahead",
          "action": "Alex spots entrance"
        }
      ],
      "transition_in": "fade from black",
      "transition_out": "cut to scene 2"
    }
  ]
}
```

**Tech**:
- PDF parsing: pdfplumber (better table extraction)
- Text processing: regex, NLTK for rule extraction
- RAG: ChromaDB vector store for rule retrieval
- LangChain: RetrievalQA chain

---

### FLOW 5: Prompt Generation Agent

**Input**:
- Scene breakdown (Flow 2)
- Character assignments (Flow 3)
- Scene instructions (Flow 4)
- Style guide (JSON/TXT)

**Style Guide Format**:
```json
{
  "visual_style": "cinematic, dark, atmospheric",
  "color_grading": "teal and orange, high contrast",
  "base_prompts": {
    "quality": "8K, ultra detailed, photorealistic",
    "lighting": "dramatic lighting, volumetric fog"
  }
}
```

**Process**:
1. **Aggregate Data**: Combine all scene data
2. **Camera Parameter Selection**: Random/select from provided options
3. **Generate Image Prompts**: For backgrounds, characters, keyframes
4. **Generate Video Prompts**: For motion, camera, transitions
5. **Optimize for Gemini**: Ensure token limits, clear instructions

**Camera Parameters**:
```
Camera: RED V-Raptor, Sony Venice, ARRI Alexa 35, etc.
Lens: Cooke S4, ARRI Signature Prime, Zeiss Ultra Prime, etc.
Focal Length: 8mm, 14mm, 35mm, 50mm
Aperture: f/1.4, f/4, f/11
```

**Prompt Template**:
```
Generate prompts for scene {scene_id}:

Scene: {description}
Characters: {characters}
Instructions: {instructions}

IMAGE PROMPT for {time_range}:
{base_style}
Camera: {camera} with {lens} at {focal_length}, f/{aperture}
Action: {action}
Lighting: {lighting}
Color: {color_scheme}

VIDEO PROMPT for {time_range}:
Camera movement: {movement}
Subject action: {action}
Transition: {transition}
Duration: {duration}s
```

**Output Structure**:
```json
{
  "scene_prompts": [
    {
      "scene_id": 1,
      "image_prompts": [
        {
          "time": "0-2s",
          "prompt": "8K cinematic shot, hero crouching in shadows, tactical gear, intense expression, RED V-Raptor with Cooke S4 35mm f/1.4, teal and orange grading, volumetric fog, dramatic lighting",
          "negative_prompt": "blurry, low quality, cartoon"
        }
      ],
      "video_prompts": [
        {
          "time": "0-5s",
          "prompt": "Slow push-in towards hero, camera pans right as they look towards lair entrance, handheld subtle movement, 5 seconds",
          "camera": "RED V-Raptor",
          "lens": "Cooke S4 35mm",
          "aperture": "f/1.4"
        }
      ]
    }
  ]
}
```

**Tech**:
- LangChain: Custom prompt chains
- Template engine: Jinja2 for prompt generation
- Validation: Pydantic models for output structure

---

### FLOW 6: Montage Agent (Optional)

**Input**:
- Generated image/video files (from external AI generator)
- Scene timing breakdown
- Transition instructions

**Process**:
1. **Load Media**: Read generated images/videos
2. **Sequence Builder**: Order by scene timing
3. **Apply Transitions**: Use FFmpeg for fades, cuts, dissolves
4. **Add Overlays**: Optional text, watermark
5. **Render Output**: Export video file

**FFmpeg Operations**:
```
- Concatenate clips: concat filter
- Transitions: xfade filter (fade, dissolve, wipe)
- Text overlays: drawtext filter
- Audio: amerge for soundtrack
```

**Output Structure**:
```json
{
  "output_file": "draft_video.mp4",
  "duration": 15,
  "resolution": "1920x1080",
  "fps": 24,
  "scenes": [
    {"start": 0, "end": 5, "file": "scene_1.mp4"},
    {"start": 5, "end": 10, "file": "scene_2.mp4"}
  ]
}
```

**Tech**:
- FFmpeg-python: Python wrapper for FFmpeg
- MoviePy: Higher-level video editing
- OpenCV: Image sequence processing

---

### FLOW 7: Sound Design Agent

**Input**:
- Complete scene breakdown (Flow 2)
- Scene instructions (Flow 4)
- All generated prompts (Flow 5)
- Video timing/montage data (Flow 6, if available)

**Process**:
1. **Analyze Scene Context**: For each scene, extract:
   - Mood/tone
   - Action intensity
   - Pacing (fast/slow)
   - Transition types
   - Visual cues

2. **LLM Call for Audio Analysis**: Generate audio recommendations
3. **Prompt Template**:
   ```
   Analyze this scene for audio design:

   Scene: {description}
   Duration: {duration}s
   Mood: {mood}
   Actions: {actions}
   Timing breakdown: {second_by_second}

   Provide audio recommendations:

   1. BACKGROUND MUSIC:
   - Genre/style (e.g., "orchestral tension", "electronic suspense")
   - Tempo (BPM)
   - Instrument suggestions
   - Key (if applicable)
   - Energy level (1-10)
   - Fade in/out timing

   2. SOUND EFFECTS (per timestamp):
   - Timestamp (0:00, 0:02, etc.)
   - Sound type (footsteps, door creak, whoosh, impact, etc.)
   - Duration
   - Volume level
   - Layering suggestions

   3. AMBIENCE:
   - Base atmosphere (wind, city hum, forest, etc.)
   - Intensity level

   4. AUDIO CUES:
   - Transition sounds (whoosh, riser, impact)
   - Accent hits for dramatic moments
   ```

4. **Validate Timing**: Ensure audio cues align with scene timestamps
5. **Store audio recommendations in database**

**Output Structure**:
```json
{
  "audio_design": [
    {
      "scene_id": 1,
      "scene_duration": 5,
      "music": {
        "style": "dark cinematic orchestral",
        "tempo_bpm": 90,
        "instruments": ["deep strings", "low brass", "timpani", "synth pads"],
        "energy_level": 4,
        "fade_in": "0-1s",
        "fade_out": "4-5s",
        "search_prompts": [
          "cinematic tension underscore dark",
          "suspenseful orchestral buildup"
        ]
      },
      "sound_effects": [
        {
          "timestamp": "0:00",
          "sound": "footsteps on gravel",
          "duration": "2s",
          "volume": "low",
          "variation": "slow, deliberate"
        },
        {
          "timestamp": "0:02",
          "sound": "metal door creak",
          "duration": "1.5s",
          "volume": "medium",
          "variation": "slow, high pitched"
        },
        {
          "timestamp": "0:04",
          "sound": "low rumble",
          "duration": "1s",
          "volume": "subtle",
          "variation": "distant, ominous"
        }
      ],
      "ambience": {
        "base": "night forest ambience",
        "elements": ["crickets", "distant owl", "wind through trees"],
        "intensity": "low"
      },
      "audio_cues": [
        {
          "timestamp": "0:00",
          "type": "fade_in_music",
          "description": "Music starts from silence"
        },
        {
          "timestamp": "0:04",
          "type": "transition_hit",
          "description": "Subtle bass hit for scene transition"
        }
      ]
    }
  ],
  "overall_audio_arc": {
    "energy_curve": "building_tension",
    "key_moments": [
      {"time": "0:00", "event": "scene_start", "energy": 3},
      {"time": "0:12", "event": "discovery", "energy": 7},
      {"time": "0:15", "event": "climax", "energy": 9}
    ]
  }
}
```

**Sound Effect Categories**:
```
Movement: footsteps, clothing rustle, breathing, equipment rattle
Environment: wind, rain, fire, water, machinery
Impact: punch, hit, slam, crash, explosion
Whoosh/Riser: transition, reveal, speed up
Magical/SF: glow, hum, power up, teleport
Doors/Objects: creak, slam, click, unlock
Vocal: grunt, scream, gasp, whisper
```

**Music Style Mapping by Mood**:
```
Tense/Suspense: dark orchestral, minimal synth, pulse bass
Action: fast percussion, brass, electronic beats
Emotional: piano, strings, ambient pads
Mystery: ethereal, arpeggiated, subtle textures
Horror: dissonant, low drones, sudden stingers
Epic: full orchestra, choir, driving rhythm
Calm: ambient, nature sounds, soft piano
```

**Tech**:
- LangChain: Structured output for audio timing
- Audio analysis: librosa (optional, for analyzing reference tracks)
- API integration: ElevenLabs for SFX generation, Suno/Udio for music
- Database: New tables for audio_design and sound_effects
- FFmpeg: Audio track synchronization (for montage)

**Audio Timeline CSV Output Format**:
```csv
Scene,Time,Type,Item,Description,Duration,Volume,Notes
1,0:00,Music,Intro,Dark orchestral swell,5s,low,Fade in from silence
1,0:00,SFX,Footsteps,Slow deliberate steps on gravel,2s,low,Right to left pan
1,0:02,SFX,Door creak,Metal door slowly opening,1.5s,medium,High pitched
1,0:04,SFX,Rumble,Low distant rumble,1s,subtle,Ominous build
1,0:04,Cue,Transition,Bass hit for scene change,0.5s,medium,Connects to scene 2
2,0:05,Music,Build,Tension increasing strings,5s,medium,Layer percussion
2,0:08,SFX,Glow,Artifact power up sound,3s,growing,Bright synth rise
...
```

**Audio Search Prompts for AI Music/SFX Generation**:
```
Music Generation (Suno/Udio):
- "Dark cinematic orchestral tension underscore, 90 BPM, D minor"
- "Building suspense with deep strings and timpani, slow crescendo"
- "Epic climax moment, full orchestra, choir, driving rhythm"

SFX Generation (ElevenLabs/stock libraries):
- "Footsteps on gravel, slow, tactical boots"
- "Metal door creaking slowly, horror movie style"
- "Low ominous rumble, distant, atmospheric"
- "Magical glowing artifact power up, bright ethereal"
- "Bass impact hit for transition, cinematic trailer style"
```

---

### FLOW 8: Output Delivery

**Input**: All generated data

**Process**:
1. **Compile Results**: Gather all prompts and metadata
2. **Format Output**: JSON/CSV/Text based on user preference
3. **Store Results**: Save to database and file system
4. **Return to User**: API response with download links

**Output Options**:
- JSON: Complete structured data
- CSV: Tabular prompt list
- TXT: Human-readable format
- Files: Downloadable prompt files per scene
- Audio Guide: Separate audio timing spreadsheet

**Sound Design Output Formats**:
- JSON: Structured audio recommendations
- CSV: Timeline format for audio editors
- EDL: Edit Decision List for DAW integration
- TXT: Human-readable audio script

**API Response**:
```json
{
  "project_id": "abc123",
  "status": "complete",
  "outputs": {
    "prompts_json": "/downloads/prompts.json",
    "prompts_csv": "/downloads/prompts.csv",
    "prompts_txt": "/downloads/prompts.txt",
    "audio_design_json": "/downloads/audio_design.json",
    "audio_timeline_csv": "/downloads/audio_timeline.csv",
    "draft_video": "/downloads/draft.mp4"
  },
  "summary": {
    "total_scenes": 3,
    "total_duration": 15,
    "characters_used": ["Alex", "Shadow"],
    "audio_summary": {
      "total_sfx": 12,
      "music_styles": ["dark orchestral", "tension build", "climax"]
    }
  }
}
```

**Tech**:
- FastAPI: FileResponse for downloads
- File storage: Organized by project ID
- Compression: ZIP for bulk downloads

---

## Agent Architecture

| Agent | Input | Output | Notes |
|-------|-------|--------|-------|
| Scenario Analysis | Scenario text, project type | Scene breakdown, timing, suggestions | Could include AI-generated enhancements |
| Character Analysis | Scene breakdown, character TXT | Character assignment, traits | Ensure consistency across scenes |
| Source Material | PDFs/TXT books | Scene instructions, camera, timing | Uses PyPDF2/Tika for parsing |
| Prompt Generation | Scene + Characters + Source | Image & video prompts | Gemini-optimized prompts with camera params |
| Montage | Generated media + scene info | Draft video | Optional; basic montage with FFmpeg |
| Sound Design | Complete scene data, timing | Music style, SFX, audio cues | Analyzes mood/action for audio |
| Orchestrator | All agents | Complete workflow | Manages order, data flow, iterative refinement |

---

## Database Schema (Supabase)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50),
    total_duration INT,
    style_preferences JSONB,
    user_id UUID DEFAULT auth.uid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scenarios
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scenes
CREATE TABLE scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    scene_number INT,
    description TEXT,
    duration INT,
    mood VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Characters
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(100),
    traits TEXT[],
    style TEXT,
    expressions TEXT[],
    poses TEXT[]
);

-- Scene Characters
CREATE TABLE scene_characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    expression VARCHAR(200),
    pose VARCHAR(200),
    action TEXT,
    costume_notes TEXT
);

-- Scene Instructions
CREATE TABLE scene_instructions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,
    breakdown JSONB,
    transition_in VARCHAR(100),
    transition_out VARCHAR(100)
);

-- Generated Prompts
CREATE TABLE generated_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,
    prompt_type VARCHAR(20), -- 'image' or 'video'
    time_range VARCHAR(20),
    prompt TEXT,
    parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audio Design
CREATE TABLE audio_design (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,
    music_style VARCHAR(200),
    music_tempo_bpm INT,
    music_instruments TEXT[],
    energy_level INT,
    fade_in VARCHAR(20),
    fade_out VARCHAR(20),
    search_prompts TEXT[],
    ambience_base VARCHAR(200),
    ambience_elements TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sound Effects
CREATE TABLE sound_effects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audio_design_id UUID REFERENCES audio_design(id) ON DELETE CASCADE,
    timestamp VARCHAR(10),
    sound_type VARCHAR(100),
    duration DECIMAL(4,2),
    volume VARCHAR(20),
    variation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audio Cues
CREATE TABLE audio_cues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audio_design_id UUID REFERENCES audio_design(id) ON DELETE CASCADE,
    timestamp VARCHAR(10),
    cue_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (RLS)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE characters ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own data
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- Cascade policies for child tables
CREATE POLICY "Users can view own scenarios" ON scenarios
    FOR SELECT USING (
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

-- Similar policies for other tables...
```

---

## API Endpoints

```
POST   /api/projects                    - Create new project
GET    /api/projects/{id}                - Get project details
POST   /api/projects/{id}/scenario       - Submit scenario
POST   /api/projects/{id}/characters     - Upload character DB
POST   /api/projects/{id}/sources        - Upload source materials
POST   /api/projects/{id}/generate       - Trigger prompt generation
GET    /api/projects/{id}/status         - Check generation status
GET    /api/projects/{id}/results        - Get generated prompts
GET    /api/projects/{id}/download       - Download outputs
POST   /api/projects/{id}/montage        - Generate montage (optional)
POST   /api/projects/{id}/sound-design    - Generate audio recommendations
```

---

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── projects.py
│   │   │   ├── scenarios.py
│   │   │   ├── generation.py
│   │   │   └── montage.py
│   ├── agents/
│   │   ├── scenario_agent.py
│   │   ├── character_agent.py
│   │   ├── source_agent.py
│   │   ├── prompt_agent.py
│   │   ├── montage_agent.py
│   │   └── sound_design_agent.py
│   ├── models/
│   │   ├── database.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── file_service.py
│   │   └── queue_service.py
│   └── main.py
├── workers/
│   └── celery_worker.py
├── prompts/
│   ├── scenario_analysis.jinja2
│   ├── character_assignment.jinja2
│   ├── source_mapping.jinja2
│   ├── prompt_generation.jinja2
│   └── sound_design.jinja2
└── requirements.txt

frontend/
├── app/
│   ├── (pages)/
│   │   ├── new-project/
│   │   ├── scenario/
│   │   ├── characters/
│   │   ├── generate/
│   │   └── results/
│   ├── components/
│   │   ├── ui/
│   │   ├── forms/
│   │   └── displays/
│   └── lib/
└── package.json

shared/
└── types/
    └── project.types.ts
```

---

## MVP Implementation Priority

### Phase 1 (MVP)
1. Scenario Analysis Agent
2. Character Analysis Agent
3. Prompt Generation Agent
4. Basic API + simple frontend
5. 1-2 scene limit

### Phase 2
1. Source Material Agent
2. Full database implementation
3. Complete frontend
4. Multi-scene support

### Phase 3
1. Montage Agent
2. Video file processing
3. Download system
4. Project history/editing

---

## Environment Variables

```bash
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Backend
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_gemini_key

# Audio APIs (Optional - for generation)
ELEVENLABS_API_KEY=your_elevenlabs_key    # SFX generation
SUNO_API_KEY=your_suno_key                # Music generation
UDIO_API_KEY=your_udio_key                # Music generation

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```
