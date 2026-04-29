import { useState, useRef, useCallback, useEffect } from 'react'

const API = 'http://localhost:8000'

export default function useAutoComplete() {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [visible, setVisible] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const debounceRef = useRef(null)

  const fetchSuggestions = useCallback(async (prefix, context = null) => {
    if (!prefix || prefix.trim().length < 2) {
      setSuggestions([])
      setVisible(false)
      return
    }

    if (debounceRef.current) clearTimeout(debounceRef.current)

    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await fetch(`${API}/api/autocomplete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prefix: prefix.trim(), context, limit: 6 }),
        })
        if (res.ok) {
          const data = await res.json()
          setSuggestions(data.suggestions || [])
          setVisible(data.suggestions?.length > 0)
          setSelectedIndex(-1)
        }
      } catch {
        setSuggestions([])
        setVisible(false)
      } finally {
        setLoading(false)
      }
    }, 80) // 80ms debounce for snappy feel
  }, [])

  const recordClick = useCallback(async (phrase) => {
    try {
      await fetch(`${API}/api/autocomplete/click?phrase=${encodeURIComponent(phrase)}`, {
        method: 'POST',
      })
    } catch {
      // Non-critical
    }
  }, [])

  const hide = useCallback(() => {
    setVisible(false)
    setSelectedIndex(-1)
  }, [])

  const handleKeyNav = useCallback((e) => {
    if (!visible || suggestions.length === 0) return false

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((i) => (i + 1) % suggestions.length)
      return true
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((i) => (i <= 0 ? suggestions.length - 1 : i - 1))
      return true
    }
    if (e.key === 'Escape') {
      hide()
      return true
    }
    return false
  }, [visible, suggestions, hide])

  const getSelected = useCallback(() => {
    if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
      return suggestions[selectedIndex]
    }
    return null
  }, [selectedIndex, suggestions])

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [])

  return {
    suggestions,
    loading,
    visible,
    selectedIndex,
    fetchSuggestions,
    recordClick,
    hide,
    handleKeyNav,
    getSelected,
    setVisible,
  }
}
