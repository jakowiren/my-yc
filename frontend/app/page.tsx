'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sparkles, Send } from "lucide-react"
import { useState, useEffect } from "react"

const examplePrompts = [
  "Build a SaaS for small businesses",
  "Create a fitness app with AI coaching",
  "Design a fintech solution for Gen Z",
  "Build an e-commerce platform for creators",
  "Create a productivity tool for remote teams"
]

export default function Home() {
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
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-pink-500/20 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/10 bg-white/5 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                my-yc
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-purple-100 hover:text-white hover:bg-white/10">
                Examples
              </Button>
              <Button variant="ghost" className="text-purple-100 hover:text-white hover:bg-white/10">
                Docs
              </Button>
              <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 border-0">
                Sign In
              </Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 py-20">
        <div className="max-w-2xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 text-white">
              Become your own
              <br />
              <span className="bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent">
                investor
              </span>
            </h1>
          </div>

          {/* Chat Interface */}
          <div className="bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 shadow-2xl max-w-2xl mx-auto">
            {/* Chat Input */}
            <div className="p-8">
              <div className="flex space-x-4">
                <Textarea
                  placeholder={currentPrompt}
                  className="flex-1 resize-none min-h-[80px] bg-white/10 border-white/20 text-white placeholder:text-purple-200 focus:border-purple-300 focus:ring-purple-300/50 text-lg"
                />
                <Button size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 px-8 h-20">
                  <Send className="w-6 h-6" />
                </Button>
              </div>
            </div>
          </div>

          {/* Simple Footer */}
          <div className="text-center mt-20 text-purple-200 text-sm">
            <p>Built with ❤️ by autonomous AI agents</p>
          </div>
        </div>
      </main>
    </div>
  )
}