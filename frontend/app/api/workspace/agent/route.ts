import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client for server-side auth verification
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

// Workspace endpoints with fallbacks (Modal uses label only, not app name in URL)
const WORKSPACE_ENDPOINTS = {
  AGENT_INVOKE: process.env.NEXT_PUBLIC_WORKSPACE_AGENT_ENDPOINT ||
                'https://jakowiren--workspace-agent-invoke.modal.run',
  AGENT_STREAM: process.env.NEXT_PUBLIC_WORKSPACE_AGENT_STREAM_ENDPOINT ||
                'https://jakowiren--workspace-agent-stream.modal.run',
  WORKSPACE_STATUS: process.env.NEXT_PUBLIC_WORKSPACE_STATUS_ENDPOINT ||
                   'https://jakowiren--workspace-status-check.modal.run',
  TEAM_BOARD: process.env.NEXT_PUBLIC_WORKSPACE_TEAM_BOARD_ENDPOINT ||
             'https://jakowiren--workspace-team-board.modal.run'
}

console.log('🔧 Workspace endpoints configured:', WORKSPACE_ENDPOINTS)

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: number
}

export async function POST(req: NextRequest) {
  console.log('=== WORKSPACE AGENT API POST REQUEST STARTED ===')
  console.log('Timestamp:', new Date().toISOString())

  try {
    // Get the authorization header
    console.log('🔐 Checking authorization...')
    const authHeader = req.headers.get('authorization')

    if (!authHeader?.startsWith('Bearer ')) {
      console.error('❌ Missing or invalid authorization header')
      return NextResponse.json({ error: 'Missing or invalid authorization header' }, { status: 401 })
    }

    const token = authHeader.split(' ')[1]

    // Verify the user is authenticated
    console.log('🔍 Verifying user with Supabase...')
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)

    if (authError || !user) {
      console.error('❌ Supabase auth error:', authError)
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    console.log('✅ User authenticated:', user.id)

    // Parse the request body
    console.log('📝 Parsing request body...')
    const {
      messages,
      startup_id,
      agent_type = 'ceo',
      stream = true,
      context = {}
    }: {
      messages: ChatMessage[],
      startup_id: string,
      agent_type?: string,
      stream?: boolean,
      context?: any
    } = await req.json()

    if (!messages || !Array.isArray(messages) || !startup_id) {
      console.error('❌ Invalid request format - messages and startup_id required')
      return NextResponse.json({ error: 'Messages and startup_id are required' }, { status: 400 })
    }

    console.log(`🤖 Routing to ${agent_type} agent for startup:`, startup_id)
    console.log(`📊 Stream mode: ${stream}`)

    // Get startup from Supabase to verify ownership
    const { data: startup, error: startupError } = await supabase
      .from('startups')
      .select('project_status, ceo_status, container_endpoint')
      .eq('id', startup_id)
      .eq('user_id', user.id)
      .single()

    if (startupError || !startup) {
      console.error('❌ Startup not found or access denied:', startupError)
      return NextResponse.json({ error: 'Startup not found or access denied' }, { status: 404 })
    }

    console.log('✅ Startup access verified')

    try {
      // Get the last user message
      const lastMessage = messages[messages.length - 1]
      if (!lastMessage || lastMessage.role !== 'user') {
        return NextResponse.json({ error: 'Last message must be from user' }, { status: 400 })
      }

      // Choose endpoint based on stream preference
      const endpoint = stream ? WORKSPACE_ENDPOINTS.AGENT_STREAM : WORKSPACE_ENDPOINTS.AGENT_INVOKE

      console.log(`📡 Calling workspace endpoint: ${endpoint}`)
      console.log(`📋 Payload:`, {
        startup_id: startup_id,
        agent_type: agent_type,
        message: lastMessage.content
      })

      // Call workspace agent endpoint
      const workspaceResponse = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          startup_id: startup_id,
          agent_type: agent_type,
          message: lastMessage.content,
          context: context
        })
      }).catch(err => {
        console.error('❌ Network error calling workspace endpoint:', err)
        throw err
      })

      console.log(`📊 Workspace response status: ${workspaceResponse.status}`)
      console.log(`📊 Workspace response headers:`, Object.fromEntries(workspaceResponse.headers.entries()))

      if (workspaceResponse.ok) {
        if (stream && workspaceResponse.body) {
          console.log('✅ Workspace streaming response received')

          // Check if it's actually an error response with 200 status
          const contentType = workspaceResponse.headers.get('content-type')
          if (contentType?.includes('application/json')) {
            // It's JSON, might be an error response
            const jsonResponse = await workspaceResponse.json()
            if (jsonResponse.success === false || jsonResponse.error) {
              console.error('❌ Workspace returned error in 200 response:', jsonResponse)
              return NextResponse.json({
                error: jsonResponse.error || 'Workspace error',
                details: JSON.stringify(jsonResponse),
                agent_type: agent_type
              }, { status: 503 })
            }
          }

          // Return the streaming response directly
          return new Response(workspaceResponse.body, {
            headers: {
              'Content-Type': 'text/event-stream',
              'Cache-Control': 'no-cache',
              'Connection': 'keep-alive',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Headers': '*'
            },
          })
        } else {
          // Non-streaming response
          const responseData = await workspaceResponse.json()
          console.log('✅ Workspace response received:', responseData)

          // Check for error in response
          if (responseData.success === false || responseData.error) {
            console.error('❌ Workspace returned error:', responseData)
            return NextResponse.json({
              error: responseData.error || 'Workspace error',
              details: JSON.stringify(responseData),
              agent_type: agent_type
            }, { status: 503 })
          }

          return NextResponse.json({
            success: true,
            agent_type: agent_type,
            startup_id: startup_id,
            response: responseData.response || responseData.content || '',
            tools_used: responseData.tools_used || [],
            container_status: responseData.container_status || 'active',
            timestamp: responseData.timestamp || new Date().toISOString()
          })
        }
      } else {
        console.error('❌ Failed to reach workspace endpoint:', workspaceResponse.status)
        const errorText = await workspaceResponse.text()
        console.error('Workspace endpoint error response:', errorText)
        console.error('Full error details:', {
          status: workspaceResponse.status,
          statusText: workspaceResponse.statusText,
          url: endpoint,
          errorBody: errorText
        })

        return NextResponse.json({
          error: 'Workspace service unavailable',
          status: workspaceResponse.status,
          details: errorText,
          agent_type: agent_type,
          endpoint: endpoint // Include endpoint for debugging
        }, { status: 503 })
      }
    } catch (error) {
      console.error('❌ Error calling workspace agent:', error)
      return NextResponse.json({
        error: 'Failed to connect to workspace service',
        details: error instanceof Error ? error.message : String(error),
        agent_type: agent_type
      }, { status: 503 })
    }

  } catch (error) {
    console.error('❌ WORKSPACE AGENT API ERROR:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// GET method for debugging, status checks, and team board access
export async function GET(req: NextRequest) {
  const url = new URL(req.url)
  const startup_id = url.searchParams.get('startup_id')
  const action = url.searchParams.get('action') // 'status', 'team-board', 'agents'

  console.log(`=== WORKSPACE AGENT API GET REQUEST: ${action || 'default'} ===`)

  // Basic API info if no parameters
  if (!startup_id) {
    return NextResponse.json({
      status: 'Workspace Agent API is running',
      service: 'workspace-agents',
      environment: process.env.NODE_ENV,
      endpoints: WORKSPACE_ENDPOINTS,
      available_actions: ['status', 'team-board', 'agents'],
      timestamp: new Date().toISOString()
    })
  }

  try {
    // Get the authorization header for authenticated requests
    const authHeader = req.headers.get('authorization')
    if (authHeader?.startsWith('Bearer ')) {
      const token = authHeader.split(' ')[1]

      // Verify the user is authenticated
      const { data: { user }, error: authError } = await supabase.auth.getUser(token)

      if (!authError && user) {
        // Verify startup ownership
        const { data: startup, error: startupError } = await supabase
          .from('startups')
          .select('id')
          .eq('id', startup_id)
          .eq('user_id', user.id)
          .single()

        if (startupError || !startup) {
          return NextResponse.json({ error: 'Startup not found or access denied' }, { status: 404 })
        }
      }
    }

    // Handle different actions
    switch (action) {
      case 'status':
        // Get workspace status
        try {
          const statusResponse = await fetch(`${WORKSPACE_ENDPOINTS.WORKSPACE_STATUS}?startup_id=${startup_id}`)
          const statusData = await statusResponse.json()

          return NextResponse.json({
            startup_id,
            workspace_status: statusData,
            endpoint_status: statusResponse.status,
            timestamp: new Date().toISOString()
          })
        } catch (error) {
          return NextResponse.json({
            startup_id,
            workspace_status: 'unreachable',
            error: error instanceof Error ? error.message : String(error),
            timestamp: new Date().toISOString()
          }, { status: 503 })
        }

      case 'team-board':
        // Get team message board
        try {
          const teamResponse = await fetch(`${WORKSPACE_ENDPOINTS.TEAM_BOARD}?startup_id=${startup_id}`)
          const teamData = await teamResponse.json()

          return NextResponse.json({
            startup_id,
            team_board: teamData,
            timestamp: new Date().toISOString()
          })
        } catch (error) {
          return NextResponse.json({
            startup_id,
            team_board: { messages: [], error: 'unreachable' },
            error: error instanceof Error ? error.message : String(error),
            timestamp: new Date().toISOString()
          }, { status: 503 })
        }

      case 'agents':
        // Get available agents (static list for now)
        return NextResponse.json({
          startup_id,
          available_agents: ['ceo', 'frontend', 'backend', 'design', 'testing', 'devops'],
          timestamp: new Date().toISOString()
        })

      default:
        // Default status check
        try {
          const statusResponse = await fetch(`${WORKSPACE_ENDPOINTS.WORKSPACE_STATUS}?startup_id=${startup_id}`)
          const statusData = await statusResponse.json()

          return NextResponse.json({
            startup_id,
            status: statusData,
            timestamp: new Date().toISOString()
          })
        } catch (error) {
          return NextResponse.json({
            startup_id,
            status: 'unreachable',
            error: error instanceof Error ? error.message : String(error),
            timestamp: new Date().toISOString()
          }, { status: 503 })
        }
    }
  } catch (error) {
    console.error('❌ WORKSPACE AGENT GET ERROR:', error)
    return NextResponse.json({
      startup_id,
      error: 'Internal server error',
      details: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}