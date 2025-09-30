import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { MODAL_ENDPOINTS } from '@/lib/config/endpoints'

// Initialize Supabase client for server-side auth verification
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: number
}

export async function POST(req: NextRequest) {
  console.log('=== CEO API POST REQUEST STARTED ===')
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
    const { messages, startup_id }: { messages: ChatMessage[], startup_id: string } = await req.json()

    if (!messages || !Array.isArray(messages) || !startup_id) {
      console.error('❌ Invalid request format - messages and startup_id required')
      return NextResponse.json({ error: 'Messages and startup_id are required' }, { status: 400 })
    }

    console.log('🤖 Routing to CEO chat for startup:', startup_id)

    // Get startup from Supabase to verify ownership and CEO status
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

    // Verify CEO is ready
    if (startup.project_status !== 'completed' || startup.ceo_status !== 'ready') {
      console.error('❌ CEO not ready for this startup')
      return NextResponse.json({
        error: 'CEO not ready for this startup. Please complete planning first.',
        ceo_status: startup.ceo_status,
        project_status: startup.project_status
      }, { status: 400 })
    }

    console.log('✅ CEO is ready, routing to Modal endpoint')

    try {
      // Get the last user message
      const lastMessage = messages[messages.length - 1]
      if (!lastMessage || lastMessage.role !== 'user') {
        return NextResponse.json({ error: 'Last message must be from user' }, { status: 400 })
      }

      // Call CEO streaming Modal endpoint
      const ceoResponse = await fetch(MODAL_ENDPOINTS.CEO_CHAT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          startup_id: startup_id,
          message: lastMessage.content
        })
      })

      if (ceoResponse.ok && ceoResponse.body) {
        console.log('✅ CEO streaming response received')

        // Return the streaming response directly
        return new Response(ceoResponse.body, {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
          },
        })
      } else {
        console.error('❌ Failed to reach CEO streaming endpoint:', ceoResponse.status)
        const errorText = await ceoResponse.text()
        console.error('CEO endpoint error:', errorText)

        return NextResponse.json({
          error: 'CEO service unavailable',
          status: ceoResponse.status,
          details: errorText
        }, { status: 503 })
      }
    } catch (error) {
      console.error('❌ Error calling CEO streaming:', error)
      return NextResponse.json({
        error: 'Failed to connect to CEO service',
        details: error instanceof Error ? error.message : String(error)
      }, { status: 503 })
    }

  } catch (error) {
    console.error('❌ CEO API ERROR:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Add GET method for debugging and health checks
export async function GET(req: NextRequest) {
  const url = new URL(req.url)
  const startup_id = url.searchParams.get('startup_id')

  if (!startup_id) {
    return NextResponse.json({
      status: 'CEO API is running',
      service: 'ceo-chat',
      environment: process.env.NODE_ENV,
      endpoints: MODAL_ENDPOINTS,
      timestamp: new Date().toISOString()
    })
  }

  // Health check for specific startup
  try {
    const healthResponse = await fetch(`${MODAL_ENDPOINTS.CEO_HEALTH}?startup_id=${startup_id}`)
    const healthData = await healthResponse.json()

    return NextResponse.json({
      startup_id,
      ceo_status: healthData,
      endpoint_status: healthResponse.status,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    return NextResponse.json({
      startup_id,
      ceo_status: 'unreachable',
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    }, { status: 503 })
  }
}