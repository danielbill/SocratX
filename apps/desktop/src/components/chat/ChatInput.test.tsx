import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import ChatInput from './ChatInput'

describe('ChatInput', () => {
  const defaultProps = {
    onSend: vi.fn(),
    disabled: false,
  }

  it('渲染输入框和发送按钮', () => {
    render(<ChatInput {...defaultProps} />)
    
    expect(screen.getByPlaceholderText(/输入你的问题/i)).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('输入框初始值为空', () => {
    render(<ChatInput {...defaultProps} />)
    
    expect(screen.getByPlaceholderText(/输入你的问题/i)).toHaveValue('')
  })

  it('点击发送按钮触发回调', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText(/输入你的问题/i), 'Hello')
    await user.click(screen.getByRole('button'))

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello')
  })

  it('发送后清空输入框', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    const input = screen.getByPlaceholderText(/输入你的问题/i)
    await user.type(input, 'Hello')
    await user.click(screen.getByRole('button'))

    expect(input).toHaveValue('')
  })

  it('禁用状态下按钮不可点击', () => {
    render(<ChatInput {...defaultProps} disabled />)
    
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('禁用状态下无法发送消息', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} disabled />)

    await user.type(screen.getByPlaceholderText(/输入你的问题/i), 'Hello')
    await user.click(screen.getByRole('button'))

    expect(defaultProps.onSend).not.toHaveBeenCalled()
  })

  it('按 Enter 键发送消息', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText(/输入你的问题/i), 'Hello{Enter}')

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello')
  })

  it('Shift+Enter 换行不发送', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    const input = screen.getByPlaceholderText(/输入你的问题/i)
    await user.type(input, 'Hello{Shift>}{Enter}{/Shift}')

    expect(defaultProps.onSend).not.toHaveBeenCalled()
    expect(input).toHaveValue('Hello\n')
  })

  it('空消息不发送', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.click(screen.getByRole('button'))

    expect(defaultProps.onSend).not.toHaveBeenCalled()
  })

  it('只包含空格的消息不发送', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText(/输入你的问题/i), '   ')
    await user.click(screen.getByRole('button'))

    expect(defaultProps.onSend).not.toHaveBeenCalled()
  })

  it('修剪消息前后空格', async () => {
    const user = userEvent.setup()
    render(<ChatInput {...defaultProps} />)

    await user.type(screen.getByPlaceholderText(/输入你的问题/i), '  Hello  ')
    await user.click(screen.getByRole('button'))

    expect(defaultProps.onSend).toHaveBeenCalledWith('Hello')
  })
})
