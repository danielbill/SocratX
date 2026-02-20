import { createContext, useContext, useEffect, useState, useCallback } from 'react'

export type ThemeMode = 'dark' | 'gray' | 'light' | 'custom'

export interface CustomThemeColors {
  background: string
  foreground: string
  card: string
  cardForeground: string
  primary: string
  primaryForeground: string
  secondary: string
  secondaryForeground: string
  muted: string
  mutedForeground: string
  accent: string
  accentForeground: string
  destructive: string
  destructiveForeground: string
  border: string
  input: string
  ring: string
}

interface ThemeContextType {
  theme: ThemeMode
  customColors: CustomThemeColors
  setTheme: (theme: ThemeMode) => void
  setCustomColors: (colors: Partial<CustomThemeColors>) => void
  isLoading: boolean
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

const THEME_STORAGE_KEY = 'socratx-theme'
const CUSTOM_COLORS_STORAGE_KEY = 'socratx-custom-colors'

// HSL color values for different themes (matching Tailwind @theme syntax)
const THEME_COLORS: Record<ThemeMode, Partial<CustomThemeColors>> = {
  dark: {
    background: 'hsl(240 10% 3.9%)',
    foreground: 'hsl(0 0% 98%)',
    card: 'hsl(240 10% 3.9%)',
    cardForeground: 'hsl(0 0% 98%)',
    primary: 'hsl(0 0% 98%)',
    primaryForeground: 'hsl(240 5.9% 10%)',
    secondary: 'hsl(240 3.7% 15.9%)',
    secondaryForeground: 'hsl(0 0% 98%)',
    muted: 'hsl(240 3.7% 15.9%)',
    mutedForeground: 'hsl(240 5% 64.9%)',
    accent: 'hsl(240 3.7% 15.9%)',
    accentForeground: 'hsl(0 0% 98%)',
    destructive: 'hsl(0 62.8% 30.6%)',
    destructiveForeground: 'hsl(0 0% 98%)',
    border: 'hsl(240 3.7% 15.9%)',
    input: 'hsl(240 3.7% 15.9%)',
    ring: 'hsl(240 4.9% 83.9%)',
  },
  gray: {
    background: 'hsl(0 0% 8%)',
    foreground: 'hsl(0 0% 95%)',
    card: 'hsl(0 0% 10%)',
    cardForeground: 'hsl(0 0% 95%)',
    primary: 'hsl(0 0% 95%)',
    primaryForeground: 'hsl(0 0% 10%)',
    secondary: 'hsl(0 0% 15%)',
    secondaryForeground: 'hsl(0 0% 95%)',
    muted: 'hsl(0 0% 15%)',
    mutedForeground: 'hsl(0 0% 60%)',
    accent: 'hsl(0 0% 15%)',
    accentForeground: 'hsl(0 0% 95%)',
    destructive: 'hsl(0 70% 35%)',
    destructiveForeground: 'hsl(0 0% 95%)',
    border: 'hsl(0 0% 18%)',
    input: 'hsl(0 0% 18%)',
    ring: 'hsl(0 0% 80%)',
  },
  light: {
    background: 'hsl(0 0% 100%)',
    foreground: 'hsl(240 10% 3.9%)',
    card: 'hsl(0 0% 100%)',
    cardForeground: 'hsl(240 10% 3.9%)',
    primary: 'hsl(240 5.9% 10%)',
    primaryForeground: 'hsl(0 0% 98%)',
    secondary: 'hsl(240 4.8% 95.9%)',
    secondaryForeground: 'hsl(240 5.9% 10%)',
    muted: 'hsl(240 4.8% 95.9%)',
    mutedForeground: 'hsl(240 3.8% 46.1%)',
    accent: 'hsl(240 4.8% 95.9%)',
    accentForeground: 'hsl(240 5.9% 10%)',
    destructive: 'hsl(0 84.2% 60.2%)',
    destructiveForeground: 'hsl(0 0% 98%)',
    border: 'hsl(240 5.9% 90%)',
    input: 'hsl(240 5.9% 90%)',
    ring: 'hsl(240 10% 3.9%)',
  },
  custom: {}, // Will use customColors
}

const DEFAULT_CUSTOM_COLORS: CustomThemeColors = {
  background: 'hsl(240 10% 3.9%)',
  foreground: 'hsl(0 0% 98%)',
  card: 'hsl(240 10% 3.9%)',
  cardForeground: 'hsl(0 0% 98%)',
  primary: 'hsl(0 0% 98%)',
  primaryForeground: 'hsl(240 5.9% 10%)',
  secondary: 'hsl(240 3.7% 15.9%)',
  secondaryForeground: 'hsl(0 0% 98%)',
  muted: 'hsl(240 3.7% 15.9%)',
  mutedForeground: 'hsl(240 5% 64.9%)',
  accent: 'hsl(240 3.7% 15.9%)',
  accentForeground: 'hsl(0 0% 98%)',
  destructive: 'hsl(0 62.8% 30.6%)',
  destructiveForeground: 'hsl(0 0% 98%)',
  border: 'hsl(240 3.7% 15.9%)',
  input: 'hsl(240 3.7% 15.9%)',
  ring: 'hsl(240 4.9% 83.9%)',
}

// Convert camelCase to kebab-case for CSS variables
const toCssVarName = (key: string): string => {
  return `--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode
    return (stored && ['dark', 'gray', 'light', 'custom'].includes(stored))
      ? stored as ThemeMode
      : 'dark'
  })
  const [customColors, setCustomColorsState] = useState<CustomThemeColors>(DEFAULT_CUSTOM_COLORS)
  const [isLoading, setIsLoading] = useState(true)

  // Load theme and custom colors from localStorage
  useEffect(() => {
    const loadTheme = () => {
      try {
        // Load theme preference
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode
        if (savedTheme && ['dark', 'gray', 'light', 'custom'].includes(savedTheme)) {
          setThemeState(savedTheme)
        }

        // Load custom colors
        const savedColors = localStorage.getItem(CUSTOM_COLORS_STORAGE_KEY)
        if (savedColors) {
          const colors = JSON.parse(savedColors) as CustomThemeColors
          setCustomColorsState(colors)
        }
      } catch (error) {
        console.error('Failed to load theme settings:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadTheme()
  }, [])

  // Apply theme to document
  const applyTheme = useCallback((themeMode: ThemeMode, colors: CustomThemeColors) => {
    const root = document.documentElement

    // Remove all theme classes
    root.classList.remove('theme-dark', 'theme-gray', 'theme-light', 'theme-custom')

    // Add new theme class
    root.classList.add(`theme-${themeMode}`)

    // Get colors to apply
    const colorsToApply = themeMode === 'custom' ? colors : THEME_COLORS[themeMode]

    // Apply colors as CSS variables
    Object.entries(colorsToApply).forEach(([key, value]) => {
      if (value) {
        const cssVarName = toCssVarName(key)
        root.style.setProperty(cssVarName, value)
      }
    })

    // For non-custom themes, ensure we use the preset colors
    if (themeMode !== 'custom') {
      const presetColors = THEME_COLORS[themeMode]
      Object.keys(presetColors).forEach((key) => {
        const cssVarName = toCssVarName(key)
        root.style.setProperty(cssVarName, presetColors[key as keyof CustomThemeColors]!)
      })
    }
  }, [])

  // Apply theme when theme or customColors change
  useEffect(() => {
    if (!isLoading) {
      applyTheme(theme, customColors)
    }
  }, [theme, customColors, isLoading, applyTheme])

  const setTheme = useCallback((newTheme: ThemeMode) => {
    setThemeState(newTheme)
    localStorage.setItem(THEME_STORAGE_KEY, newTheme)
  }, [])

  const setCustomColors = useCallback((colors: Partial<CustomThemeColors>) => {
    const newColors = { ...customColors, ...colors }
    setCustomColorsState(newColors)
    localStorage.setItem(CUSTOM_COLORS_STORAGE_KEY, JSON.stringify(newColors))
  }, [customColors])

  const value: ThemeContextType = {
    theme,
    customColors,
    setTheme,
    setCustomColors,
    isLoading,
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
