"use client"

import { useState, useCallback, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { supabase } from '@/lib/supabase'
import { Startup, Message, MessageInsert } from '@/lib/types/supabase'
import { StartupDesignDoc } from '@/lib/ai/design-doc-template'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  metadata?: Record<string, any>
}

interface UseStartupReturn {
  startup: Startup | null
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendMessage: (content: string, agentType?: string) => Promise<void>
  loadStartup: (startupId: string, reloadMessages?: boolean) => Promise<Startup | null>
  clearMessages: () => void
}

export function useStartup(): UseStartupReturn {
  const { session } = useAuth()
  const [startup, setStartup] = useState<Startup | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadStartup = useCallback(async (startupId: string, reloadMessages: boolean = true): Promise<Startup | null> => {
    if (!session?.access_token) {
      setError('Not authenticated')
      return null
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

      // Only reload messages if explicitly requested
      if (reloadMessages) {
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
            metadata: msg.metadata || {}
          }))

        setMessages(chatMessages)
      }

      return startupData
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load startup')
      console.error('Error loading startup:', err)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const sendMessage = useCallback(async (content: string, agentType?: string) => {
    if (!session?.access_token) {
      throw new Error('Not authenticated')
    }

    if (!startup) {
      throw new Error('No startup loaded')
    }

    if (!content.trim()) return

    // Determine current agent based on project status and passed agentType
    let currentAgent: string
    if (startup.project_status === 'workspace_ready' && startup.ceo_status === 'ready') {
      // Use provided agent type or default to 'ceo' for workspace
      currentAgent = agentType || 'ceo'
    } else {
      // Use Jason for planning phase
      currentAgent = 'jason'
    }

    // Add user message immediately (optimistic update) with metadata
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: Date.now(),
      metadata: { agent: currentAgent }
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
        metadata: { agent: currentAgent }
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
          startup_id: startup.id,
          agent_type: currentAgent
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
        metadata: { agent: currentAgent }
      }

      // Add empty assistant message that we'll update
      setMessages(prev => [...prev, assistantMessage])

      const decoder = new TextDecoder()
      let buffer = '' // Buffer for accumulating words
      let displayedContent = '' // Content currently displayed
      let updateScheduled = false

      // Function to update UI with buffered content
      const updateUI = () => {
        if (buffer.length > 0) {
          displayedContent += buffer
          buffer = ''

          // Filter out DESIGN_DOC_FINAL lines from display
          let displayContent = displayedContent
          const designDocIndex = displayContent.indexOf('DESIGN_DOC_FINAL:')
          if (designDocIndex !== -1) {
            let braceCount = 0
            let jsonStart = displayContent.indexOf('{', designDocIndex)
            if (jsonStart !== -1) {
              let jsonEnd = jsonStart
              for (let i = jsonStart; i < displayContent.length; i++) {
                if (displayContent[i] === '{') braceCount++
                if (displayContent[i] === '}') braceCount--
                if (braceCount === 0) {
                  jsonEnd = i
                  break
                }
              }
              displayContent = displayContent.substring(0, designDocIndex) + displayContent.substring(jsonEnd + 1)
              displayContent = displayContent.trim()
            }
          }

          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: displayContent }
                : msg
            )
          )
        }
        updateScheduled = false
      }

      // Schedule update on next animation frame for smooth rendering
      const scheduleUpdate = () => {
        if (!updateScheduled) {
          updateScheduled = true
          requestAnimationFrame(updateUI)
        }
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()

            if (data === '[DONE]') {
              // Flush any remaining buffered content
              if (buffer.length > 0) {
                updateUI()
              }

              // Save final assistant message to database
              if (assistantContent) {
                const assistantMessageData: MessageInsert = {
                  startup_id: startup.id,
                  role: 'assistant',
                  content: assistantContent,
                  metadata: { agent: currentAgent }
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
                buffer += parsed.content

                // Update on word boundaries or punctuation for natural flow
                // This includes spaces, newlines, and punctuation
                if (parsed.content.match(/[\s\n,.!?;:]/)) {
                  scheduleUpdate()
                }

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

                // Check for finalized design document
                if (assistantContent.includes('DESIGN_DOC_FINAL:')) {
                  try {
                    const docMatch = assistantContent.match(/DESIGN_DOC_FINAL:\s*(\{[\s\S]*?\})/i)
                    if (docMatch) {
                      const designDocJson = docMatch[1]
                      const designDoc: StartupDesignDoc = JSON.parse(designDocJson)

                      console.log('📋 Design document finalized:', designDoc)

                      // Update startup with design document and mark as ready
                      supabase
                        .from('startups')
                        .update({
                          design_doc: designDoc,
                          project_status: 'design_ready',
                          title: designDoc.title
                        })
                        .eq('id', startup.id)
                        .then(({ error }) => {
                          if (!error) {
                            setStartup(prev => prev ? {
                              ...prev,
                              design_doc: designDoc,
                              project_status: 'design_ready',
                              title: designDoc.title
                            } : null)
                          } else {
                            console.error('Failed to save design doc:', error)
                          }
                        })
                    }
                  } catch (e) {
                    console.error('Failed to parse design document:', e)
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

      // Final update to ensure all content is displayed
      if (assistantContent) {
        let displayContent = assistantContent
        const designDocIndex = displayContent.indexOf('DESIGN_DOC_FINAL:')
        if (designDocIndex !== -1) {
          let braceCount = 0
          let jsonStart = displayContent.indexOf('{', designDocIndex)
          if (jsonStart !== -1) {
            let jsonEnd = jsonStart
            for (let i = jsonStart; i < displayContent.length; i++) {
              if (displayContent[i] === '{') braceCount++
              if (displayContent[i] === '}') braceCount--
              if (braceCount === 0) {
                jsonEnd = i
                break
              }
            }
            displayContent = displayContent.substring(0, designDocIndex) + displayContent.substring(jsonEnd + 1)
            displayContent = displayContent.trim()
          }
        }

        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMessage.id
              ? { ...msg, content: displayContent }
              : msg
          )
        )
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