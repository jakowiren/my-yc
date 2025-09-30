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
  console.log('=== PLANNING API POST REQUEST STARTED ===')
  console.log('Timestamp:', new Date().toISOString())

  try {
    // Check if OpenAI is properly initialized
    if (!openai) {
      console.error('❌ OpenAI client not initialized - check OPENAI_API_KEY')
      return NextResponse.json({ error: 'AI service unavailable' }, { status: 503 })
    }

    console.log('✅ OpenAI client is initialized')

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
    const { messages }: { messages: ChatMessage[] } = await req.json()

    if (!messages || !Array.isArray(messages)) {
      console.error('❌ Invalid messages format')
      return NextResponse.json({ error: 'Invalid messages format' }, { status: 400 })
    }

    console.log('🎭 Using Jason AI for planning')

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
          console.log('✅ Planning stream completed successfully')
          console.log('- Total chunks processed:', chunkCount)
          console.log('- Total content length:', totalContent.length)

          // Send done signal
          controller.enqueue(encoder.encode(`data: [DONE]\n\n`))
          controller.close()
        } catch (error) {
          console.error('❌ Planning streaming error:', error)
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

  } catch (error) {
    console.error('❌ PLANNING API ERROR:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Add GET method for debugging
export async function GET() {
  return NextResponse.json({
    status: 'Planning API is running',
    service: 'jason-ai',
    environment: process.env.NODE_ENV,
    openaiConfigured: !!openai,
    timestamp: new Date().toISOString()
  })
}