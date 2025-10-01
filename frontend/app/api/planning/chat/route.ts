/**
 * Planning Chat API - Jason AI for initial startup ideation
 */

import { NextRequest, NextResponse } from 'next/server'
import { getOpenAIClient, CHAT_CONFIG } from '@/lib/server/openai'
import { verifyAuth } from '@/lib/server/auth'
import { errorResponse } from '@/lib/server/api-response'
import { ChatMessage, ChatRequest } from '@/lib/types/chat'
import { JASON_SYSTEM_PROMPT } from '@/lib/ai/jason-prompt'

export async function POST(req: NextRequest) {
  try {
    // Authenticate user
    const user = await verifyAuth(req)
    console.log('✅ User authenticated:', user.id)

    // Parse and validate request
    const { messages }: ChatRequest = await req.json()

    if (!messages || !Array.isArray(messages)) {
      return errorResponse('Invalid messages format', 400)
    }

    // Get OpenAI client
    const openai = getOpenAIClient()

    // Prepare messages with system prompt
    const openaiMessages = [
      { role: 'system', content: JASON_SYSTEM_PROMPT },
      ...messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }))
    ]

    // Create streaming response
    const stream = await openai.chat.completions.create({
      ...CHAT_CONFIG,
      messages: openaiMessages as any,
    })

    // Stream response to client
    const encoder = new TextEncoder()
    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const content = chunk.choices[0]?.delta?.content
            if (content) {
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`))
            }
          }
          controller.enqueue(encoder.encode(`data: [DONE]\n\n`))
          controller.close()
        } catch (error) {
          console.error('Streaming error:', error)
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: 'Streaming failed' })}\n\n`))
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
    console.error('Planning API error:', error)
    const message = error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(message, error instanceof Error && message === 'Unauthorized' ? 401 : 500)
  }
}

// Health check endpoint
export async function GET() {
  try {
    const openai = getOpenAIClient()
    return NextResponse.json({
      status: 'healthy',
      service: 'jason-ai-planning',
      timestamp: new Date().toISOString(),
    })
  } catch {
    return NextResponse.json({
      status: 'unhealthy',
      service: 'jason-ai-planning',
    }, { status: 503 })
  }
}
