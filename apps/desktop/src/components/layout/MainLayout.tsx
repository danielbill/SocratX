import { ReactNode } from 'react'
import { Titlebar } from './Titlebar'

interface MainLayoutProps {
  children: ReactNode
  onSettingsClick?: () => void
}

export function MainLayout({ children, onSettingsClick }: MainLayoutProps) {
  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      {/* Custom Titlebar */}
      <Titlebar onSettingsClick={onSettingsClick} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Content area */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
