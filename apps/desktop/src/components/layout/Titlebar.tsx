import { useState } from 'react'
import { Minus, Square, X, Settings, MessageSquare, Sun, Moon, Brain, Users } from 'lucide-react'
import { getCurrentWindow } from '@tauri-apps/api/window'
import { useTheme } from '@/contexts/ThemeContext'

interface TitlebarProps {
  onSettingsClick?: () => void
}

export function Titlebar({ onSettingsClick }: TitlebarProps) {
  const [isMaximized, setIsMaximized] = useState(false)
  const { theme, setTheme } = useTheme()

  const handleMinimize = async () => {
    try {
      const window = getCurrentWindow()
      await window.minimize()
    } catch (error) {
      console.error('Failed to minimize window:', error)
    }
  }

  const handleMaximize = async () => {
    try {
      const window = getCurrentWindow()
      const maximized = await window.isMaximized()
      if (maximized) {
        await window.unmaximize()
        setIsMaximized(false)
      } else {
        await window.maximize()
        setIsMaximized(true)
      }
    } catch (error) {
      console.error('Failed to maximize/unmaximize window:', error)
    }
  }

  const handleClose = async () => {
    try {
      const window = getCurrentWindow()
      await window.close()
    } catch (error) {
      console.error('Failed to close window:', error)
    }
  }

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('gray')
    } else {
      setTheme('light')
    }
  }

  const getThemeIcon = () => {
    if (theme === 'light') return Sun
    if (theme === 'dark') return Moon
    return Sun // gray and custom use sun
  }

  const ThemeIcon = getThemeIcon()

  return (
    <div
      className="h-11 bg-background border-b border-border flex items-center justify-between select-none"
      data-tauri-drag-region
    >
      {/* Left side - App title + Theme toggle */}
      <div className="flex items-center pl-4 gap-2" data-tauri-drag-region>
        <MessageSquare size={16} className="text-foreground/60" />
        <span className="text-sm font-medium text-foreground/80">SocratX</span>

        {/* Theme toggle button */}
        <button
          onClick={toggleTheme}
          className="ml-2 p-1.5 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
          title={`Current theme: ${theme}. Click to cycle themes.`}
          type="button"
          data-tauri-drag-region={false}
        >
          <ThemeIcon size={14} className="text-foreground/70" />
        </button>
      </div>

      {/* Center - Drag region (invisible but functional) */}
      <div className="flex-1" data-tauri-drag-region />

      {/* Right side - Navigation + Window controls */}
      <div className="flex items-center pr-3 gap-1">
        {/* Navigation buttons */}
        <button
          onClick={() => {/* Navigate to agents */}}
          className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
          title="Agents"
          type="button"
          data-tauri-drag-region={false}
        >
          <Brain size={16} />
        </button>

        <button
          onClick={() => {/* Navigate to memory */}}
          className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
          title="Memory"
          type="button"
          data-tauri-drag-region={false}
        >
          <Users size={16} />
        </button>

        {onSettingsClick && (
          <button
            onClick={onSettingsClick}
            className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
            title="Settings"
            type="button"
            data-tauri-drag-region={false}
          >
            <Settings size={16} />
          </button>
        )}

        {/* Window controls - Right side (Windows style) */}
        <div className="flex items-center space-x-2 pl-2">
          {/* Minimize button */}
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              handleMinimize()
            }}
            className="w-11 h-8 flex items-center justify-center hover:bg-muted/50 transition-colors"
            title="Minimize"
            type="button"
            data-tauri-drag-region={false}
          >
            <Minus size={14} className="text-foreground/70" />
          </button>

          {/* Maximize button */}
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              handleMaximize()
            }}
            className="w-11 h-8 flex items-center justify-center hover:bg-muted/50 transition-colors"
            title={isMaximized ? "Restore" : "Maximize"}
            type="button"
            data-tauri-drag-region={false}
          >
            <Square size={12} className="text-foreground/70" />
          </button>

          {/* Close button */}
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              handleClose()
            }}
            className="w-11 h-8 flex items-center justify-center hover:bg-red-600 hover:text-white transition-colors"
            title="Close"
            type="button"
            data-tauri-drag-region={false}
          >
            <X size={14} className="text-foreground/70" />
          </button>
        </div>
      </div>
    </div>
  )
}
