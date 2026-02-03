from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# =============================================================================
# Project Schemas
# =============================================================================

class ProjectCreate(BaseModel):
    type: str = Field(..., description="trailer, commercial, short_film, tiktok, custom")
    total_duration: Optional[int] = Field(None, description="Total duration in seconds")
    scene_count_target: Optional[int] = Field(None, description="Target number of scenes")
    style_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    pacing: Optional[str] = Field("mixed", description="fast, slow, mixed")


class ProjectResponse(BaseModel):
    id: UUID
    type: str
    total_duration: Optional[int]
    style_preferences: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Scenario Schemas
# =============================================================================

class ScenarioCreate(BaseModel):
    text: str = Field(..., min_length=1)


class ScenarioResponse(BaseModel):
    id: UUID
    project_id: UUID
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Scene Schemas
# =============================================================================

class SceneAction(BaseModel):
    action: str
    timestamp: Optional[str] = None


class SceneBreakdown(BaseModel):
    id: int
    description: str
    actions: List[str]
    duration: int
    mood: str
    enhancements: Optional[List[str]] = None
    time_breakdown: Optional[List[Dict[str, str]]] = None


class SceneAnalysisResponse(BaseModel):
    scenes: List[SceneBreakdown]
    total_duration: int
    suggestions: Optional[List[str]] = None


class SceneResponse(BaseModel):
    id: UUID
    project_id: UUID
    scene_number: int
    description: str
    duration: int
    mood: str
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Character Schemas
# =============================================================================

class CharacterInput(BaseModel):
    name: str
    traits: List[str]
    style: Optional[str] = None
    expressions: Optional[List[str]] = None
    poses: Optional[List[str]] = None


class CharacterAssignment(BaseModel):
    name: str
    expression: str
    pose: str
    action: str
    costume_notes: Optional[str] = None


class CharacterAnalysisResponse(BaseModel):
    assignments: List[Dict[str, Any]]
    consistency_map: Dict[str, Dict[str, Any]]


class CharacterResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    traits: List[str]
    style: Optional[str]
    expressions: Optional[List[str]]
    poses: Optional[List[str]]

    class Config:
        from_attributes = True


# =============================================================================
# Source Material Schemas
# =============================================================================

class SourceMaterialUpload(BaseModel):
    filename: str
    content_type: str
    file_path: str


class SceneInstruction(BaseModel):
    scene_id: int
    breakdown: List[Dict[str, str]]
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None


class SourceAnalysisResponse(BaseModel):
    scene_instructions: List[SceneInstruction]


# =============================================================================
# Prompt Generation Schemas
# =============================================================================

class CameraParameters(BaseModel):
    camera: str
    lens: str
    focal_length: str
    aperture: str


class ImagePrompt(BaseModel):
    time: str
    prompt: str
    negative_prompt: Optional[str] = None


class VideoPrompt(BaseModel):
    time: str
    prompt: str
    camera: str
    lens: str
    aperture: str
    duration: Optional[int] = None


class ScenePrompts(BaseModel):
    scene_id: int
    image_prompts: List[ImagePrompt]
    video_prompts: List[VideoPrompt]


class PromptGenerationResponse(BaseModel):
    scene_prompts: List[ScenePrompts]


# =============================================================================
# Sound Design Schemas
# =============================================================================

class SoundEffect(BaseModel):
    timestamp: str
    sound_type: str
    duration: str
    volume: str
    variation: Optional[str] = None


class MusicRecommendation(BaseModel):
    style: str
    tempo_bpm: int
    instruments: List[str]
    energy_level: int
    fade_in: str
    fade_out: str
    search_prompts: List[str]


class AudioCue(BaseModel):
    timestamp: str
    cue_type: str
    description: str


class Ambience(BaseModel):
    base: str
    elements: List[str]
    intensity: str


class SceneAudioDesign(BaseModel):
    scene_id: int
    scene_duration: int
    music: MusicRecommendation
    sound_effects: List[SoundEffect]
    ambience: Ambience
    audio_cues: List[AudioCue]


class AudioDesignResponse(BaseModel):
    audio_design: List[SceneAudioDesign]
    overall_audio_arc: Dict[str, Any]


# =============================================================================
# Montage Schemas
# =============================================================================

class MontageRequest(BaseModel):
    include_audio: bool = False
    resolution: str = "1920x1080"
    fps: int = 24


class MontageResponse(BaseModel):
    output_file: str
    duration: int
    resolution: str
    fps: int
    scenes: List[Dict[str, Any]]


# =============================================================================
# Generation Status
# =============================================================================

class GenerationStatus(BaseModel):
    project_id: UUID
    status: str  # pending, processing, completed, failed
    current_step: Optional[str] = None
    progress: int = 0
    error: Optional[str] = None


class GenerationResults(BaseModel):
    project_id: UUID
    status: str
    outputs: Dict[str, str]
    summary: Dict[str, Any]
