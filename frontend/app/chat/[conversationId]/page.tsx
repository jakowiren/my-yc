'use client'

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeft, Send, MessageSquare, Zap } from "lucide-react"
import { useState, useEffect, useRef } from "react"
import { useAuth } from "@/lib/auth-context"
import { useStartup } from "@/lib/hooks/use-startup"
import { ChatMessageComponent } from "@/components/chat/ChatMessage"
import { DesignDocument } from "@/components/chat/DesignDocument"
import { AgentSelector } from "@/components/agent-selector"
import { WorkspaceStatus } from "@/components/workspace-status"
import { TeamBoard } from "@/components/team-board"
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
  const { user, session } = useAuth()
  const { startup, messages, isLoading, error, sendMessage, loadStartup } = useStartup()
  const [inputValue, setInputValue] = useState("")
  const [isStartingProject, setIsStartingProject] = useState(false)
  const [activeTab, setActiveTab] = useState<'planning' | 'action'>('planning')
  const [selectedAgent, setSelectedAgent] = useState('ceo')
  const hasInitializedRef = useRef(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  // Get startup ID from URL params (this is the Supabase startup ID)
  const startupId = params.conversationId
  const initialMessage = searchParams.get('message')

  // Load startup and messages when component mounts
  useEffect(() => {
    if (startupId && user) {
      loadStartup(startupId)
    }
  }, [startupId, user, loadStartup])

  // Send initial message after startup is loaded
  useEffect(() => {
    if (initialMessage && !hasInitializedRef.current && startup && user) {
      console.log('📤 Sending initial message:', initialMessage)
      hasInitializedRef.current = true
      sendMessage(initialMessage)
    }
  }, [initialMessage, startup, user, sendMessage])

  // Switch to Action tab when workspace is ready
  useEffect(() => {
    if (startup?.project_status === 'workspace_ready' && startup?.ceo_status === 'ready') {
      setActiveTab('action')
    }
  }, [startup?.project_status, startup?.ceo_status])

  // Filter messages based on active tab
  const filteredMessages = messages.filter(message => {
    // For new messages with agent metadata, use that
    if (message.metadata?.agent) {
      return activeTab === 'planning' ? message.metadata.agent === 'jason' : message.metadata.agent === 'ceo'
    }

    // For existing messages without metadata, fall back to timestamp logic
    if (activeTab === 'planning') {
      // Planning tab shows messages before project was spawned
      const spawnTime = startup?.spawned_at ? new Date(startup.spawned_at).getTime() : Date.now()
      return message.timestamp < spawnTime
    } else {
      // Action tab shows messages after project was spawned
      const spawnTime = startup?.spawned_at ? new Date(startup.spawned_at).getTime() : 0
      return message.timestamp >= spawnTime
    }
  })

  // Determine if user can send messages in current tab
  const canSendMessage = activeTab === 'planning'
    ? startup?.project_status !== 'completed'
    : startup?.project_status === 'completed' && startup?.ceo_status === 'ready'

  // Get appropriate AI name for current tab
  const currentAIName = activeTab === 'planning' ? 'Jason' : 'CEO'

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
      // Pass the selected agent for workspace chats
      const agentToUse = activeTab === 'action' ? selectedAgent : undefined
      await sendMessage(inputValue, agentToUse)
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

  const handleStartProject = async () => {
    if (!startup?.design_doc) return

    setIsStartingProject(true)
    try {
      console.log('🚀 Starting project for startup:', startup.id)

      // Call Supabase edge function to spawn project
      const response = await fetch('/api/spawn-project', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
        body: JSON.stringify({
          startup_id: startup.id
        })
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || 'Failed to start project')
      }

      console.log('✅ Project spawn result:', result)
      console.log('🔄 Reloading startup data for ID:', startup.id)

      // Reload startup to get updated status
      if (startup.id) {
        const reloadedStartup = await loadStartup(startup.id)
        console.log('✅ Startup reloaded, new status:', reloadedStartup?.project_status)
      }

      // Show success message with GitHub link if available
      if (result.github_url) {
        const viewRepo = confirm(
          `🎉 ${result.message}\n\nRepository: ${result.repo_name}\n\nWould you like to view your new GitHub repository?`
        )
        if (viewRepo) {
          window.open(result.github_url, '_blank')
        }
      } else {
        alert(`🎉 ${result.message}`)
      }

    } catch (error) {
      console.error('Failed to start project:', error)
      alert(`Failed to start project: ${error instanceof Error ? error.message : String(error)}`)
    } finally {
      setIsStartingProject(false)
    }
  }

  return (
    <div className="h-screen bg-black text-white flex flex-col">
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-10 bg-black border-b border-white/10">
        <div className="container mx-auto max-w-4xl p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-white/70 hover:text-white">
                <ArrowLeft size={20} />
              </Link>
              <h1 className="text-xl font-light">{startup?.title || "New Startup"}</h1>
            </div>
            <span className="text-white/50 text-sm">Startup {startupId.slice(0, 8)}</span>
          </div>

          {/* Tabs */}
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('planning')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'planning'
                  ? 'bg-white/10 text-white border border-white/20'
                  : 'text-white/60 hover:text-white/80 hover:bg-white/5'
              }`}
            >
              <MessageSquare size={16} />
              <span>Planning</span>
              {startup?.project_status === 'designing' || startup?.project_status === 'design_ready' ? (
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              ) : null}
            </button>
            <button
              onClick={() => setActiveTab('action')}
              disabled={startup?.project_status !== 'workspace_ready' || startup?.ceo_status !== 'ready'}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'action'
                  ? 'bg-white/10 text-white border border-white/20'
                  : 'text-white/60 hover:text-white/80 hover:bg-white/5'
              } ${
                startup?.project_status !== 'workspace_ready' || startup?.ceo_status !== 'ready'
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              }`}
            >
              <Zap size={16} />
              <span>Action</span>
              {startup?.project_status === 'completed' && startup?.ceo_status === 'ready' && (
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Scrollable Messages Area */}
      <main ref={messagesContainerRef} className="flex-1 overflow-y-auto messages-scroll pt-32 pb-32">
        <div className="container mx-auto max-w-4xl p-4">
          <div className="space-y-4">
            {/* Tab-specific content */}
            {activeTab === 'planning' && startup?.project_status === 'workspace_ready' && (
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-4">
                <div className="text-yellow-400 text-sm font-medium mb-1">Planning Phase Complete</div>
                <div className="text-white/70 text-sm">
                  The design phase with Jason is complete. Switch to the Action tab to start working with your AI team.
                </div>
              </div>
            )}

            {activeTab === 'action' && (!startup?.project_status || startup?.project_status !== 'workspace_ready') && (
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 mb-4">
                <div className="text-blue-400 text-sm font-medium mb-1">Action Phase Not Ready</div>
                <div className="text-white/70 text-sm">
                  Complete the planning phase and start your workspace to begin working with the AI team.
                </div>
              </div>
            )}

            {/* Workspace Interface - Show in Action tab when ready */}
            {activeTab === 'action' && startup?.project_status === 'workspace_ready' && (
              <div className="space-y-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg mb-4">
                <h4 className="text-sm font-medium text-blue-400 mb-3">🚀 Your AI Workspace is Ready!</h4>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <WorkspaceStatus startupId={startupId} />
                  <div className="space-y-2">
                    <TeamBoard startupId={startupId} />
                    <p className="text-xs text-blue-300/70">Test persistent memory by asking the CEO to write messages to the team board.</p>
                  </div>
                </div>

                <AgentSelector
                  selectedAgent={selectedAgent}
                  onAgentChange={setSelectedAgent}
                  className="mt-4"
                />

                <div className="text-sm text-blue-300/80 space-y-1 mt-4">
                  <p><strong>💡 Next Steps:</strong></p>
                  <p>• Ask the CEO: "Create a GitHub repository for our project"</p>
                  <p>• Test team communication: "Write to the team board that we're starting development"</p>
                  <p>• Switch between different AI agents (Frontend, Backend, Design, etc.)</p>
                </div>
              </div>
            )}

            {filteredMessages.map((message) => (
              <ChatMessageComponent key={message.id} message={message} />
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/10 px-4 py-3 rounded-lg">
                  <div className="text-xs text-white/60 mb-1 font-medium">{currentAIName}</div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse delay-100"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse delay-200"></div>
                  </div>
                </div>
              </div>
            )}

            {/* Design Document Display - Only in Planning tab */}
            {activeTab === 'planning' && startup?.design_doc && (
              <div className="mt-6">
                <DesignDocument
                  designDoc={startup.design_doc}
                  projectStatus={startup.project_status}
                  githubUrl={startup.github_url}
                  onStartProject={handleStartProject}
                  isStarting={isStartingProject}
                />
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
              placeholder={
                canSendMessage
                  ? `Continue the conversation with ${currentAIName}...`
                  : activeTab === 'planning'
                  ? "Planning phase is complete"
                  : "Start your project to chat with CEO"
              }
              className="w-full resize-none min-h-[60px] bg-transparent border-0 text-white placeholder:text-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
              disabled={isLoading || !canSendMessage}
            />
            <div className="flex items-center justify-between mt-2">
              <div className="text-xs text-white/40">
                {canSendMessage ? `Chatting with ${currentAIName}` :
                 activeTab === 'planning' ? 'Planning phase complete' :
                 'CEO not available yet'}
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading || !canSendMessage}
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