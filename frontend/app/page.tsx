'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sparkles, Send, LogOut } from "lucide-react"
import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import Link from "next/link"

const examplePrompts = [
  "Build a SaaS for small businesses",
  "Create a fitness app with AI coaching",
  "Design a fintech solution for Gen Z",
  "Build an e-commerce platform for creators",
  "Create a productivity tool for remote teams"
]

export default function Home() {
  const { user, loading, signOut } = useAuth()
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [promptIndex, setPromptIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)

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

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-blue-900 to-rose-500 relative overflow-hidden">

      {/* Header */}
      <header className="relative z-10 border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-white">
                my-yc
              </span>
            </div>
            <div className="flex items-center space-x-4">
              {loading ? (
                <div className="w-8 h-8 animate-spin rounded-full border-2 border-white/30 border-t-white"></div>
              ) : user ? (
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    {user.user_metadata?.avatar_url && (
                      <img
                        src={user.user_metadata.avatar_url}
                        alt="Profile"
                        className="w-8 h-8 rounded-full"
                      />
                    )}
                    <span className="text-white text-sm">
                      {user.user_metadata?.full_name || user.email}
                    </span>
                  </div>
                  <Button
                    onClick={signOut}
                    variant="ghost"
                    size="sm"
                    className="text-white/70 hover:text-white hover:bg-white/10"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </div>
              ) : (
                <Link href="/signin">
                  <Button className="bg-blue-600 hover:bg-blue-700 border-0">
                    Sign In
                  </Button>
                </Link>
              )}
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-16">
            <h1 className="text-6xl md:text-7xl font-bold tracking-tight mb-4 text-white">
              Become your own investor
            </h1>
            <p className="text-lg text-white/70 font-normal">
              Create apps and websites by chatting with AI
            </p>
          </div>

          {/* Input Interface */}
          <div className="w-full max-w-3xl mx-auto">
            <div className="bg-gray-900 rounded-2xl border border-gray-700 p-4">
              <Textarea
                placeholder={currentPrompt}
                className="w-full resize-none min-h-[100px] bg-transparent border-0 text-white placeholder:text-gray-400 focus:ring-0 text-base leading-relaxed"
              />
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-700">
                <div className="flex items-center space-x-3">
                  <button className="flex items-center space-x-1 px-2 py-1 bg-gray-800 rounded text-sm text-gray-300">
                    <span>Public</span>
                  </button>
                  <button className="flex items-center space-x-1 px-2 py-1 bg-green-900/30 text-green-400 rounded text-sm">
                    <span>⚡</span>
                    <span>Supabase</span>
                  </button>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-gray-800 rounded">
                    <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </button>
                  <button className="p-2 hover:bg-gray-800 rounded">
                    <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  )
}