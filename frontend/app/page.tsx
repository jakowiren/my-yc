'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sparkles, Send, LogOut } from "lucide-react"
import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
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
  const [currentPrompt, setCurrentPrompt] = useState("")
  const [promptIndex, setPromptIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)

  // Cursor tracking for star
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const star = document.getElementById('cursor-star')
      if (star) {
        star.style.left = `${e.clientX - 2}px`
        star.style.top = `${e.clientY - 2}px`
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

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
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Cursor Following Star */}
      <div
        id="cursor-star"
        className="fixed w-1 h-1 bg-white rounded-full pointer-events-none z-50 opacity-60 transition-all duration-75 ease-out"
        style={{ left: '-10px', top: '-10px' }}
      />

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

          {/* Input Interface */}
          <div className="w-full max-w-xl mx-auto">
            <div className="bg-black border border-white/10 rounded-lg p-3">
              <Textarea
                placeholder={currentPrompt}
                className="w-full resize-none min-h-[60px] bg-transparent border-0 text-white placeholder:text-white/40 focus:ring-0 text-sm"
              />
              <div className="flex items-center justify-end mt-2">
                <button className="text-white/50 hover:text-white text-xs px-2 py-1">Send</button>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  )
}