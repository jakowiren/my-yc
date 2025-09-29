'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
// import { ScrollArea } from '@/components/ui/scroll-area'
import { RefreshCw, MessageSquare, Clock, User, AlertCircle, CheckCircle } from 'lucide-react'
import { useAuth } from '@/lib/auth-context'

interface TeamBoardProps {
  startupId: string
  className?: string
}

interface TeamMessage {
  id: string
  message: string
  author: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  tags: string[]
  timestamp: string
  startup_id: string
}

interface TeamBoardData {
  startup_id: string
  messages: TeamMessage[]
  count: number
  timestamp: string
}

export function TeamBoard({ startupId, className }: TeamBoardProps) {
  const { session } = useAuth()
  const [boardData, setBoardData] = useState<TeamBoardData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)

  const fetchTeamBoard = async () => {
    if (!session?.access_token || !startupId) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/workspace/agent?startup_id=${startupId}&action=team-board`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBoardData(data.team_board)
      } else {
        throw new Error(`Failed to fetch team board: ${response.status}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      fetchTeamBoard()
    }
  }, [isOpen, startupId, session])

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'destructive'
      case 'high': return 'default'
      case 'normal': return 'secondary'
      case 'low': return 'outline'
      default: return 'secondary'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent': return <AlertCircle className="h-3 w-3" />
      case 'high': return <AlertCircle className="h-3 w-3" />
      case 'normal': return <CheckCircle className="h-3 w-3" />
      case 'low': return <CheckCircle className="h-3 w-3" />
      default: return <CheckCircle className="h-3 w-3" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return timestamp
    }
  }

  const formatTimeAgo = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`

      const diffHours = Math.floor(diffMins / 60)
      if (diffHours < 24) return `${diffHours}h ago`

      const diffDays = Math.floor(diffHours / 24)
      return `${diffDays}d ago`
    } catch {
      return 'Unknown'
    }
  }

  const getAuthorColor = (author: string) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-green-100 text-green-800',
      'bg-purple-100 text-purple-800',
      'bg-orange-100 text-orange-800',
      'bg-pink-100 text-pink-800',
      'bg-indigo-100 text-indigo-800'
    ]
    const hash = author.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
    return colors[hash % colors.length]
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className={className}>
          <MessageSquare className="h-4 w-4 mr-2" />
          View Team Board
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Team Message Board
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchTeamBoard}
              disabled={loading}
              className="h-6 w-6 p-0"
            >
              <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Summary */}
          {boardData && (
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{boardData.count} messages total</span>
              <span>Last updated: {formatTimestamp(boardData.timestamp)}</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-destructive flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Error: {error}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Loading State */}
          {loading && !boardData && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground flex items-center gap-2">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Loading team messages...
                </div>
              </CardContent>
            </Card>
          )}

          {/* Empty State */}
          {boardData && boardData.messages.length === 0 && (
            <Card>
              <CardContent className="pt-6 text-center">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No messages on the team board yet.</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Ask the CEO to write a message to the team board to test the functionality!
                </p>
              </CardContent>
            </Card>
          )}

          {/* Messages */}
          {boardData && boardData.messages.length > 0 && (
            <div className="h-[400px] overflow-y-auto pr-4">
              <div className="space-y-3">
                {boardData.messages.map((message) => (
                  <Card key={message.id} className="transition-colors hover:bg-muted/50">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge
                            variant="secondary"
                            className={`text-xs ${getAuthorColor(message.author)}`}
                          >
                            <User className="h-3 w-3 mr-1" />
                            {message.author}
                          </Badge>
                          <Badge
                            variant={getPriorityColor(message.priority)}
                            className="text-xs flex items-center gap-1"
                          >
                            {getPriorityIcon(message.priority)}
                            {message.priority}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {formatTimeAgo(message.timestamp)}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-sm">{message.message}</p>
                      {message.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {message.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <div className="text-xs text-muted-foreground mt-2">
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Testing Instructions */}
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-blue-800">Testing Instructions</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-blue-700 space-y-1">
              <p>• Ask the CEO: &quot;Write a message to the team board saying &apos;Project kickoff at 3pm&apos;&quot;</p>
              <p>• Refresh this dialog to see the message appear</p>
              <p>• Log out, log back in, and ask CEO: &quot;What messages are on the team board?&quot;</p>
              <p>• This tests persistent memory and team communication tools</p>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  )
}