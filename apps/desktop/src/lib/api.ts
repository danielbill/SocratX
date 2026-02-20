// API 封装层 - Tauri 命令调用

import { invoke } from '@tauri-apps/api/core';

// ========== 类型定义 ==========

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: number;
}

export interface Session {
  id: string;
  user_id: string;
  created_at: number;
  updated_at: number;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  content: string;
  session_id: string;
  model: string;
  tool_calls?: ToolCall[];
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface Memory {
  facts: string[];
  history: string[];
}

// ========== API 客户端 ==========

export const api = {
  // 聊天
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return await invoke<ChatResponse>('chat', {
      message: request.message,
      sessionId: request.session_id || 'default',
      userId: request.user_id || 'default',
    });
  },

  // 获取会话列表
  async getSessions(userId?: string): Promise<Session[]> {
    return await invoke<Session[]>('get_sessions', {
      userId: userId || 'default',
    });
  },

  // 获取会话详情
  async getSession(sessionId: string): Promise<Session | null> {
    try {
      return await invoke<Session>('get_session', { sessionId });
    } catch {
      return null;
    }
  },

  // 删除会话
  async deleteSession(sessionId: string): Promise<void> {
    await invoke('delete_session', { sessionId });
  },

  // 获取记忆
  async getMemory(): Promise<Memory> {
    return await invoke<Memory>('get_memory');
  },

  // 添加记忆
  async addMemory(fact: string): Promise<void> {
    await invoke('add_memory', { fact });
  },

  // 获取配置
  async getConfig(): Promise<Record<string, unknown>> {
    return await invoke<Record<string, unknown>>('get_config');
  },

  // 更新配置
  async updateConfig(config: Record<string, unknown>): Promise<void> {
    await invoke('update_config', { config });
  },

  // 获取可用工具
  async getTools(): Promise<string[]> {
    return await invoke<string[]>('get_tools');
  },
};

// ========== 工具函数 ==========

export function formatMessage(role: Message['role'], content: string): Message {
  return {
    role,
    content,
    timestamp: Date.now(),
  };
}

export function isUserMessage(message: Message): boolean {
  return message.role === 'user';
}

export function isAssistantMessage(message: Message): boolean {
  return message.role === 'assistant';
}
