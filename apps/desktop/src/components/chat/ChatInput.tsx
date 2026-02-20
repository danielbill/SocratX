import { useState, KeyboardEvent } from 'react'
import { Button } from '../ui/button'
import { Textarea } from '../ui/textarea'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex gap-2 p-4 border-t">
      <Textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
        className="min-h-[60px] resize-none"
        disabled={disabled}
      />
      <Button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="px-4"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  )
}
