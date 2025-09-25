import { z } from 'zod'

// Project schemas
export const ProjectIdeaSchema = z.object({
  title: z.string().min(1).max(100),
  description: z.string().min(10).max(1000),
  category: z.string().optional(),
  target_market: z.string().optional(),
})

export const ProjectStatusSchema = z.object({
  project_id: z.string().uuid(),
  status: z.enum(['spawning', 'running', 'sleeping', 'error']),
  progress: z.number().min(0).max(100),
  current_task: z.string().optional(),
  agents_active: z.array(z.string()),
  created_at: z.string(),
  last_updated: z.string(),
})

// Agent schemas
export const AgentTypeSchema = z.enum([
  'coordinator',
  'business_analyst',
  'frontend_developer',
  'backend_developer',
  'devops_engineer',
  'marketing_specialist'
])

export const MCPActionSchema = z.object({
  server: z.string(),
  action: z.string(),
  params: z.record(z.any()),
})

// Export types
export type ProjectIdea = z.infer<typeof ProjectIdeaSchema>
export type ProjectStatus = z.infer<typeof ProjectStatusSchema>
export type AgentType = z.infer<typeof AgentTypeSchema>
export type MCPAction = z.infer<typeof MCPActionSchema>

// API response schemas
export const SpawnResponseSchema = z.object({
  project_id: z.string().uuid(),
  message: z.string(),
  status: z.string(),
})

export type SpawnResponse = z.infer<typeof SpawnResponseSchema>