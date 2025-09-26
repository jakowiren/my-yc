import OpenAI from 'openai'

if (!process.env.OPENAI_API_KEY) {
  throw new Error('OPENAI_API_KEY environment variable is required')
}

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export const JASON_MODEL = 'gpt-4o'

export const CHAT_CONFIG = {
  model: JASON_MODEL,
  temperature: 0.7,
  max_tokens: 2000,
  stream: true,
} as const