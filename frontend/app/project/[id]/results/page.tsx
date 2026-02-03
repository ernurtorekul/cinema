"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

export default function ResultsPage() {
  const router = useRouter()
  const params = useParams()
  const projectId = params.id as string

  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"scenes" | "characters" | "prompts" | "audio">("scenes")

  // Helper to extract scenes from results (handles both old and new formats)
  const getScenes = () => {
    if (results?.scenario_analysis?.scenes) {
      return results.scenario_analysis.scenes
    }
    return results?.scenes || []
  }

  // Helper to extract prompts from results
  const getPrompts = () => {
    if (results?.prompt_generation?.scene_prompts) {
      // Flatten scene prompts into individual prompts
      const prompts: any[] = []
      results.prompt_generation.scene_prompts.forEach((sp: any) => {
        if (sp.image_prompts) {
          sp.image_prompts.forEach((ip: any) => {
            prompts.push({
              ...ip,
              scene_id: sp.scene_id,
              prompt_type: "image",
              time_range: ip.time
            })
          })
        }
        if (sp.video_prompts) {
          sp.video_prompts.forEach((vp: any) => {
            prompts.push({
              ...vp,
              scene_id: sp.scene_id,
              prompt_type: "video",
              time_range: vp.time
            })
          })
        }
      })
      return prompts
    }
    return results?.prompts || []
  }

  // Helper to extract audio design from results
  const getAudioDesign = () => {
    if (results?.sound_design?.audio_design) {
      return results.sound_design.audio_design
    }
    return results?.audio_design || []
  }

  // Helper to extract character assignments from results
  const getCharacterAssignments = () => {
    if (results?.character_analysis?.assignments) {
      return results.character_analysis.assignments
    }
    return []
  }

  // Helper to get consistency map
  const getConsistencyMap = () => {
    if (results?.character_analysis?.consistency_map) {
      return results.character_analysis.consistency_map
    }
    return {}
  }

  useEffect(() => {
    fetchResults()
  }, [])

  const fetchResults = async () => {
    let apiResults = null

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/results`
      )
      if (response.ok) {
        apiResults = await response.json()
      }
    } catch (error) {
      console.error("Failed to fetch results:", error)
    }

    // Use API results if they have content, otherwise fallback to sessionStorage
    const hasResults = apiResults && (
      apiResults.scenes?.length > 0 ||
      apiResults.prompts?.length > 0 ||
      apiResults.audio_design?.length > 0 ||
      apiResults.scenario_analysis ||
      apiResults.prompt_generation ||
      apiResults.sound_design
    )

    if (hasResults) {
      setResults(apiResults)
    } else {
      // Fallback to sessionStorage
      const storedResults = sessionStorage.getItem(`results-${projectId}`)
      if (storedResults) {
        try {
          const data = JSON.parse(storedResults)
          setResults(data)
        } catch (e) {
          console.error("Failed to parse stored results:", e)
        }
      }
    }

    setLoading(false)
  }

  const downloadResults = (format: "json" | "csv") => {
    if (!results) return

    let content = ""
    let filename = ""
    let type = ""

    if (format === "json") {
      content = JSON.stringify(results, null, 2)
      filename = `project-${projectId}-results.json`
      type = "application/json"
    } else {
      // Simple CSV format
      const prompts = getPrompts()
      content = "Scene,Type,Time,Prompt\n"
      prompts.forEach((p: any) => {
        content += `${p.scene_id},${p.prompt_type},"${p.time_range}","${p.prompt}"\n`
      })
      filename = `project-${projectId}-prompts.csv`
      type = "text/csv"
    }

    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-white">Loading results...</div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-slate-400">No results found</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Generation Results
              </h1>
              <p className="text-slate-400">
                {getScenes().length || 0} scenes •{" "}
                {getPrompts().length || 0} prompts
              </p>
            </div>
            <button
              onClick={() => router.push("/")}
              className="py-2 px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              New Project
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <TabButton
              active={activeTab === "scenes"}
              onClick={() => setActiveTab("scenes")}
            >
              Scenes
            </TabButton>
            {getCharacterAssignments().length > 0 && (
              <TabButton
                active={activeTab === "characters"}
                onClick={() => setActiveTab("characters")}
              >
                Characters
              </TabButton>
            )}
            <TabButton
              active={activeTab === "prompts"}
              onClick={() => setActiveTab("prompts")}
            >
              Prompts
            </TabButton>
            <TabButton
              active={activeTab === "audio"}
              onClick={() => setActiveTab("audio")}
            >
              Audio Design
            </TabButton>
          </div>

          {/* Content */}
          <div className="bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700">
            {activeTab === "scenes" && (
              <div className="p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Scene Breakdown</h2>
                <div className="space-y-4">
                  {getScenes().map((scene: any, idx: number) => (
                    <div
                      key={scene.id || idx}
                      className="bg-slate-700/50 rounded-lg p-4"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-white font-medium">
                          Scene {scene.scene_number || scene.id || idx + 1}
                        </h3>
                        <span className="text-sm text-slate-400">
                          {scene.duration}s
                        </span>
                      </div>
                      <p className="text-slate-300">{scene.description}</p>
                      {scene.mood && (
                        <p className="text-sm text-slate-500 mt-2">
                          Mood: {scene.mood}
                        </p>
                      )}
                      {scene.actions && scene.actions.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs text-slate-500 mb-1">Actions:</p>
                          <ul className="text-sm text-slate-400 list-disc list-inside">
                            {scene.actions.map((action: string, i: number) => (
                              <li key={i}>{action}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === "characters" && (
              <div className="p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Character Assignments</h2>
                <p className="text-slate-400 text-sm mb-6">
                  AI assigned characters to scenes based on traits, roles, and scene requirements.
                </p>

                {/* Consistency Map */}
                {Object.keys(getConsistencyMap()).length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-medium text-white mb-3">Character Consistency</h3>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {Object.entries(getConsistencyMap()).map(([name, info]: [string, any]) => (
                        <div key={name} className="bg-slate-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium">{name}</h4>
                          <p className="text-xs text-slate-400 mt-1">
                            Traits: {info.base_traits?.join(", ")}
                          </p>
                          <p className="text-xs text-slate-500 mt-1">
                            Costume: {info.costume}
                          </p>
                          <p className="text-xs text-blue-400 mt-1">
                            Scenes: {info.appearances?.join(", ")}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Scene Assignments */}
                <div>
                  <h3 className="text-lg font-medium text-white mb-3">Scene by Scene</h3>
                  <div className="space-y-4">
                    {getCharacterAssignments().map((assignment: any, idx: number) => (
                      <div key={idx} className="bg-slate-700/50 rounded-lg p-4">
                        <h4 className="text-white font-medium mb-2">
                          Scene {assignment.scene_id}
                        </h4>
                        {assignment.characters && assignment.characters.length > 0 ? (
                          <div className="grid md:grid-cols-2 gap-3">
                            {assignment.characters.map((char: any, charIdx: number) => (
                              <div key={charIdx} className="bg-slate-600/50 rounded p-3">
                                <h5 className="text-blue-300 font-medium">{char.name}</h5>
                                <div className="mt-2 space-y-1 text-xs">
                                  {char.expression && (
                                    <p><span className="text-slate-500">Expression:</span> <span className="text-slate-300">{char.expression}</span></p>
                                  )}
                                  {char.pose && (
                                    <p><span className="text-slate-500">Pose:</span> <span className="text-slate-300">{char.pose}</span></p>
                                  )}
                                  {char.action && (
                                    <p><span className="text-slate-500">Action:</span> <span className="text-slate-300">{char.action}</span></p>
                                  )}
                                  {char.costume_notes && (
                                    <p><span className="text-slate-500">Costume:</span> <span className="text-slate-300">{char.costume_notes}</span></p>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-slate-500 text-sm italic">No characters assigned to this scene</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "prompts" && (
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold text-white">
                    Generated Prompts
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={() => downloadResults("json")}
                      className="py-2 px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm"
                    >
                      Download JSON
                    </button>
                    <button
                      onClick={() => downloadResults("csv")}
                      className="py-2 px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm"
                    >
                      Download CSV
                    </button>
                  </div>
                </div>
                <div className="space-y-4">
                  {getPrompts().map((prompt: any, idx: number) => (
                    <div
                      key={prompt.id || idx}
                      className="bg-slate-700/50 rounded-lg p-4"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs uppercase text-slate-500 font-medium">
                          {prompt.prompt_type} • Scene {prompt.scene_id || idx + 1}
                        </span>
                        <span className="text-sm text-slate-400">
                          {prompt.time_range}
                        </span>
                      </div>
                      <p className="text-slate-300 text-sm">{prompt.prompt}</p>
                      {prompt.camera && (
                        <p className="text-xs text-slate-500 mt-2">
                          Camera: {prompt.camera} • Lens: {prompt.lens} • Aperture: {prompt.aperture}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === "audio" && (
              <div className="p-6">
                <h2 className="text-xl font-semibold text-white mb-4">
                  Sound Design
                </h2>
                {getAudioDesign().length === 0 ? (
                  <p className="text-slate-500">
                    No audio design data available
                  </p>
                ) : (
                  <div className="space-y-6">
                    {getAudioDesign().map((audio: any, idx: number) => (
                      <div
                        key={audio.id || idx}
                        className="bg-slate-700/50 rounded-lg p-4"
                      >
                        <h3 className="text-white font-medium mb-3">
                          Scene {audio.scene_id || idx + 1} Audio Design
                        </h3>

                        {/* Music */}
                        {audio.music && (
                          <div className="mb-4">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">
                              Music
                            </h4>
                            <p className="text-slate-300 text-sm">
                              {audio.music.style} • {audio.music.tempo_bpm} BPM
                            </p>
                            <p className="text-slate-500 text-xs mt-1">
                              Instruments: {audio.music.instruments?.join(", ")}
                            </p>
                            <p className="text-slate-500 text-xs mt-1">
                              Energy: {audio.music.energy_level}/10 • {audio.music.fade_in} • {audio.music.fade_out}
                            </p>
                          </div>
                        )}

                        {/* Sound Effects */}
                        {audio.sound_effects?.length > 0 && (
                          <div className="mb-4">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">
                              Sound Effects
                            </h4>
                            <div className="space-y-1">
                              {audio.sound_effects.map((sfx: any, sfxIdx: number) => (
                                <div
                                  key={sfx.id || sfxIdx}
                                  className="text-slate-300 text-sm flex justify-between"
                                >
                                  <span>{sfx.sound_type}</span>
                                  <span className="text-slate-500">
                                    {sfx.timestamp} • {sfx.duration} • {sfx.volume}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Ambience */}
                        {audio.ambience && (
                          <div className="mb-4">
                            <h4 className="text-sm font-medium text-slate-400 mb-2">
                              Ambience
                            </h4>
                            <p className="text-slate-300 text-sm">
                              {audio.ambience.base}
                            </p>
                            <p className="text-slate-500 text-xs mt-1">
                              Intensity: {audio.ambience.intensity}
                            </p>
                          </div>
                        )}

                        {/* Audio Cues */}
                        {audio.audio_cues?.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">
                              Audio Cues
                            </h4>
                            <div className="space-y-1">
                              {audio.audio_cues.map((cue: any, cueIdx: number) => (
                                <div
                                  key={cue.id || cueIdx}
                                  className="text-slate-300 text-sm flex justify-between"
                                >
                                  <span>{cue.cue_type}</span>
                                  <span className="text-slate-500">
                                    {cue.timestamp}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`py-2 px-4 rounded-lg transition-colors ${
        active
          ? "bg-blue-600 text-white"
          : "bg-slate-700 text-slate-300 hover:bg-slate-600"
      }`}
    >
      {children}
    </button>
  )
}
