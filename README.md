# AI Video Generation Platform

Automated AI-generated video creation using multiple specialized agents.

## Tech Stack

### Backend
- Python 3.11+ with FastAPI
- Supabase (PostgreSQL) + Storage
- Celery + Redis for async tasks
- LangChain + Gemini AI
- PyPDF2, pdfplumber for file processing

### Frontend
- Next.js 14 (React)
- Supabase JS Client
- Tailwind CSS + shadcn/ui

## Quick Start

### Prerequisites

1. Create a Supabase project at https://supabase.com
2. Get your Gemini API key from https://makersuite.google.com

### Setup Database

Run this SQL in your Supabase SQL Editor:

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
    prompt_type VARCHAR(20),
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
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase URL, keys, and Gemini API key

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_SUPABASE_URL=your_supabase_url" >> .env.local
echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key" >> .env.local

# Run frontend
npm run dev
```

Frontend runs at http://localhost:3000

### Docker (Optional)

```bash
# Start all services
docker-compose up

# Or run individually
docker-compose up backend frontend
```

## API Endpoints

```
POST   /api/projects                    - Create new project
GET    /api/projects/{id}                - Get project details
POST   /api/projects/{id}/scenario       - Submit scenario
POST   /api/projects/{id}/generate       - Trigger full generation
GET    /api/projects/{id}/status         - Check generation status
GET    /api/projects/{id}/results        - Get generated prompts
POST   /api/projects/{id}/step/{step}    - Run single step
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agents
│   │   ├── api/routes/      # API endpoints
│   │   ├── models/          # Pydantic schemas
│   │   ├── services/        # Supabase, LLM, file services
│   │   └── utils/           # Config, utilities
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── project/[id]/    # Project pages
│   │   └── globals.css
│   └── package.json
└── docker-compose.yml
```

## How It Works

1. **Create Project**: Select type (trailer, commercial, etc.)
2. **Enter Scenario**: Describe your story
3. **Add Characters** (optional): Define character traits
4. **Generate**: AI agents process through:
   - Scenario Analysis → Scene breakdown
   - Character Analysis → Assign characters
   - Prompt Generation → Image/video prompts
   - Sound Design → Music & SFX recommendations
5. **View Results**: Download prompts as JSON/CSV
