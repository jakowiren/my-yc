"use client"

import { useState, useCallback, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { supabase } from '@/lib/supabase'
import { Startup, Message, MessageInsert } from '@/lib/types/supabase'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface UseStartupReturn {
  startup: Startup | null
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendMessage: (content: string) => Promise<void>
  loadStartup: (startupId: string) => Promise<void>
  clearMessages: () => void
}

export function useStartup(): UseStartupReturn {
  const { session } = useAuth()
  const [startup, setStartup] = useState<Startup | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadStartup = useCallback(async (startupId: string) => {
    if (!session?.access_token) {
      setError('Not authenticated')
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      // Load startup details
      const { data: startupData, error: startupError } = await supabase
        .from('startups')
        .select('*')
        .eq('id', startupId)
        .single()

      if (startupError) {
        throw new Error(startupError.message)
      }

      setStartup(startupData)

      // Load messages for this startup
      const { data: messagesData, error: messagesError } = await supabase
        .from('messages')
        .select('*')
        .eq('startup_id', startupId)
        .order('created_at', { ascending: true })

      if (messagesError) {
        throw new Error(messagesError.message)
      }

      // Convert Supabase messages to ChatMessage format
      const chatMessages: ChatMessage[] = messagesData
        .filter(msg => msg.role !== 'system')
        .map(msg => ({
          id: msg.id,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: new Date(msg.created_at).getTime(),
        }))

      setMessages(chatMessages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load startup')
      console.error('Error loading startup:', err)
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const sendMessage = useCallback(async (content: string) => {
    if (!session?.access_token) {
      throw new Error('Not authenticated')
    }

    if (!startup) {
      throw new Error('No startup loaded')
    }

    if (!content.trim()) return

    // Add user message immediately (optimistic update)
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: Date.now(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      // Save user message to database
      const userMessageData: MessageInsert = {
        startup_id: startup.id,
        role: 'user',
        content: content.trim(),
      }

      const { error: userMessageError } = await supabase
        .from('messages')
        .insert(userMessageData)

      if (userMessageError) {
        throw new Error(`Failed to save user message: ${userMessageError.message}`)
      }

      // Prepare messages for API (include history for context)
      const apiMessages = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
      }))

      // Call chat API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          messages: apiMessages,
          startup_id: startup.id
        }),
      })

      if (!response.ok) {
        let errorMessage = 'Failed to send message'
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorMessage
        } catch (e) {
          errorMessage = response.statusText || errorMessage
        }
        throw new Error(errorMessage)
      }

      // Handle streaming response
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      let assistantContent = ''
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      }

      // Add empty assistant message that we'll update
      setMessages(prev => [...prev, assistantMessage])

      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()

            if (data === '[DONE]') {
              // Save final assistant message to database
              if (assistantContent) {
                const assistantMessageData: MessageInsert = {
                  startup_id: startup.id,
                  role: 'assistant',
                  content: assistantContent,
                }

                await supabase
                  .from('messages')
                  .insert(assistantMessageData)
              }
              setIsLoading(false)
              return
            }

            if (data === '') continue

            try {
              const parsed = JSON.parse(data)
              if (parsed.error) {
                throw new Error(parsed.error)
              }
              if (parsed.content) {
                assistantContent += parsed.content

                // Update the assistant message with accumulated content
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessage.id
                      ? { ...msg, content: assistantContent }
                      : msg
                  )
                )

                // Check if this is the first message and extract title
                if (messages.length === 1 && assistantContent.includes('TITLE:')) {
                  const titleMatch = assistantContent.match(/TITLE:\s*(.+)/i)
                  if (titleMatch) {
                    const suggestedTitle = titleMatch[1].trim()

                    // Update startup title in database
                    supabase
                      .from('startups')
                      .update({ title: suggestedTitle })
                      .eq('id', startup.id)
                      .then(({ error }) => {
                        if (!error) {
                          setStartup(prev => prev ? { ...prev, title: suggestedTitle } : null)
                        }
                      })
                  }
                }
              }
            } catch (e) {
              if (e instanceof Error && e.message !== 'Unexpected end of JSON input') {
                throw e
              }
              console.debug('Skipping unparseable chunk:', data)
            }
          }
        }
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [session, startup, messages])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    startup,
    messages,
    isLoading,
    error,
    sendMessage,
    loadStartup,
    clearMessages,
  }
}