"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

const PROJECT_TYPES = [
  { value: "trailer", label: "Trailer" },
  { value: "commercial", label: "Commercial" },
  { value: "short_film", label: "Short Film" },
  { value: "tiktok", label: "TikTok Video" },
  { value: "custom", label: "Custom" },
]

const PACING_OPTIONS = [
  { value: "fast", label: "Fast" },
  { value: "mixed", label: "Mixed" },
  { value: "slow", label: "Slow" },
]

export default function HomePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sceneCountAny, setSceneCountAny] = useState(false)

  const handleCreateProject = async (formData: FormData) => {
    setIsLoading(true)
    setError(null)

    const sceneCountValue = formData.get("sceneCount") as string
    const projectData = {
      type: formData.get("type"),
      total_duration: parseInt(formData.get("duration") as string) || null,
      scene_count_target: sceneCountAny || !sceneCountValue ? null : parseInt(sceneCountValue) || null,
      pacing: formData.get("pacing"),
      style_preferences: {},
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projectData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }))
        throw new Error(errorData.detail || `Failed: ${response.status}`)
      }

      const project = await response.json()
      router.push(`/project/${project.id}/scenario`)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create project"
      setError(message)
      console.error("Failed to create project:", err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-4">
            AI Video Generation Platform
          </h1>
          <p className="text-xl text-slate-300">
            Transform your scenarios into cinematic prompts with AI
          </p>
        </div>

        {/* Create Project Form */}
        <div className="max-w-2xl mx-auto">
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-8 border border-slate-700">
            <h2 className="text-2xl font-semibold text-white mb-6">
              Create New Project
            </h2>

            {/* Error Display */}
            {error && (
              <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 text-red-300">
                {error}
              </div>
            )}

            <form action={handleCreateProject} className="space-y-6">
              {/* Project Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Project Type
                </label>
                <select
                  name="type"
                  required
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {PROJECT_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Duration */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Duration (seconds) - Optional
                </label>
                <input
                  type="number"
                  name="duration"
                  min="5"
                  max="300"
                  placeholder="e.g., 30"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Scene Count */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Target Scene Count
                </label>
                <div className="flex items-center gap-3 mb-2">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={sceneCountAny}
                      onChange={(e) => setSceneCountAny(e.target.checked)}
                      className="mr-2 w-4 h-4 rounded"
                    />
                    <span className="text-slate-300">Let AI decide based on scenario</span>
                  </label>
                </div>
                {!sceneCountAny && (
                  <input
                    type="number"
                    name="sceneCount"
                    min="1"
                    max="20"
                    placeholder="e.g., 5"
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                )}
              </div>

              {/* Pacing */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Pacing
                </label>
                <div className="flex gap-4">
                  {PACING_OPTIONS.map((option) => (
                    <label key={option.value} className="flex items-center">
                      <input
                        type="radio"
                        name="pacing"
                        value={option.value}
                        defaultChecked={option.value === "mixed"}
                        className="mr-2"
                      />
                      <span className="text-slate-300">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
              >
                {isLoading ? "Creating..." : "Create Project"}
              </button>
            </form>
          </div>
        </div>

        {/* Features */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <FeatureCard
            title="Scenario Analysis"
            description="AI breaks down your story into cinematic scenes with timing and mood"
          />
          <FeatureCard
            title="Character Mapping"
            description="Assign characters consistently across all scenes"
          />
          <FeatureCard
            title="Sound Design"
            description="Get music and sound effect recommendations for each scene"
          />
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="bg-slate-800/30 backdrop-blur rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  )
}
