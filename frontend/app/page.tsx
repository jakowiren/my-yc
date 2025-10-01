'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sparkles, Send, LogOut } from "lucide-react"
import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { LoginModal } from "@/components/chat/LoginModal"
import { StartupsList } from "@/components/startups/StartupsList"
import { useRouter } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { StartupInsert } from "@/lib/types/supabase"
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
  const router = useRouter()
  const { user, loading, signOut } = useAuth()
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [promptIndex, setPromptIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)
  const [inputValue, setInputValue] = useState("")
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [isCreatingStartup, setIsCreatingStartup] = useState(false)


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


  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    if (!user) {
      setShowLoginModal(true)
      return
    }

    setIsCreatingStartup(true)

    try {
      // Create new startup in Supabase first
      const startupData: StartupInsert = {
        user_id: user.id,
        status: 'active'
      }

      const { data: startup, error } = await supabase
        .from('startups')
        .insert(startupData)
        .select()
        .single()

      if (error) {
        console.error('Failed to create startup:', error)
        setIsCreatingStartup(false)
        if (error.message.includes('Maximum of 5 active startups')) {
          alert('You have reached the maximum of 5 startups. Please delete some old ones first.')
          return
        }
        alert('Failed to create startup. Please try again.')
        return
      }

      // Navigate to chat page using Supabase startup ID
      const encodedMessage = encodeURIComponent(inputValue)
      router.push(`/chat/${startup.id}?message=${encodedMessage}`)
      // Don't clear loading state here - let the navigation happen
    } catch (error) {
      console.error('Error creating startup:', error)
      setIsCreatingStartup(false)
      alert('Failed to create startup. Please try again.')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isCreatingStartup) {
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

          {/* Start Conversation Interface */}
          <div className="w-full max-w-4xl mx-auto">
            <div className="bg-black border border-white/10 rounded-lg transition-all duration-300 p-3">
              <Textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={inputValue ? '' : currentPrompt}
                disabled={isCreatingStartup}
                className="w-full resize-none min-h-[60px] bg-transparent border-0 text-white placeholder:text-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm disabled:opacity-60"
              />
              <div className="flex items-center justify-between mt-2">
                <div className="text-xs text-white/40">
                  {isCreatingStartup ? 'Starting conversation...' : !user ? 'Sign in to chat with Jason' : 'Press Enter to start your conversation'}
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isCreatingStartup}
                  className="text-white/50 hover:text-white text-xs px-2 py-1 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                >
                  {isCreatingStartup ? 'Starting...' : 'Start Chat'}
                </button>
              </div>
            </div>
          </div>

          {/* Separator Line */}
          <div className="w-full h-px bg-white/10 my-12"></div>

          {/* Your Startups Section */}
          <div className="w-full max-w-4xl mx-auto">
            <h2 className="text-xl font-light text-white mb-6">Your Startups</h2>
            <StartupsList />
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