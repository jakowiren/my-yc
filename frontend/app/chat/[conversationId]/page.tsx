'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeft, Send } from "lucide-react"
import { useState, useEffect, useRef } from "react"
import { useAuth } from "@/lib/auth-context"
import { useChat } from "@/lib/hooks/use-chat"
import { ChatMessageComponent } from "@/components/chat/ChatMessage"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"

interface ChatPageProps {
  params: {
    conversationId: string
  }
}

export default function ChatPage({ params }: ChatPageProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat()
  const [inputValue, setInputValue] = useState("")
  const [conversationTitle, setConversationTitle] = useState("New Conversation")
  const hasInitializedRef = useRef(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  // Get initial message from URL params
  const initialMessage = searchParams.get('message')

  // Send initial message when component mounts
  useEffect(() => {
    if (initialMessage && !hasInitializedRef.current && user) {
      console.log('📤 Sending initial message:', initialMessage)
      hasInitializedRef.current = true
      sendMessage(initialMessage)
    }
  }, [initialMessage, user, sendMessage])

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesContainerRef.current && messagesEndRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: 'smooth'
      })
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    try {
      await sendMessage(inputValue)
      setInputValue('')
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="h-screen bg-black text-white flex flex-col">
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-10 bg-black border-b border-white/10 p-4">
        <div className="container mx-auto max-w-4xl flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-white/70 hover:text-white">
              <ArrowLeft size={20} />
            </Link>
            <h1 className="text-xl font-light">{conversationTitle}</h1>
          </div>
          <span className="text-white/50 text-sm">Conversation {params.conversationId.slice(0, 8)}</span>
        </div>
      </header>

      {/* Scrollable Messages Area */}
      <main ref={messagesContainerRef} className="flex-1 overflow-y-auto messages-scroll pt-20 pb-32">
        <div className="container mx-auto max-w-4xl p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessageComponent key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/10 px-4 py-3 rounded-lg">
                  <div className="text-xs text-white/60 mb-1 font-medium">Jason</div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse delay-100"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </main>

      {/* Fixed Input Area */}
      <footer className="fixed bottom-0 left-0 right-0 z-10 bg-black border-t border-white/10 p-4">
        <div className="container mx-auto max-w-4xl">
          <div className="bg-black border border-white/10 rounded-lg p-3">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Continue the conversation..."
              className="w-full resize-none min-h-[60px] bg-transparent border-0 text-white placeholder:text-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
              disabled={isLoading}
            />
            <div className="flex items-center justify-between mt-2">
              <div className="text-xs text-white/40">
                Chatting with Jason
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="text-white/50 hover:text-white text-xs px-2 py-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </footer>

      {error && (
        <div className="fixed bottom-4 right-4 bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm z-20">
          {error}
        </div>
      )}
    </div>
  )
}