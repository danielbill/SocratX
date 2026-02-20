import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ChatMessage from './ChatMessage'
import { Message } from '@/lib/api'

describe('ChatMessage', () => {
  const createUserMessage = (content: string): Message => ({
    role: 'user',
    content,
    timestamp: Date.now(),
  })

  const createAssistantMessage = (content: string): Message => ({
    role: 'assistant',
    content,
    timestamp: Date.now(),
  })

  it('渲染用户消息', () => {
    const message = createUserMessage('Hello from user')
    render(<ChatMessage message={message} />)

    expect(screen.getByText('Hello from user')).toBeInTheDocument()
  })

  it('渲染助手消息', () => {
    const message = createAssistantMessage('Hello from assistant')
    render(<ChatMessage message={message} />)

    expect(screen.getByText('Hello from assistant')).toBeInTheDocument()
  })

  it('用户消息靠右对齐', () => {
    const message = createUserMessage('User message')
    const { container } = render(<ChatMessage message={message} />)

    expect(container.firstChild).toHaveClass('justify-end')
  })

  it('助手消息靠左对齐', () => {
    const message = createAssistantMessage('Assistant message')
    const { container } = render(<ChatMessage message={message} />)

    expect(container.firstChild).toHaveClass('justify-start')
  })

  it('显示时间戳', () => {
    const message = createUserMessage('Test message')
    render(<ChatMessage message={message} />)

    // 时间戳应该被渲染（作为 span 元素）
    const timestamp = screen.getByText((content) => {
      return /\d{1,2}:\d{2}:\d{2}/.test(content)
    })
    expect(timestamp).toBeInTheDocument()
  })

  it('处理多行消息', () => {
    const message = createUserMessage('Line 1\nLine 2\nLine 3')
    render(<ChatMessage message={message} />)

    const content = screen.getByText('Line 1\nLine 2\nLine 3')
    expect(content).toBeInTheDocument()
  })

  it('处理空消息', () => {
    const message = createUserMessage('')
    render(<ChatMessage message={message} />)

    expect(screen.getByText('')).toBeInTheDocument()
  })

  it('处理长消息', () => {
    const longContent = 'a'.repeat(1000)
    const message = createUserMessage(longContent)
    render(<ChatMessage message={message} />)

    expect(screen.getByText(longContent)).toBeInTheDocument()
  })

  it('使用正确的样式类', () => {
    const message = createUserMessage('Test')
    const { container } = render(<ChatMessage message={message} />)

    const messageDiv = container.querySelector('div')
    expect(messageDiv).toHaveClass('rounded-lg', 'p-3', 'max-w-[80%]')
  })
})
