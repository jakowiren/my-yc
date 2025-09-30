// TypeScript types for Supabase database schema
import { StartupDesignDoc } from '../ai/design-doc-template'

export type ProjectStatus = 'designing' | 'design_ready' | 'workspace_initializing' | 'workspace_ready' | 'project_creating' | 'completed' | 'error'

export interface Startup {
  id: string
  user_id: string
  title: string | null
  status: 'active' | 'archived' | 'deleted'
  metadata: Record<string, any>
  conversation_context: Record<string, any>
  design_doc: StartupDesignDoc | null
  project_status: ProjectStatus
  github_url: string | null
  modal_project_id: string | null
  spawned_at: string | null
  error_details: string | null
  ceo_status: 'not_initialized' | 'initializing' | 'ready' | 'error' | null
  container_endpoint: string | null
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
  design_doc?: StartupDesignDoc | null
  project_status?: ProjectStatus
  github_url?: string | null
  modal_project_id?: string | null
  error_details?: string | null
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
  design_doc?: StartupDesignDoc | null
  project_status?: ProjectStatus
  github_url?: string | null
  modal_project_id?: string | null
  error_details?: string | null
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