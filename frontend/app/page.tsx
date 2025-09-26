'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sparkles, Send, LogOut } from "lucide-react"
import { useState, useEffect, useRef } from "react"
import { useAuth } from "@/lib/auth-context"
import { useChat } from "@/lib/hooks/use-chat"
import { ChatMessageComponent } from "@/components/chat/ChatMessage"
import { LoginModal } from "@/components/chat/LoginModal"
import Link from "next/link"
import Image from "next/image"

const examplePrompts = [
  "Build a SaaS for small businesses",
  "Create a fitness app with AI coaching",
  "Design a fintech solution for Gen Z",
  "Build an e-commerce platform for creators",
  "Create a productivity tool for remote teams"
]

export default function Home() {
  const { user, loading, signOut } = useAuth()
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat()
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [promptIndex, setPromptIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)
  const [inputValue, setInputValue] = useState("")
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [chatExpanded, setChatExpanded] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)


  useEffect(() => {
    let timeout: NodeJS.Timeout

    if (isTyping) {
      const prompt = examplePrompts[promptIndex]
      if (currentPrompt.length < prompt.length) {
        timeout = setTimeout(() => {
          setCurrentPrompt(prompt.slice(0, currentPrompt.length + 1))
        }, 100)
      } else {
        timeout = setTimeout(() => {
          setIsTyping(false)
        }, 2000)
      }
    } else {
      if (currentPrompt.length > 0) {
        timeout = setTimeout(() => {
          setCurrentPrompt(currentPrompt.slice(0, -1))
        }, 50)
      } else {
        setPromptIndex((prev) => (prev + 1) % examplePrompts.length)
        setIsTyping(true)
      }
    }

    return () => clearTimeout(timeout)
  }, [currentPrompt, promptIndex, isTyping])

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    if (!user) {
      setShowLoginModal(true)
      return
    }

    try {
      await sendMessage(inputValue)
      setInputValue('')
      setChatExpanded(true)
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
    <div className="min-h-screen bg-black relative overflow-hidden">

      {/* Header */}
      <header className="relative z-10 border-b border-white/5">
        <div className="container mx-auto px-6 py-3">
          <nav className="flex items-center justify-between">
            <span className="text-lg font-light text-white">my-yc</span>
            <div className="flex items-center space-x-3">
              {loading ? (
                <div className="w-4 h-4 animate-spin rounded-full border border-white/30 border-t-white"></div>
              ) : user ? (
                <div className="flex items-center space-x-2">
                  <span className="text-white/70 text-sm">{user.user_metadata?.full_name || user.email}</span>
                  <button onClick={signOut} className="text-white/50 hover:text-white text-sm">×</button>
                </div>
              ) : (
                <Link href="/signin" className="text-white/70 hover:text-white text-sm">Sign In</Link>
              )}
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-6 py-12">
        <div className="max-w-2xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-12">
            <h1 className="text-3xl font-light tracking-wide text-white">
              Become your own investor
            </h1>
          </div>

          {/* Chat Interface */}
          <div className="w-full max-w-4xl mx-auto">
            <div className={`bg-black border border-white/10 rounded-lg transition-all duration-300 ${
              chatExpanded ? 'p-4' : 'p-3'
            }`}>
              {/* Chat Messages - Only show when expanded */}
              {chatExpanded && messages.length > 0 && (
                <div className="mb-4 max-h-96 overflow-y-auto">
                  {messages.map((message) => (
                    <ChatMessageComponent key={message.id} message={message} />
                  ))}
                  {isLoading && (
                    <div className="flex justify-start mb-4">
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
              )}

              {/* Input Interface */}
              <div className={chatExpanded ? "border-t border-white/10 pt-4" : ""}>
                <Textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={inputValue ? '' : currentPrompt}
                  className="w-full resize-none min-h-[60px] bg-transparent border-0 text-white placeholder:text-white/40 focus:ring-0 text-sm"
                  disabled={isLoading}
                />
                <div className="flex items-center justify-between mt-2">
                  <div className="text-xs text-white/40">
                    {!user ? 'Sign in to chat with Jason' : (chatExpanded ? 'Chatting with Jason' : 'Press Enter to start')}
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
            {error && (
              <div className="mt-2 text-xs text-red-400 text-center">
                {error}
              </div>
            )}
          </div>

          {/* Separator Line */}
          <div className="w-full h-px bg-white/10 my-12"></div>

          {/* Your Startups Section */}
          <div className="w-full max-w-4xl mx-auto">
            <h2 className="text-xl font-light text-white mb-6">Your Startups</h2>

            {!user ? (
              <div className="text-center py-8">
                <p className="text-white/60 text-sm">Log in to see your startups</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Project containers will be populated here */}
                <div className="text-center py-12 col-span-full">
                  <p className="text-white/40 text-sm">Your startups will appear here</p>
                </div>
              </div>
            )}
          </div>

        </div>
      </main>

      {/* Login Modal */}
      <LoginModal
        open={showLoginModal}
        onOpenChange={setShowLoginModal}
      />
    </div>
  )
}