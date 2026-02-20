import { useState, useRef, useEffect } from 'react'
import { X, Plus, MessageSquare, Settings, Brain, Loader2, AlertCircle } from 'lucide-react'
import { useTabContext, type Tab } from '@/contexts/TabContext'
import { cn } from '@/lib/utils'

interface TabItemProps {
  tab: Tab
  isActive: boolean
  onClose: (id: string) => void
  onClick: (id: string) => void
}

const TabItem: React.FC<TabItemProps> = ({ tab, isActive, onClose, onClick }) => {
  const [isHovered, setIsHovered] = useState(false)

  const getIcon = () => {
    switch (tab.type) {
      case 'chat':
        return MessageSquare
      case 'settings':
        return Settings
      case 'memory':
        return Brain
      case 'agents':
        return Brain
      default:
        return MessageSquare
    }
  }

  const getStatusIndicator = () => {
    switch (tab.status) {
      case 'loading':
        return <Loader2 className="w-3 h-3 animate-spin text-primary" />
      case 'error':
        return <AlertCircle className="w-3 h-3 text-destructive" />
      default:
        return null
    }
  }

  const Icon = getIcon()
  const statusIndicator = getStatusIndicator()

  return (
    <button
      type="button"
      onClick={() => onClick(tab.id)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        'relative flex items-center gap-2 text-sm cursor-pointer select-none group',
        'transition-all duration-200 overflow-hidden border-r border-border/20',
        'min-w-[120px] max-w-[200px] h-9 px-3',
        isActive
          ? 'bg-background text-foreground border-b-2 border-b-primary'
          : 'bg-muted/30 text-muted-foreground hover:bg-muted/50 hover:text-foreground border-b-2 border-b-transparent'
      )}
    >
      {/* Tab Icon */}
      <div className="flex-shrink-0">
        <Icon className="w-4 h-4" />
      </div>

      {/* Tab Title */}
      <span className="flex-1 truncate text-xs font-medium min-w-0">
        {tab.title}
      </span>

      {/* Status Indicators */}
      <div className="flex items-center gap-1.5 flex-shrink-0 w-6 justify-end">
        {statusIndicator}
        {tab.hasUnsavedChanges && !statusIndicator && (
          <span
            className="w-1.5 h-1.5 bg-primary rounded-full"
            title="Unsaved changes"
          />
        )}
      </div>

      {/* Close Button */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          onClose(tab.id)
        }}
        className={cn(
          'flex-shrink-0 w-4 h-4 flex items-center justify-center rounded-sm',
          'transition-all duration-150 hover:bg-destructive/20 hover:text-destructive',
          'focus:outline-none',
          (isHovered || isActive) ? 'opacity-100' : 'opacity-0'
        )}
        title={`Close ${tab.title}`}
        tabIndex={-1}
      >
        <X className="w-3 h-3" />
      </button>
    </button>
  )
}

interface TabManagerProps {
  className?: string
  onNewTab?: () => void
}

export function TabManager({ className, onNewTab }: TabManagerProps) {
  const {
    tabs,
    activeTabId,
    removeTab,
    setActiveTab,
    reorderTabs,
    closeAllTabs
  } = useTabContext()

  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [showLeftScroll, setShowLeftScroll] = useState(false)
  const [showRightScroll, setShowRightScroll] = useState(false)

  // Check scroll position
  const checkScroll = () => {
    const container = scrollContainerRef.current
    if (container) {
      setShowLeftScroll(container.scrollLeft > 0)
      setShowRightScroll(
        container.scrollLeft < container.scrollWidth - container.clientWidth - 1
      )
    }
  }

  useEffect(() => {
    const container = scrollContainerRef.current
    if (container) {
      container.addEventListener('scroll', checkScroll)
      window.addEventListener('resize', checkScroll)
      checkScroll()

      return () => {
        container.removeEventListener('scroll', checkScroll)
        window.removeEventListener('resize', checkScroll)
      }
    }
  }, [tabs])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+T - New tab
      if (e.ctrlKey && e.key === 't') {
        e.preventDefault()
        onNewTab?.()
      }

      // Ctrl+W - Close current tab
      if (e.ctrlKey && e.key === 'w') {
        e.preventDefault()
        if (activeTabId) {
          removeTab(activeTabId)
        }
      }

      // Ctrl+Tab - Next tab
      if (e.ctrlKey && e.key === 'Tab' && !e.shiftKey) {
        e.preventDefault()
        const currentIndex = tabs.findIndex(tab => tab.id === activeTabId)
        const nextIndex = (currentIndex + 1) % tabs.length
        if (tabs[nextIndex]) {
          setActiveTab(tabs[nextIndex].id)
        }
      }

      // Ctrl+Shift+Tab - Previous tab
      if (e.ctrlKey && e.shiftKey && e.key === 'Tab') {
        e.preventDefault()
        const currentIndex = tabs.findIndex(tab => tab.id === activeTabId)
        const prevIndex = currentIndex <= 0 ? tabs.length - 1 : currentIndex - 1
        if (tabs[prevIndex]) {
          setActiveTab(tabs[prevIndex].id)
        }
      }

      // Ctrl+1-9 - Switch to specific tab
      if (e.ctrlKey && e.key >= '1' && e.key <= '9') {
        e.preventDefault()
        const tabIndex = parseInt(e.key) - 1
        if (tabs[tabIndex]) {
          setActiveTab(tabs[tabIndex].id)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [tabs, activeTabId, removeTab, setActiveTab, onNewTab])

  const scroll = (direction: 'left' | 'right') => {
    const container = scrollContainerRef.current
    if (container) {
      const scrollAmount = 200
      container.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      })
    }
  }

  return (
    <div className={cn('flex items-center bg-muted/30 border-b border-border', className)}>
      {/* Scroll Left Button */}
      {showLeftScroll && (
        <button
          type="button"
          onClick={() => scroll('left')}
          className="flex-shrink-0 w-6 h-9 flex items-center justify-center hover:bg-muted/50 transition-colors"
          aria-label="Scroll tabs left"
        >
          <div className="w-1 h-1 bg-foreground/50 rotate-45" />
        </button>
      )}

      {/* Tabs Container */}
      <div
        ref={scrollContainerRef}
        className="flex-1 flex items-center overflow-x-auto overflow-y-hidden scrollbar-hide"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        <div className="flex items-center">
          {tabs.map((tab) => (
            <TabItem
              key={tab.id}
              tab={tab}
              isActive={tab.id === activeTabId}
              onClose={removeTab}
              onClick={setActiveTab}
            />
          ))}
        </div>
      </div>

      {/* Scroll Right Button */}
      {showRightScroll && (
        <button
          type="button"
          onClick={() => scroll('right')}
          className="flex-shrink-0 w-6 h-9 flex items-center justify-center hover:bg-muted/50 transition-colors"
          aria-label="Scroll tabs right"
        >
          <div className="w-1 h-1 bg-foreground/50 -rotate-45" />
        </button>
      )}

      {/* New Tab Button */}
      <button
        type="button"
        onClick={onNewTab}
        className="flex-shrink-0 w-8 h-8 mx-1 flex items-center justify-center rounded-md hover:bg-muted/50 transition-colors"
        title="New tab (Ctrl+T)"
        aria-label="New tab"
      >
        <Plus className="w-4 h-4" />
      </button>

      {/* Tab Count Badge */}
      <span className="text-xs text-muted-foreground px-2">
        {tabs.length}
      </span>
    </div>
  )
}
