import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react'

export type TabType = 'chat' | 'settings' | 'memory' | 'agents'

export interface Tab {
  id: string
  type: TabType
  title: string
  sessionId?: string
  status: 'active' | 'idle' | 'loading'
  hasUnsavedChanges: boolean
  order: number
  icon?: string
  createdAt: Date
  updatedAt: Date
}

interface TabContextType {
  tabs: Tab[]
  activeTabId: string | null
  addTab: (tab: Omit<Tab, 'id' | 'order' | 'createdAt' | 'updatedAt'>) => string
  removeTab: (id: string) => void
  updateTab: (id: string, updates: Partial<Tab>) => void
  setActiveTab: (id: string) => void
  reorderTabs: (startIndex: number, endIndex: number) => void
  getTabById: (id: string) => Tab | undefined
  closeAllTabs: () => void
  getTabsByType: (type: TabType) => Tab[]
}

const TabContext = createContext<TabContextType | undefined>(undefined)

const TABS_STORAGE_KEY = 'socratx_tabs'
const ACTIVE_TAB_STORAGE_KEY = 'socratx_active_tab'
const MAX_TABS = 20

const generateTabId = (): string => {
  return `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Save tabs to localStorage
const saveTabs = (tabs: Tab[], activeTabId: string | null) => {
  try {
    localStorage.setItem(TABS_STORAGE_KEY, JSON.stringify(tabs))
    if (activeTabId) {
      localStorage.setItem(ACTIVE_TAB_STORAGE_KEY, activeTabId)
    } else {
      localStorage.removeItem(ACTIVE_TAB_STORAGE_KEY)
    }
  } catch (error) {
    console.error('Failed to save tabs:', error)
  }
}

// Load tabs from localStorage
const loadTabs = (): { tabs: Tab[]; activeTabId: string | null } => {
  try {
    const savedTabs = localStorage.getItem(TABS_STORAGE_KEY)
    const savedActiveTab = localStorage.getItem(ACTIVE_TAB_STORAGE_KEY)

    if (savedTabs) {
      const tabs = JSON.parse(savedTabs) as Tab[]
      // Convert date strings back to Date objects
      tabs.forEach(tab => {
        tab.createdAt = new Date(tab.createdAt)
        tab.updatedAt = new Date(tab.updatedAt)
      })
      return {
        tabs,
        activeTabId: savedActiveTab || null
      }
    }
  } catch (error) {
    console.error('Failed to load tabs:', error)
  }

  return { tabs: [], activeTabId: null }
}

export const TabProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [tabs, setTabs] = useState<Tab[]>([])
  const [activeTabId, setActiveTabId] = useState<string | null>(null)
  const isInitialized = useRef(false)
  const saveTimeoutRef = useRef<NodeJS.Timeout>()

  // Load tabs from storage on mount
  useEffect(() => {
    if (isInitialized.current) return
    isInitialized.current = true

    const { tabs: savedTabs, activeTabId: savedActiveTabId } = loadTabs()

    if (savedTabs.length > 0) {
      setTabs(savedTabs)
      setActiveTabId(savedActiveTabId)
    } else {
      // Create default chat tab if no saved tabs
      const defaultTab: Tab = {
        id: generateTabId(),
        type: 'chat',
        title: 'New Chat',
        status: 'idle',
        hasUnsavedChanges: false,
        order: 0,
        createdAt: new Date(),
        updatedAt: new Date()
      }
      setTabs([defaultTab])
      setActiveTabId(defaultTab.id)
    }
  }, [])

  // Save tabs to localStorage with debounce
  useEffect(() => {
    if (!isInitialized.current) return

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }

    saveTimeoutRef.current = setTimeout(() => {
      saveTabs(tabs, activeTabId)
    }, 500)

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [tabs, activeTabId])

  // Save tabs immediately when window is about to close
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (isInitialized.current && tabs.length > 0) {
        saveTabs(tabs, activeTabId)
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      if (isInitialized.current && tabs.length > 0) {
        saveTabs(tabs, activeTabId)
      }
    }
  }, [tabs, activeTabId])

  const addTab = useCallback((tabData: Omit<Tab, 'id' | 'order' | 'createdAt' | 'updatedAt'>): string => {
    if (tabs.length >= MAX_TABS) {
      throw new Error(`Maximum number of tabs (${MAX_TABS}) reached`)
    }

    const newTab: Tab = {
      ...tabData,
      id: generateTabId(),
      order: tabs.length,
      createdAt: new Date(),
      updatedAt: new Date()
    }

    setTabs(prevTabs => [...prevTabs, newTab])
    setActiveTabId(newTab.id)
    return newTab.id
  }, [tabs.length])

  const removeTab = useCallback((id: string) => {
    setTabs(prevTabs => {
      const filteredTabs = prevTabs.filter(tab => tab.id !== id)

      // Reorder remaining tabs
      const reorderedTabs = filteredTabs.map((tab, index) => ({
        ...tab,
        order: index
      }))

      // Update active tab if necessary
      if (activeTabId === id && reorderedTabs.length > 0) {
        const removedTabIndex = prevTabs.findIndex(tab => tab.id === id)
        const newActiveIndex = Math.min(removedTabIndex, reorderedTabs.length - 1)
        setActiveTabId(reorderedTabs[newActiveIndex].id)
      } else if (reorderedTabs.length === 0) {
        // Create a new chat tab if all tabs are closed
        const newTab: Tab = {
          id: generateTabId(),
          type: 'chat',
          title: 'New Chat',
          status: 'idle',
          hasUnsavedChanges: false,
          order: 0,
          createdAt: new Date(),
          updatedAt: new Date()
        }
        setTimeout(() => {
          setTabs([newTab])
          setActiveTabId(newTab.id)
        }, 0)
      }

      return reorderedTabs
    })
  }, [activeTabId])

  const updateTab = useCallback((id: string, updates: Partial<Tab>) => {
    setTabs(prevTabs =>
      prevTabs.map(tab =>
        tab.id === id
          ? { ...tab, ...updates, updatedAt: new Date() }
          : tab
      )
    )
  }, [])

  const setActiveTab = useCallback((id: string) => {
    if (tabs.find(tab => tab.id === id)) {
      setActiveTabId(id)
    }
  }, [tabs])

  const reorderTabs = useCallback((startIndex: number, endIndex: number) => {
    setTabs(prevTabs => {
      const newTabs = [...prevTabs]
      const [removed] = newTabs.splice(startIndex, 1)
      newTabs.splice(endIndex, 0, removed)

      // Update order property
      return newTabs.map((tab, index) => ({
        ...tab,
        order: index
      }))
    })
  }, [])

  const getTabById = useCallback((id: string): Tab | undefined => {
    return tabs.find(tab => tab.id === id)
  }, [tabs])

  const closeAllTabs = useCallback(() => {
    setTabs([])
    setActiveTabId(null)
    localStorage.removeItem(TABS_STORAGE_KEY)
    localStorage.removeItem(ACTIVE_TAB_STORAGE_KEY)

    // Create a new default tab
    const newTab: Tab = {
      id: generateTabId(),
      type: 'chat',
      title: 'New Chat',
      status: 'idle',
      hasUnsavedChanges: false,
      order: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    }
    setTimeout(() => {
      setTabs([newTab])
      setActiveTabId(newTab.id)
    }, 0)
  }, [])

  const getTabsByType = useCallback((type: TabType): Tab[] => {
    return tabs.filter(tab => tab.type === type)
  }, [tabs])

  const value: TabContextType = {
    tabs,
    activeTabId,
    addTab,
    removeTab,
    updateTab,
    setActiveTab,
    reorderTabs,
    getTabById,
    closeAllTabs,
    getTabsByType
  }

  return (
    <TabContext.Provider value={value}>
      {children}
    </TabContext.Provider>
  )
}

export const useTabContext = () => {
  const context = useContext(TabContext)
  if (!context) {
    throw new Error('useTabContext must be used within a TabProvider')
  }
  return context
}
