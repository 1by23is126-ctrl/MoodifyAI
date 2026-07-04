import { useState, useCallback, useRef } from 'react'
import useMoodTheme from './useMoodTheme'
import { analyze, getSessionId } from '../utils/api'
import { saveMoodHistoryEntry } from '../utils/storage'

// The new profile map encompassing all 12 moods + contextual weather
const profileMap = {
  Happy: { weather: 'radiant sun', envScore: 0.9, depth: 'shallow', baseline: 'high' },
  Sad: { weather: 'gentle rain', envScore: 0.2, depth: 'deep', baseline: 'low' },
  Angry: { weather: 'electric storm', envScore: 0.1, depth: 'turbulent', baseline: 'erratic' },
  Chill: { weather: 'cool drift', envScore: 0.6, depth: 'calm', baseline: 'steady' },
  Romantic: { weather: 'warm haze', envScore: 0.8, depth: 'intimate', baseline: 'soft' },
  Motivated: { weather: 'clear skies', envScore: 0.85, depth: 'focused', baseline: 'rising' },
  Lonely: { weather: 'empty echo', envScore: 0.3, depth: 'hollow', baseline: 'still' },
  Energetic: { weather: 'solar flare', envScore: 0.95, depth: 'vibrant', baseline: 'peaking' },
  Focus: { weather: 'crystal stillness', envScore: 0.7, depth: 'sharp', baseline: 'locked' },
  'Late Night': { weather: 'neon shadows', envScore: 0.4, depth: 'mysterious', baseline: 'floating' },
  Rainy: { weather: 'heavy drops', envScore: 0.3, depth: 'muffled', baseline: 'dampened' },
  Party: { weather: 'strobe flash', envScore: 1.0, depth: 'explosive', baseline: 'chaotic' }
}

export function useEmotionalEngine() {
  const [phase, setPhase] = useState('idle') // 'idle' | 'analyzing' | 'results' | 'analytics'
  const [rawInput, setRawInput] = useState('')
  const [currentMood, setCurrentMood] = useState('Chill')
  const [moodData, setMoodData] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const activeRequestRef = useRef(null)
  const sessionIdRef = useRef(getSessionId())
  
  // Theme hook syncs CSS variables to document
  const themeColors = useMoodTheme(currentMood)

  const processInput = useCallback(async (text) => {
    const trimmed = text?.trim()
    if (!trimmed) return

    activeRequestRef.current?.abort()
    const controller = new AbortController()
    activeRequestRef.current = controller

    setRawInput(trimmed)
    setPhase('analyzing')
    setErrorMessage('')

    try {
      const data = await analyze(trimmed, controller.signal, sessionIdRef.current)
      if (controller.signal.aborted) return

      setCurrentMood(data.mood || 'Chill')
      
      const profile = profileMap[data.mood] || profileMap['Chill']
      const savedData = {
        ...data,
        prompt: trimmed,
        profile,
        themeColors
      }

      setMoodData(savedData)
      saveMoodHistoryEntry({
        prompt: trimmed,
        mood: data.mood || 'Chill',
        language: data.selectedLanguage || data.language || 'English',
        recommended_songs: data.recommendationsByLanguage || data.recommendations_by_language || data.tracks || [],
        top_recommendation: Array.isArray(data.tracks) ? data.tracks[0] : null,
        confidence: typeof data.confidence === 'number' ? data.confidence : null
      })
      
      window.setTimeout(() => {
        if (!controller.signal.aborted) {
          setPhase('results')
        }
      }, 1800)
      
    } catch (err) {
      if (controller.signal.aborted) return

      console.error('Mood engine failure:', err)
      const fallbackMessage = err?.message || 'We hit a temporary issue while preparing your soundscape.'
      setErrorMessage(`${fallbackMessage} Falling back to a calm baseline.`)
      setCurrentMood('Chill')
      setMoodData({
        mood: 'Chill',
        nuancedLabel: 'Calm & Neutral',
        intensity: 'moderate',
        confidence: 0.5,
        scores: { Chill: 100 },
        genres: ['Ambient', 'Lo-Fi'],
        playlists: ['Moonlit Calm'],
        title: 'Calm & Neutral | Day Rhythm',
        explanation: 'The system encountered an error, falling back to a relaxing baseline.',
        tracks: [],
        profile: profileMap['Chill'],
        themeColors
      })
      setPhase('results')
    }
  }, [themeColors])

  const reset = useCallback(() => {
    activeRequestRef.current?.abort()
    activeRequestRef.current = null
    setPhase('idle')
    setRawInput('')
    setCurrentMood('Chill')
    setMoodData(null)
    setErrorMessage('')
  }, [])

  const returnToInput = useCallback(() => {
    activeRequestRef.current?.abort()
    activeRequestRef.current = null
    setPhase('idle')
    setMoodData(null)
    setErrorMessage('')
  }, [])

  const clearError = useCallback(() => {
    setErrorMessage('')
  }, [])

  return {
    phase,
    setPhase,
    rawInput,
    setRawInput,
    currentMood,
    moodData,
    themeColors,
    errorMessage,
    clearError,
    processInput,
    reset,
    returnToInput
  }
}
