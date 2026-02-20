import { useState, useCallback } from 'react'
import { Plus, Search, Star, MessageSquare, Trash2, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useTabContext } from '@/contexts/TabContext'

interface Session {
  id: string
  title: string
  updatedAt: Date
  isPinned: boolean
}

interface SidebarProps {
  className?: string
  collapsed?: boolean
  onToggleCollapse?: () => void
}

export function Sidebar({ className, collapsed = false, onToggleCollapse }: SidebarProps) {
  const { addTab, tabs } = useTabContext()
  const [searchQuery, setSearchQuery] = useState('')
  const [sessions, setSessions] = useState<Session[]>([
    {
      id: '1',
      title: 'Welcome Chat',
      updatedAt: new Date(),
      isPinned: false
    }
  ])
  const [showPinnedOnly, setShowPinnedOnly] = useState(false)

  // Create new chat session
  const handleNewChat = useCallback(() => {
    const newSession: Session = {
      id: Date.now().toString(),
      title: 'New Chat',
      updatedAt: new Date(),
      isPinned: false
    }
    setSessions((prev) => [newSession, ...prev])

    // Also create a new tab
    addTab({
      type: 'chat',
      title: 'New Chat',
      status: 'idle',
      hasUnsavedChanges: false
    })
  }, [addTab])

  // Delete session
  const handleDeleteSession = useCallback((sessionId: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== sessionId))
  }, [])

  // Toggle pin
  const handleTogglePin = useCallback((sessionId: string) => {
    setSessions((prev) =>
      prev.map((s) =>
        s.id === sessionId ? { ...s, isPinned: !s.isPinned } : s
      )
    )
  }, [])

  // Filter sessions
  const filteredSessions = sessions
    .filter((session) => {
      if (showPinnedOnly && !session.isPinned) return false
      if (searchQuery && !session.title.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }
      return true
    })
    .sort((a, b) => {
      // Pinned sessions first
      if (a.isPinned && !b.isPinned) return -1
      if (!a.isPinned && b.isPinned) return 1
      // Then by date (newest first)
      return b.updatedAt.getTime() - a.updatedAt.getTime()
    })

  const pinnedSessions = filteredSessions.filter((s) => s.isPinned)
  const otherSessions = filteredSessions.filter((s) => !s.isPinned)

  return (
    <div
      className={cn(
        'flex flex-col border-r border-border bg-muted/30 transition-all duration-300',
        collapsed ? 'w-12' : 'w-64',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!collapsed && (
          <h2 className="text-sm font-semibold text-foreground">Chats</h2>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-1 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          type="button"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Search bar */}
      {!collapsed && (
        <div className="p-3 space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-9 text-sm"
            />
          </div>
          <Button
            onClick={handleNewChat}
            className="w-full justify-center gap-2"
            size="sm"
          >
            <Plus size={14} />
            New Chat
          </Button>
        </div>
      )}

      {/* Sessions list */}
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-4 py-2">
          {/* Pinned sessions */}
          {pinnedSessions.length > 0 && (
            <div>
              <div className="flex items-center gap-1 px-2 mb-2">
                <Star size={12} className="text-muted-foreground" />
                {!collapsed && (
                  <span className="text-xs text-muted-foreground font-medium">Pinned</span>
                )}
              </div>
              {pinnedSessions.map((session) => (
                <SessionItem
                  key={session.id}
                  session={session}
                  collapsed={collapsed}
                  onDelete={handleDeleteSession}
                  onTogglePin={handleTogglePin}
                />
              ))}
            </div>
          )}

          {/* Other sessions */}
          {otherSessions.length > 0 && (
            <div>
              {!collapsed && (
                <div className="px-2 mb-2">
                  <span className="text-xs text-muted-foreground font-medium">Recent</span>
                </div>
              )}
              {otherSessions.map((session) => (
                <SessionItem
                  key={session.id}
                  session={session}
                  collapsed={collapsed}
                  onDelete={handleDeleteSession}
                  onTogglePin={handleTogglePin}
                />
              ))}
            </div>
          )}

          {filteredSessions.length === 0 && (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              {searchQuery ? 'No chats found' : 'No chats yet'}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer - Filter toggle */}
      {!collapsed && (
        <div className="p-3 border-t border-border">
          <button
            onClick={() => setShowPinnedOnly(!showPinnedOnly)}
            className={cn(
              'w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors',
              showPinnedOnly && 'bg-accent text-accent-foreground'
            )}
            type="button"
          >
            <Star size={14} className={showPinnedOnly ? 'fill-current' : ''} />
            {showPinnedOnly ? 'Show All' : 'Show Pinned Only'}
          </button>
        </div>
      )}
    </div>
  )
}

interface SessionItemProps {
  session: Session
  collapsed: boolean
  onDelete: (id: string) => void
  onTogglePin: (id: string) => void
}

function SessionItem({ session, collapsed, onDelete, onTogglePin }: SessionItemProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className={cn(
        'group relative flex items-center gap-2 px-2 py-2 rounded-md hover:bg-accent/50 cursor-pointer transition-colors',
        isHovered && 'bg-accent/50'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Icon */}
      <MessageSquare size={16} className="shrink-0 text-muted-foreground" />

      {/* Title */}
      {!collapsed && (
        <span className="flex-1 text-sm truncate text-foreground">
          {session.title}
        </span>
      )}

      {/* Actions - show on hover */}
      {(isHovered || collapsed) && (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation()
              onTogglePin(session.id)
            }}
            className="p-1 rounded hover:bg-muted transition-colors"
            title={session.isPinned ? 'Unpin' : 'Pin'}
            type="button"
          >
            <Star
              size={12}
              className={session.isPinned ? 'fill-primary' : 'text-muted-foreground'}
            />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete(session.id)
            }}
            className="p-1 rounded hover:bg-destructive/20 hover:text-destructive transition-colors"
            title="Delete"
            type="button"
          >
            <Trash2 size={12} />
          </button>
        </div>
      )}
    </div>
  )
}
