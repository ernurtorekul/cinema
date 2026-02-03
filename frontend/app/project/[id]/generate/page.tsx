"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

type Step = "scenario_analysis" | "character_analysis" | "source_analysis" | "prompt_generation" | "sound_design"

const STEP_LABELS: Record<Step, string> = {
  scenario_analysis: "Analyzing Scenario",
  character_analysis: "Assigning Characters",
  source_analysis: "Processing Source Materials",
  prompt_generation: "Generating Prompts",
  sound_design: "Creating Sound Design",
}

export default function GeneratePage() {
  const router = useRouter()
  const params = useParams()
  const projectId = params.id as string

  const [currentStep, setCurrentStep] = useState<Step | null>(null)
  const [completedSteps, setCompletedSteps] = useState<Step[]>([])
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [includeSoundDesign, setIncludeSoundDesign] = useState(true)

  useEffect(() => {
    startGeneration()
  }, [])

  const startGeneration = async () => {
    try {
      const charactersStr = sessionStorage.getItem("characters")
      const character_config = charactersStr ? JSON.parse(charactersStr) : null

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/generate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            character_config: character_config,
            include_sound_design: includeSoundDesign,
          }),
        }
      )

      if (!response.ok) throw new Error("Generation failed")

      // Stream or poll for progress (simplified here)
      const data = await response.json()
      setResults(data)
      setCurrentStep(null)

      // Store results in sessionStorage for the results page
      sessionStorage.setItem(`results-${projectId}`, JSON.stringify(data))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-2">
              Generating Your Video
            </h1>
            <p className="text-slate-400">
              AI agents are working on your project
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-900/50 border border-red-700 rounded-xl p-6 mb-8">
              <p className="text-red-300">{error}</p>
              <button
                onClick={() => router.push("/")}
                className="mt-4 text-red-300 hover:text-white"
              >
                ← Go back
              </button>
            </div>
          )}

          {/* Progress Steps */}
          <div className="space-y-4 mb-12">
            {(
              [
                "scenario_analysis",
                "character_analysis",
                "prompt_generation",
                "sound_design",
              ] as Step[]
            ).map((step) => {
              const isCurrent = currentStep === step
              const isCompleted = completedSteps.includes(step)

              return (
                <div
                  key={step}
                  className={`flex items-center gap-4 p-4 rounded-lg border transition-colors ${
                    isCurrent
                      ? "bg-blue-900/30 border-blue-600"
                      : isCompleted
                      ? "bg-green-900/30 border-green-600"
                      : "bg-slate-800/30 border-slate-700"
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isCurrent
                        ? "bg-blue-600 text-white"
                        : isCompleted
                        ? "bg-green-600 text-white"
                        : "bg-slate-700 text-slate-400"
                    }`}
                  >
                    {isCompleted ? "✓" : isCurrent ? "→" : ""}
                  </div>
                  <span className="text-white">{STEP_LABELS[step]}</span>
                </div>
              )
            })}
          </div>

          {/* Results */}
          {results && !currentStep && (
            <div className="bg-slate-800/50 backdrop-blur rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-semibold text-white mb-6">
                Generation Complete!
              </h2>

              {/* Summary */}
              <div className="grid md:grid-cols-3 gap-4 mb-8">
                <StatCard
                  label="Scenes"
                  value={results.scenario_analysis?.scenes?.length || 0}
                />
                <StatCard
                  label="Duration"
                  value={`${results.scenario_analysis?.total_duration || 0}s`}
                />
                <StatCard
                  label="Prompts"
                  value={
                    results.prompt_generation?.scene_prompts?.length * 2 || 0
                  }
                />
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={() =>
                    router.push(`/project/${projectId}/results`)
                  }
                  className="py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                >
                  View Results
                </button>
                <button
                  onClick={() => router.push("/")}
                  className="py-3 px-6 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
                >
                  New Project
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="bg-slate-700/50 rounded-lg p-4 text-center">
      <p className="text-3xl font-bold text-white">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  )
}
