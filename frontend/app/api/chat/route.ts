/**
 * Smart Chat Router - Routes requests to appropriate agent based on project status
 *
 * Routes to:
 * - Jason AI (planning/chat) for design phase
 * - Workspace Agent for active projects
 */

import { NextRequest } from 'next/server'
import { verifyAuth } from '@/lib/server/auth'
import { getSupabaseServerClient } from '@/lib/server/supabase'
import { errorResponse } from '@/lib/server/api-response'
import { ChatRequest } from '@/lib/types/chat'

export async function POST(req: NextRequest) {
  try {
    // Authenticate user
    const user = await verifyAuth(req)

    // Parse request body
    const body: ChatRequest = await req.json()
    const { messages, startup_id } = body

    if (!messages || !Array.isArray(messages)) {
      return errorResponse('Invalid messages format', 400)
    }

    // If no startup_id, route to planning (Jason)
    if (!startup_id) {
      console.log('→ Routing to Jason (planning phase)')
      return routeToPlanning(req, body)
    }

    // Get startup status to determine routing
    const supabase = getSupabaseServerClient()
    const { data: startup, error } = await supabase
      .from('startups')
      .select('project_status, ceo_status')
      .eq('id', startup_id)
      .eq('user_id', user.id)
      .single()

    if (error || !startup) {
      return errorResponse('Startup not found', 404)
    }

    // Route based on project status
    const isWorkspaceReady = (startup as any).project_status === 'workspace_ready' &&
                             (startup as any).ceo_status === 'ready'

    if (isWorkspaceReady) {
      console.log('→ Routing to Workspace Agent')
      return routeToWorkspace(req, body)
    } else {
      console.log('→ Routing to Jason (planning phase)')
      return routeToPlanning(req, body)
    }
  } catch (error) {
    console.error('Chat router error:', error)
    const message = error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(message, error instanceof Error && message === 'Unauthorized' ? 401 : 500)
  }
}

/**
 * Route to planning/chat (Jason AI)
 * Creates a new request with the body to avoid "body already read" error
 */
async function routeToPlanning(originalReq: NextRequest, body: ChatRequest) {
  const { POST: planningPost } = await import('../planning/chat/route')

  // Create a new request with the parsed body
  const newReq = new NextRequest(originalReq.url, {
    method: 'POST',
    headers: originalReq.headers,
    body: JSON.stringify(body),
  })

  return planningPost(newReq)
}

/**
 * Route to workspace/agent (CEO and team agents)
 * Creates a new request with the body to avoid "body already read" error
 */
async function routeToWorkspace(originalReq: NextRequest, body: ChatRequest) {
  const { POST: workspacePost } = await import('../workspace/agent/route')

  // Create a new request with the parsed body
  const newReq = new NextRequest(originalReq.url, {
    method: 'POST',
    headers: originalReq.headers,
    body: JSON.stringify(body),
  })

  return workspacePost(newReq)
}
