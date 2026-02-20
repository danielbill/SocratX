import { useState, useRef, useEffect } from 'react'
import { api, Message } from '@/lib/api'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { ScrollArea } from '../ui/scroll-area'

interface ChatContainerProps {
  sessionId?: string
}

export default function ChatContainer({ sessionId = 'default' }: ChatContainerProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: Date.now(),
    }
    setMessages((prev: Message[]) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call API
      const responseContent = await api.chat({
        message: content,
        session_id: sessionId,
        user_id: 'default',
      })

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: responseContent,
        timestamp: Date.now(),
      }
      setMessages((prev: Message[]) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        timestamp: Date.now(),
      }
      setMessages((prev: Message[]) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <ScrollArea className="flex-1 px-4">
        <div ref={scrollRef} className="py-4">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground py-12">
              <p className="text-lg mb-2">👋 欢迎使用 SocratX</p>
              <p className="text-sm">开始对话吧...</p>
            </div>
          ) : (
            messages.map((message: Message, index: number) => (
              <ChatMessage key={index} message={message} />
            ))
          )}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-muted rounded-lg p-3">
                <p className="text-sm">Thinking...</p>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  )
}
