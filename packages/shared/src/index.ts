// Shared types for SocratX

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  metadata?: Record<string, unknown>
}

export interface Session {
  id: string
  project_id?: string
  messages: Message[]
  created_at?: string
  updated_at?: string
}

export interface Project {
  id: string
  path: string
  sessions: string[]
  created_at: number
  most_recent_session?: number
}

export interface ChatRequest {
  message: string
  session_id: string
  model?: string
}

export interface ChatResponse {
  reply: string
  sources?: string[]
  metadata?: Record<string, unknown>
}

export interface AgentConfig {
  name: string
  system_prompt: string
  model: string
  temperature?: number
  max_tokens?: number
}
