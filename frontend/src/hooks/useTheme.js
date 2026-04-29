import { useState, useEffect, useCallback } from 'react'
import useLocalStorage from './useLocalStorage'

export default function useTheme() {
  const [stored, setStored] = useLocalStorage('campusrule-theme', 'dark')
  const [theme, setThemeState] = useState(stored)

  const applyTheme = useCallback((t) => {
    const root = document.documentElement
    if (t === 'light') {
      root.classList.add('light-theme')
      root.classList.remove('dark')
    } else {
      root.classList.remove('light-theme')
      root.classList.add('dark')
    }
  }, [])

  useEffect(() => {
    applyTheme(theme)
  }, [theme, applyTheme])

  const setTheme = useCallback((t) => {
    if (t === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      const resolved = prefersDark ? 'dark' : 'light'
      setThemeState(resolved)
      setStored('auto')
      applyTheme(resolved)
    } else {
      setThemeState(t)
      setStored(t)
      applyTheme(t)
    }
  }, [setStored, applyTheme])

  const toggle = useCallback(() => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }, [theme, setTheme])

  return { theme, setTheme, toggle }
}
