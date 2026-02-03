"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

interface Character {
  name: string
  traits: string[]
  style?: string
  typical_roles?: string[]
  age_range?: string
}

interface CharacterPool {
  pool_name: string
  description: string
  characters: Character[]
}

export default function CharactersPage() {
  const router = useRouter()
  const params = useParams()
  const projectId = params.id as string

  const [aiChooses, setAiChooses] = useState(true)
  const [characterPool, setCharacterPool] = useState<Character[]>([])
  const [selectedCharacters, setSelectedCharacters] = useState<Character[]>([])
  const [customCharacter, setCustomCharacter] = useState<Partial<Character>>({})
  const [isLoadingPool, setIsLoadingPool] = useState(false)

  // Load character pool when AI mode is enabled
  useEffect(() => {
    if (aiChooses) {
      loadCharacterPool()
    }
  }, [aiChooses])

  const loadCharacterPool = async () => {
    setIsLoadingPool(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/projects/characters/pool`)
      if (response.ok) {
        const data: CharacterPool = await response.json()
        setCharacterPool(data.characters)
      }
    } catch (error) {
      console.error("Failed to load character pool:", error)
    } finally {
      setIsLoadingPool(false)
    }
  }

  const toggleCharacter = (character: Character) => {
    if (selectedCharacters.find(c => c.name === character.name)) {
      setSelectedCharacters(selectedCharacters.filter(c => c.name !== character.name))
    } else {
      setSelectedCharacters([...selectedCharacters, character])
    }
  }

  const addCustomCharacter = () => {
    if (!customCharacter.name || !customCharacter.traits || customCharacter.traits.length === 0) return

    const newChar: Character = {
      name: customCharacter.name,
      traits: Array.isArray(customCharacter.traits) ? customCharacter.traits : customCharacter.traits.split(',').map(t => t.trim()),
      style: customCharacter.style,
      typical_roles: customCharacter.typical_roles,
      age_range: customCharacter.age_range
    }

    setSelectedCharacters([...selectedCharacters, newChar])
    setCustomCharacter({})
  }

  const removeCharacter = (name: string) => {
    setSelectedCharacters(selectedCharacters.filter(c => c.name !== name))
  }

  const handleContinue = () => {
    if (aiChooses) {
      // AI mode: pass pool and must_include
      const characterData = {
        mode: "ai_decides",
        pool: characterPool,
        must_include: selectedCharacters
      }
      sessionStorage.setItem("characters", JSON.stringify(characterData))
    } else {
      // Manual mode: pass only selected characters
      const characterData = {
        mode: "manual",
        characters: selectedCharacters
      }
      sessionStorage.setItem("characters", JSON.stringify(characterData))
    }
    router.push(`/project/${projectId}/generate`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Back Button */}
          <button
            onClick={() => router.back()}
            className="text-slate-400 hover:text-white mb-8 flex items-center gap-2"
          >
            ← Back
          </button>

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              Select Characters (Optional)
            </h1>
            <p className="text-slate-400">
              Choose how to handle character casting for your video
            </p>
          </div>

          {/* Mode Toggle */}
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-white font-semibold mb-1">Character Selection Mode</h3>
                <p className="text-sm text-slate-400">
                  {aiChooses
                    ? "AI will intelligently choose characters from your pool based on each scene's requirements"
                    : "Manually enter characters - they will be assigned as specified"
                  }
                </p>
              </div>
              <div className="flex items-center gap-4">
                <span className={`text-sm ${!aiChooses ? "text-blue-400 font-medium" : "text-slate-500"}`}>
                  Manual Entry
                </span>
                <button
                  onClick={() => setAiChooses(!aiChooses)}
                  className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors ${
                    aiChooses ? "bg-blue-600" : "bg-slate-600"
                  }`}
                >
                  <span
                    className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                      aiChooses ? "translate-x-8" : "translate-x-1"
                    }`}
                  />
                </button>
                <span className={`text-sm ${aiChooses ? "text-blue-400 font-medium" : "text-slate-500"}`}>
                  AI Chooses
                </span>
              </div>
            </div>

            {aiChooses && (
              <div className="mt-4 p-4 bg-blue-900/30 border border-blue-700 rounded-lg">
                <p className="text-sm text-blue-300">
                  <strong>AI will:</strong>
                  <ul className="list-disc list-inside mt-2 space-y-1 text-blue-200">
                    <li>Analyze each scene's mood, action, and requirements</li>
                    <li>Match characters from characters.txt based on traits and roles</li>
                    <li>Assign expressions, poses, and actions that fit each scene</li>
                    <li>Selected characters below will be prioritized</li>
                  </ul>
                </p>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column: Character Selection */}
            <div className="lg:col-span-2 space-y-8">
              {aiChooses ? (
                /* AI Mode: Show character pool */
                <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700">
                  <h2 className="text-xl font-semibold text-white mb-4">
                    Character Pool
                    <span className="text-sm font-normal text-slate-400 ml-2">
                      (loaded from characters.txt)
                    </span>
                  </h2>
                  <p className="text-sm text-slate-400 mb-4">
                    Click to select characters you want to prioritize. AI will still consider all characters when casting.
                  </p>

                  {isLoadingPool ? (
                    <div className="text-center py-8 text-slate-500">
                      Loading character pool...
                    </div>
                  ) : characterPool.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                      No characters found. Add names to characters.txt
                    </div>
                  ) : (
                    <div className="grid md:grid-cols-2 gap-3">
                      {characterPool.map((char) => {
                        const isSelected = selectedCharacters.find(c => c.name === char.name)
                        return (
                          <div
                            key={char.name}
                            onClick={() => toggleCharacter(char)}
                            className={`cursor-pointer rounded-lg p-4 border transition-all ${
                              isSelected
                                ? "bg-blue-900/40 border-blue-500"
                                : "bg-slate-700/50 border-slate-600 hover:border-slate-500"
                            }`}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <h3 className="text-white font-medium">{char.name}</h3>
                              {isSelected && <span className="text-blue-400">✓</span>}
                            </div>
                            <p className="text-xs text-slate-400 mb-1">
                              {char.traits?.slice(0, 4).join(", ")}
                            </p>
                            <p className="text-xs text-slate-500">
                              {char.typical_roles?.slice(0, 2).join(", ")}
                            </p>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              ) : (
                /* Manual Mode: Custom character form */
                <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700">
                  <h2 className="text-xl font-semibold text-white mb-4">
                    Add Custom Characters
                  </h2>
                  <p className="text-sm text-slate-400 mb-4">
                    Enter characters manually. These will be used exactly as specified.
                  </p>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Name *
                      </label>
                      <input
                        type="text"
                        value={customCharacter.name || ""}
                        onChange={(e) =>
                          setCustomCharacter({ ...customCharacter, name: e.target.value })
                        }
                        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500"
                        placeholder="Character name"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Age Range
                      </label>
                      <input
                        type="text"
                        value={customCharacter.age_range || ""}
                        onChange={(e) =>
                          setCustomCharacter({ ...customCharacter, age_range: e.target.value })
                        }
                        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 25-40"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Traits (comma separated) *
                      </label>
                      <input
                        type="text"
                        value={Array.isArray(customCharacter.traits) ? customCharacter.traits.join(', ') : customCharacter.traits || ""}
                        onChange={(e) =>
                          setCustomCharacter({ ...customCharacter, traits: e.target.value })
                        }
                        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., brave, determined, athletic"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Typical Roles
                      </label>
                      <input
                        type="text"
                        value={customCharacter.typical_roles?.join(', ') || ""}
                        onChange={(e) =>
                          setCustomCharacter({ ...customCharacter, typical_roles: e.target.value.split(',').map(r => r.trim()) })
                        }
                        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., warrior, hero, leader"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Style Description
                      </label>
                      <input
                        type="text"
                        value={customCharacter.style || ""}
                        onChange={(e) =>
                          setCustomCharacter({ ...customCharacter, style: e.target.value })
                        }
                        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., tactical gear, dark colors, muscular build"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <button
                        onClick={addCustomCharacter}
                        disabled={!customCharacter.name || !customCharacter.traits}
                        className="w-full py-2 px-4 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg transition-colors"
                      >
                        Add Character
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Selected Characters */}
            <div className="lg:col-span-1">
              <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700 sticky top-8">
                <h2 className="text-xl font-semibold text-white mb-4">
                  Selected ({selectedCharacters.length})
                </h2>

                {selectedCharacters.length === 0 ? (
                  <p className="text-slate-500 text-center py-8">
                    {aiChooses
                      ? "No characters prioritized. AI will use the full pool."
                      : "No characters added yet"}
                  </p>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {selectedCharacters.map((char) => (
                      <div
                        key={char.name}
                        className="bg-slate-700/50 rounded-lg p-3"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-white font-medium text-sm">{char.name}</h3>
                          <button
                            onClick={() => removeCharacter(char.name)}
                            className="text-red-400 hover:text-red-300 text-xs"
                          >
                            ✕
                          </button>
                        </div>
                        <p className="text-xs text-slate-400">
                          {char.traits?.slice(0, 3).join(", ")}
                        </p>
                        {aiChooses && (
                          <p className="text-xs text-blue-400 mt-1">
                            Will be prioritized by AI
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Continue Button */}
                <button
                  onClick={handleContinue}
                  className="w-full mt-6 py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                >
                  {aiChooses
                    ? selectedCharacters.length > 0
                      ? "Continue with AI Selection"
                      : "Continue (AI picks from full pool)"
                    : selectedCharacters.length > 0
                      ? "Continue with Characters"
                      : "Skip Characters"
                  }
                </button>

                <button
                  onClick={() => {
                    sessionStorage.removeItem("characters")
                    router.push(`/project/${projectId}/generate`)
                  }}
                  className="w-full mt-3 py-2 px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm"
                >
                  Skip This Step
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
