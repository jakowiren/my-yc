'use client'

import { useState, useEffect, useCallback } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
// import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { RefreshCw, ChevronDown, ChevronRight, Activity, Users, MessageSquare, Database } from 'lucide-react'
import { useAuth } from '@/lib/auth-context'

interface WorkspaceStatusProps {
  startupId: string
  className?: string
}

interface WorkspaceStatus {
  startup_id: string
  status: string
  workspace_path?: string
  last_activity?: string
  container_status: string
  agents?: {
    available: string[]
    count: number
    summaries: Record<string, any>
  }
  team_communication?: {
    recent_messages: any[]
    message_count: number
    shared_notes: any[]
    notes_count: number
  }
  metadata?: any
  timestamp: string
}

export function WorkspaceStatus({ startupId, className }: WorkspaceStatusProps) {
  const { session } = useAuth()
  const [status, setStatus] = useState<WorkspaceStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  const fetchStatus = useCallback(async () => {
    if (!session?.access_token || !startupId) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/workspace/agent?startup_id=${startupId}&action=status`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setStatus(data.workspace_status)
        setLastRefresh(new Date())
      } else if (response.status === 503) {
        // Workspace is cold-starting or not yet ready
        setError('Workspace is cold-starting. Send a message to wake it up.')
      } else {
        throw new Error(`Failed to fetch status: ${response.status}`)
      }
    } catch (err) {
      // For network errors or other issues, show a friendly message
      if (err instanceof Error && err.message.includes('503')) {
        setError('Workspace is cold-starting. Send a message to wake it up.')
      } else {
        setError(err instanceof Error ? err.message : 'Unknown error')
      }
    } finally {
      setLoading(false)
    }
  }, [session, startupId])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const getStatusColor = (status: string, containerStatus: string) => {
    if (status === 'error') return 'destructive'
    if (containerStatus === 'cold') return 'secondary'
    if (containerStatus === 'active') return 'default'
    return 'outline'
  }

  const getStatusIcon = (containerStatus: string) => {
    if (containerStatus === 'active') return <Activity className="h-3 w-3" />
    if (containerStatus === 'cold') return <Database className="h-3 w-3" />
    return null
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

  if (error) {
    const isColdStart = error.includes('cold-starting')
    return (
      <Card className={className}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-sm">
            Workspace Status
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchStatus}
              disabled={loading}
              className="h-6 w-6 p-0"
            >
              <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className={`text-sm ${isColdStart ? 'text-yellow-400' : 'text-destructive'}`}>
            {isColdStart ? '⚡ ' : ''}{error}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!status) {
    return (
      <Card className={className}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-sm">
            Workspace Status
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchStatus}
              disabled={loading}
              className="h-6 w-6 p-0"
            >
              <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">
            {loading ? 'Loading...' : 'No status available'}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-sm">
          Workspace Status
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchStatus}
            disabled={loading}
            className="h-6 w-6 p-0"
          >
            <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
        <CardDescription className="text-xs">
          {lastRefresh ? `Last updated: ${formatTimeAgo(lastRefresh.toISOString())}` : ''}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Container Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Container</span>
          <Badge
            variant={getStatusColor(status.status, status.container_status)}
            className="text-xs flex items-center gap-1"
          >
            {getStatusIcon(status.container_status)}
            {status.container_status}
          </Badge>
        </div>

        {/* Last Activity */}
        {status.last_activity && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Last Activity</span>
            <span className="text-xs text-muted-foreground">
              {formatTimeAgo(status.last_activity)}
            </span>
          </div>
        )}

        {/* Agents Summary */}
        {status.agents && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium flex items-center gap-1">
              <Users className="h-3 w-3" />
              Agents
            </span>
            <span className="text-xs text-muted-foreground">
              {status.agents.count} active
            </span>
          </div>
        )}

        {/* Team Communication Summary */}
        {status.team_communication && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium flex items-center gap-1">
              <MessageSquare className="h-3 w-3" />
              Team Board
            </span>
            <span className="text-xs text-muted-foreground">
              {status.team_communication.message_count} messages
            </span>
          </div>
        )}

        {/* Expandable Debug Info */}
        <div>
          <Button
            variant="ghost"
            className="w-full h-6 p-0 text-xs justify-between"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            Debug Info
            {isExpanded ?
              <ChevronDown className="h-3 w-3" /> :
              <ChevronRight className="h-3 w-3" />
            }
          </Button>
          {isExpanded && (
            <div className="mt-2">
              <div className="text-xs bg-muted/50 rounded p-2 font-mono">
                <pre className="whitespace-pre-wrap break-all">
                  {JSON.stringify({
                    startup_id: status.startup_id,
                    status: status.status,
                    container_status: status.container_status,
                    workspace_path: status.workspace_path,
                    agents_available: status.agents?.available || [],
                    messages_count: status.team_communication?.message_count || 0,
                    notes_count: status.team_communication?.notes_count || 0,
                    timestamp: status.timestamp
                  }, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}