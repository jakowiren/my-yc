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
  try {
    // Check if OpenAI is properly initialized
    if (!openai) {
      console.error('OpenAI client not initialized - check OPENAI_API_KEY')
      return NextResponse.json({ error: 'AI service unavailable' }, { status: 503 })
    }

    // Get the authorization header
    const authHeader = req.headers.get('authorization')
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Missing or invalid authorization header' }, { status: 401 })
    }

    const token = authHeader.split(' ')[1]

    // Verify the user is authenticated
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Parse the request body
    const { messages }: { messages: ChatMessage[] } = await req.json()

    if (!messages || !Array.isArray(messages)) {
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

    // TODO: Add rate limiting (10 messages per day for free users)
    // TODO: Track message count in Supabase user_daily_limits table

    // Create streaming response
    const stream = await openai.chat.completions.create({
      ...CHAT_CONFIG,
      messages: openaiMessages as any,
    })

    // Create a readable stream for the response
    const encoder = new TextEncoder()
    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const content = chunk.choices[0]?.delta?.content
            if (content) {
              const data = `data: ${JSON.stringify({ content })}\n\n`
              controller.enqueue(encoder.encode(data))
            }
          }
          // Send done signal
          controller.enqueue(encoder.encode(`data: [DONE]\n\n`))
          controller.close()
        } catch (error) {
          console.error('Streaming error:', error)
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

  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Add GET method for debugging
export async function GET() {
  return NextResponse.json({
    status: 'Chat API is running',
    openaiConfigured: !!openai,
    timestamp: new Date().toISOString()
  })
}