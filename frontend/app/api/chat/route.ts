import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { JASON_SYSTEM_PROMPT } from '@/lib/ai/jason-prompt'
import OpenAI from 'openai'

// Initialize Supabase client for server-side auth verification
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

// Initialize OpenAI client inline to avoid import errors
let openai: OpenAI | null = null
try {
  if (process.env.OPENAI_API_KEY) {
    openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    })
  }
} catch (error) {
  console.error('Failed to initialize OpenAI client:', error)
}

const CHAT_CONFIG = {
  model: 'gpt-4o',
  temperature: 0.7,
  max_tokens: 2000,
  stream: true,
} as const

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: number
}

export async function POST(req: NextRequest) {
  console.log('=== CHAT API POST REQUEST STARTED ===')
  console.log('Timestamp:', new Date().toISOString())
  console.log('Environment check:')
  console.log('- OPENAI_API_KEY exists:', !!process.env.OPENAI_API_KEY)
  console.log('- OPENAI_API_KEY length:', process.env.OPENAI_API_KEY?.length || 0)
  console.log('- OPENAI_API_KEY starts with sk-:', process.env.OPENAI_API_KEY?.startsWith('sk-') || false)
  console.log('- SUPABASE_SERVICE_ROLE_KEY exists:', !!process.env.SUPABASE_SERVICE_ROLE_KEY)
  console.log('- NEXT_PUBLIC_SUPABASE_URL exists:', !!process.env.NEXT_PUBLIC_SUPABASE_URL)
  console.log('- OpenAI client initialized:', !!openai)

  try {
    // Check if OpenAI is properly initialized
    if (!openai) {
      console.error('❌ OpenAI client not initialized - check OPENAI_API_KEY')
      console.error('Available env vars:', Object.keys(process.env).filter(key => key.includes('OPENAI')))
      return NextResponse.json({ error: 'AI service unavailable' }, { status: 503 })
    }

    console.log('✅ OpenAI client is initialized')

    // Get the authorization header
    console.log('🔐 Checking authorization...')
    const authHeader = req.headers.get('authorization')
    console.log('- Auth header exists:', !!authHeader)
    console.log('- Auth header starts with Bearer:', authHeader?.startsWith('Bearer ') || false)

    if (!authHeader?.startsWith('Bearer ')) {
      console.error('❌ Missing or invalid authorization header')
      return NextResponse.json({ error: 'Missing or invalid authorization header' }, { status: 401 })
    }

    const token = authHeader.split(' ')[1]
    console.log('- Token length:', token?.length || 0)

    // Verify the user is authenticated
    console.log('🔍 Verifying user with Supabase...')
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)

    if (authError) {
      console.error('❌ Supabase auth error:', authError)
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    if (!user) {
      console.error('❌ No user found')
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    console.log('✅ User authenticated:', user.id)

    // Parse the request body
    console.log('📝 Parsing request body...')
    const { messages, startup_id }: { messages: ChatMessage[], startup_id?: string } = await req.json()
    console.log('- Messages received:', messages?.length || 0)
    console.log('- Startup ID:', startup_id)
    console.log('- Messages preview:', messages?.slice(-2).map(m => ({ role: m.role, length: m.content?.length })))

    if (!messages || !Array.isArray(messages)) {
      console.error('❌ Invalid messages format')
      return NextResponse.json({ error: 'Invalid messages format' }, { status: 400 })
    }

    // Ensure we have the system prompt at the beginning
    const systemMessage: ChatMessage = {
      role: 'system',
      content: JASON_SYSTEM_PROMPT,
    }

    // Prepare messages for OpenAI (exclude timestamps and ensure proper format)
    const openaiMessages = [
      systemMessage,
      ...messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }))
    ]

    console.log('📤 Prepared', openaiMessages.length, 'messages for OpenAI')
    console.log('- System prompt length:', JASON_SYSTEM_PROMPT.length)

    // TODO: Add rate limiting (10 messages per day for free users)
    // TODO: Track message count in Supabase user_daily_limits table

    // Create streaming response
    console.log('🤖 Calling OpenAI with config:', CHAT_CONFIG)
    const stream = await openai.chat.completions.create({
      ...CHAT_CONFIG,
      messages: openaiMessages as any,
    })
    console.log('✅ OpenAI stream created successfully')

    // Create a readable stream for the response
    console.log('📡 Creating streaming response...')
    const encoder = new TextEncoder()
    let chunkCount = 0
    let totalContent = ''

    const readable = new ReadableStream({
      async start(controller) {
        try {
          console.log('🔄 Starting stream processing...')
          for await (const chunk of stream) {
            chunkCount++
            const content = chunk.choices[0]?.delta?.content
            if (content) {
              totalContent += content
              const data = `data: ${JSON.stringify({ content })}\n\n`
              controller.enqueue(encoder.encode(data))

              if (chunkCount <= 3) {
                console.log(`📦 Chunk ${chunkCount}:`, content.substring(0, 50) + '...')
              }
            }
          }
          console.log('✅ Stream completed successfully')
          console.log('- Total chunks processed:', chunkCount)
          console.log('- Total content length:', totalContent.length)
          console.log('- Content preview:', totalContent.substring(0, 100) + '...')

          // Send done signal
          controller.enqueue(encoder.encode(`data: [DONE]\n\n`))
          controller.close()
        } catch (error) {
          console.error('❌ Streaming error:', error)
          console.error('Error details:', {
            name: error instanceof Error ? error.name : 'Unknown',
            message: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : 'No stack trace'
          })
          // Send error message before closing
          const errorData = `data: ${JSON.stringify({ error: 'Streaming failed' })}\n\n`
          controller.enqueue(encoder.encode(errorData))
          controller.close()
        }
      },
    })

    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })

    console.log('🎉 API request completed successfully')

  } catch (error) {
    console.error('❌ CHAT API ERROR:', error)
    console.error('Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : 'No stack trace'
    })
    console.log('=== CHAT API REQUEST FAILED ===')

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Add GET method for debugging
export async function GET() {
  console.log('=== CHAT API GET REQUEST ===')
  console.log('Environment debug info:')
  console.log('- NODE_ENV:', process.env.NODE_ENV)
  console.log('- VERCEL:', process.env.VERCEL)
  console.log('- OPENAI_API_KEY exists:', !!process.env.OPENAI_API_KEY)
  console.log('- OPENAI_API_KEY length:', process.env.OPENAI_API_KEY?.length || 0)
  console.log('- All env vars containing OPENAI:', Object.keys(process.env).filter(key => key.includes('OPENAI')))

  return NextResponse.json({
    status: 'Chat API is running',
    environment: process.env.NODE_ENV,
    isVercel: !!process.env.VERCEL,
    openaiConfigured: !!openai,
    openaiKeyExists: !!process.env.OPENAI_API_KEY,
    openaiKeyLength: process.env.OPENAI_API_KEY?.length || 0,
    supabaseConfigured: !!process.env.SUPABASE_SERVICE_ROLE_KEY,
    timestamp: new Date().toISOString()
  })
}