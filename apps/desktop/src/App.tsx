import { ThemeProvider } from './contexts/ThemeContext'
import { TabProvider, useTabContext } from './contexts/TabContext'
import { MainLayout } from './components/layout'
import { TabManager } from './components/layout/TabManager'
import { Sidebar } from './components/layout/Sidebar'
import ChatContainer from './components/chat/ChatContainer'
import { Settings } from 'lucide-react'
import { useState } from 'react'

function AppContent() {
  const { addTab } = useTabContext()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const handleNewTab = () => {
    addTab({
      type: 'chat',
      title: 'New Chat',
      status: 'idle',
      hasUnsavedChanges: false
    })
  }

  const handleSettingsClick = () => {
    addTab({
      type: 'settings',
      title: 'Settings',
      status: 'idle',
      hasUnsavedChanges: false
    })
  }

  return (
    <MainLayout onSettingsClick={handleSettingsClick}>
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main content area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <TabManager onNewTab={handleNewTab} />
          <div className="flex-1 overflow-auto">
            <ChatContainer />
          </div>
        </div>
      </div>
    </MainLayout>
  )
}

function App() {
  return (
    <ThemeProvider>
      <TabProvider>
        <AppContent />
      </TabProvider>
    </ThemeProvider>
  )
}

export default App
