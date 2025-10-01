/**
 * Chat and messaging type definitions
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: number
}

export interface ChatRequest {
  messages: ChatMessage[]
  startup_id: string
  agent_type?: string
}

export interface StreamChunk {
  content?: string
  error?: string
}
