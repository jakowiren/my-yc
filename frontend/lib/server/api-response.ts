/**
 * Standardized API response utilities
 */

import { NextResponse } from 'next/server'

export function errorResponse(message: string, status: number = 500) {
  return NextResponse.json({ error: message }, { status })
}

export function successResponse<T>(data: T, status: number = 200) {
  return NextResponse.json(data, { status })
}

/**
 * Create a streaming response for OpenAI chat
 */
export function createStreamResponse() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      return {
        controller,
        write: (data: any) => {
          const json = JSON.stringify(data)
          controller.enqueue(encoder.encode(`data: ${json}\n\n`))
        },
        close: () => {
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        },
      }
    },
  })

  return new NextResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
