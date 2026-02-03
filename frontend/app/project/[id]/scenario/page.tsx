"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

export default function ScenarioPage() {
  const router = useRouter()
  const params = useParams()
  const projectId = params.id as string

  const [scenario, setScenario] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    // Verify project exists
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}`)
      .then((res) => {
        if (!res.ok) router.push("/")
      })
      .catch(() => router.push("/"))
  }, [projectId, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!scenario.trim()) return

    setIsLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/scenario`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: scenario }),
        }
      )

      if (response.ok) {
        router.push(`/project/${projectId}/characters`)
      }
    } catch (error) {
      console.error("Failed to save scenario:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const exampleScenarios = [
    "A hero sneaks into the villain's lair and discovers a glowing artifact.",
    "A spaceship crash-lands on an alien planet and the crew must survive.",
    "A detective arrives at a crime scene and finds a mysterious clue.",
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          {/* Back Button */}
          <button
            onClick={() => router.push("/")}
            className="text-slate-400 hover:text-white mb-8 flex items-center gap-2"
          >
            ← Back
          </button>

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              Enter Your Scenario
            </h1>
            <p className="text-slate-400">
              Describe the story you want to transform into a video
            </p>
          </div>

          {/* Scenario Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Scenario Text (10-5000 characters)
              </label>
              <textarea
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                required
                rows={12}
                placeholder="Describe your story here..."
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <div className="flex justify-end mt-2">
                <span className="text-sm text-slate-500">
                  {scenario.length} characters
                </span>
              </div>
            </div>

            {/* Example Scenarios */}
            <div>
              <p className="text-sm text-slate-400 mb-2">Examples:</p>
              <div className="space-y-2">
                {exampleScenarios.map((example, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setScenario(example)}
                    className="block w-full text-left px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-slate-400 hover:text-white transition-colors text-sm"
                  >
                    "{example}"
                  </button>
                ))}
              </div>
            </div>

            {/* Submit */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isLoading || scenario.length < 10}
                className="flex-1 py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
              >
                {isLoading ? "Saving..." : "Continue"}
              </button>
              <button
                type="button"
                onClick={() => router.push(`/project/${projectId}/generate`)}
                className="py-3 px-6 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
              >
                Skip
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
