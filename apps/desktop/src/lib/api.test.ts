import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api, Session } from './api'

// Mock Tauri invoke
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}))

const { invoke } = await import('@tauri-apps/api/core')

describe('api', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('chat', () => {
    it('发送消息并返回响应', async () => {
      const mockResponse = {
        content: 'Hello from assistant',
        session_id: 'session-1',
        model: 'gpt-4',
      }
      vi.mocked(invoke).mockResolvedValueOnce(mockResponse)

      const result = await api.chat({ message: 'Hello', session_id: 'session-1' })

      expect(invoke).toHaveBeenCalledWith('chat', {
        message: 'Hello',
        sessionId: 'session-1',
        userId: 'default',
      })
      expect(result).toEqual(mockResponse)
    })

    it('处理空消息', async () => {
      const mockResponse = {
        content: '',
        session_id: 'session-1',
        model: 'gpt-4',
      }
      vi.mocked(invoke).mockResolvedValueOnce(mockResponse)

      const result = await api.chat({ message: '', session_id: 'session-1' })

      expect(result.content).toBe('')
    })

    it('处理错误响应', async () => {
      vi.mocked(invoke).mockRejectedValueOnce(new Error('Network error'))

      await expect(api.chat({ message: 'Hello' })).rejects.toThrow('Network error')
    })
  })

  describe('getSessions', () => {
    it('获取会话列表', async () => {
      const mockSessions: Session[] = [
        { id: '1', user_id: 'user1', created_at: 123456, updated_at: 123456 },
        { id: '2', user_id: 'user1', created_at: 123457, updated_at: 123457 },
      ]
      vi.mocked(invoke).mockResolvedValueOnce(mockSessions)

      const result = await api.getSessions('user1')

      expect(invoke).toHaveBeenCalledWith('get_sessions', { userId: 'user1' })
      expect(result).toEqual(mockSessions)
    })

    it('处理空会话列表', async () => {
      vi.mocked(invoke).mockResolvedValueOnce([])

      const result = await api.getSessions()

      expect(result).toEqual([])
    })
  })

  describe('getSession', () => {
    it('获取单个会话', async () => {
      const mockSession: Session = {
        id: '1',
        user_id: 'user1',
        created_at: 123456,
        updated_at: 123456,
      }
      vi.mocked(invoke).mockResolvedValueOnce(mockSession)

      const result = await api.getSession('1')

      expect(invoke).toHaveBeenCalledWith('get_session', { sessionId: '1' })
      expect(result).toEqual(mockSession)
    })

    it('处理不存在的会话', async () => {
      vi.mocked(invoke).mockRejectedValueOnce(new Error('Session not found'))

      const result = await api.getSession('nonexistent')

      expect(result).toBeNull()
    })
  })

  describe('deleteSession', () => {
    it('删除会话', async () => {
      vi.mocked(invoke).mockResolvedValueOnce(undefined)

      await api.deleteSession('session-1')

      expect(invoke).toHaveBeenCalledWith('delete_session', { sessionId: 'session-1' })
    })
  })

  describe('getMemory', () => {
    it('获取记忆', async () => {
      const mockMemory = { facts: ['fact1', 'fact2'], history: ['msg1', 'msg2'] }
      vi.mocked(invoke).mockResolvedValueOnce(mockMemory)

      const result = await api.getMemory()

      expect(invoke).toHaveBeenCalledWith('get_memory')
      expect(result).toEqual(mockMemory)
    })
  })

  describe('addMemory', () => {
    it('添加记忆', async () => {
      vi.mocked(invoke).mockResolvedValueOnce(undefined)

      await api.addMemory('new fact')

      expect(invoke).toHaveBeenCalledWith('add_memory', { fact: 'new fact' })
    })
  })

  describe('getConfig', () => {
    it('获取配置', async () => {
      const mockConfig = { model: 'gpt-4', temperature: 0.7 }
      vi.mocked(invoke).mockResolvedValueOnce(mockConfig)

      const result = await api.getConfig()

      expect(invoke).toHaveBeenCalledWith('get_config')
      expect(result).toEqual(mockConfig)
    })
  })

  describe('updateConfig', () => {
    it('更新配置', async () => {
      vi.mocked(invoke).mockResolvedValueOnce(undefined)

      await api.updateConfig({ model: 'gpt-4-turbo' })

      expect(invoke).toHaveBeenCalledWith('update_config', { config: { model: 'gpt-4-turbo' } })
    })
  })

  describe('getTools', () => {
    it('获取可用工具列表', async () => {
      const mockTools = ['file_read', 'file_write', 'web_search']
      vi.mocked(invoke).mockResolvedValueOnce(mockTools)

      const result = await api.getTools()

      expect(invoke).toHaveBeenCalledWith('get_tools')
      expect(result).toEqual(mockTools)
    })
  })
})
