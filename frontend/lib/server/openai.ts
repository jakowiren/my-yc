/**
 * Server-side OpenAI client utilities
 */

import OpenAI from 'openai'

// Singleton OpenAI client
let openaiInstance: OpenAI | null = null

export function getOpenAIClient(): OpenAI {
  if (!openaiInstance) {
    const apiKey = process.env.OPENAI_API_KEY

    if (!apiKey) {
      throw new Error('OPENAI_API_KEY is not configured')
    }

    openaiInstance = new OpenAI({ apiKey })
  }

  return openaiInstance
}

// Standard chat configuration
export const CHAT_CONFIG = {
  model: 'gpt-4o',
  temperature: 0.7,
  max_tokens: 2000,
  stream: true,
} as const
