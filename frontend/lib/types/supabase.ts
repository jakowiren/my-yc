// TypeScript types for Supabase database schema

export interface Startup {
  id: string
  user_id: string
  title: string | null
  status: 'active' | 'archived' | 'deleted'
  metadata: Record<string, any>
  conversation_context: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  startup_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: Record<string, any>
  created_at: string
}

export interface StartupInsert {
  user_id: string
  title?: string
  status?: 'active' | 'archived' | 'deleted'
  metadata?: Record<string, any>
  conversation_context?: Record<string, any>
}

export interface MessageInsert {
  startup_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata?: Record<string, any>
}

export interface StartupUpdate {
  title?: string
  status?: 'active' | 'archived' | 'deleted'
  metadata?: Record<string, any>
  conversation_context?: Record<string, any>
}

export interface Database {
  public: {
    Tables: {
      startups: {
        Row: Startup
        Insert: StartupInsert
        Update: StartupUpdate
      }
      messages: {
        Row: Message
        Insert: MessageInsert
        Update: Partial<MessageInsert>
      }
    }
  }
}