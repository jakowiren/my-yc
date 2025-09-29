'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import {
  Crown,
  Palette,
  Code,
  Database,
  TestTube,
  Settings,
  Bot,
  Zap,
  Users,
  MessageSquare
} from 'lucide-react'

interface AgentSelectorProps {
  selectedAgent: string
  onAgentChange: (agent: string) => void
  className?: string
}

const AVAILABLE_AGENTS = [
  {
    id: 'ceo',
    name: 'CEO',
    description: 'Strategic oversight, team coordination, and decision making',
    icon: Crown,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    capabilities: ['Strategic Planning', 'Team Management', 'GitHub Operations', 'Team Communication']
  },
  {
    id: 'frontend',
    name: 'Frontend Agent',
    description: 'React/Next.js development, UI components, and user experience',
    icon: Palette,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    capabilities: ['React/Next.js', 'CSS & Styling', 'Component Architecture', 'User Experience']
  },
  {
    id: 'backend',
    name: 'Backend Agent',
    description: 'API development, database design, and server-side logic',
    icon: Database,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    capabilities: ['API Development', 'Database Design', 'Authentication', 'Server Infrastructure']
  },
  {
    id: 'design',
    name: 'Design Agent',
    description: 'UI/UX design, design systems, and visual consistency',
    icon: Palette,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    capabilities: ['UI/UX Design', 'Design Systems', 'Brand Identity', 'Accessibility']
  },
  {
    id: 'testing',
    name: 'Testing Agent',
    description: 'Automated testing, quality assurance, and CI/CD setup',
    icon: TestTube,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    capabilities: ['Automated Testing', 'Quality Assurance', 'CI/CD Pipelines', 'Code Review']
  },
  {
    id: 'devops',
    name: 'DevOps Agent',
    description: 'Infrastructure, deployment, monitoring, and security',
    icon: Settings,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    capabilities: ['Infrastructure Management', 'Deployment Automation', 'Monitoring', 'Security']
  }
]

export function AgentSelector({ selectedAgent, onAgentChange, className }: AgentSelectorProps) {
  const [showDetails, setShowDetails] = useState(false)

  const selectedAgentData = AVAILABLE_AGENTS.find(agent => agent.id === selectedAgent)

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Agent Selection */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">Chat with:</span>
        </div>
        <select
          value={selectedAgent}
          onChange={(e) => onAgentChange(e.target.value)}
          className="w-[200px] px-3 py-2 border border-gray-300 rounded-md bg-white"
        >
          {AVAILABLE_AGENTS.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name}
            </option>
          ))}
        </select>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs"
        >
          {showDetails ? 'Hide' : 'Show'} Details
        </Button>
      </div>

      {/* Agent Details */}
      {showDetails && selectedAgentData && (
        <Card className={`${selectedAgentData.bgColor} ${selectedAgentData.borderColor} border`}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm">
              <selectedAgentData.icon className={`h-4 w-4 ${selectedAgentData.color}`} />
              {selectedAgentData.name}
            </CardTitle>
            <CardDescription className="text-xs">
              {selectedAgentData.description}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="text-xs font-medium mb-2 flex items-center gap-1">
                <Zap className="h-3 w-3" />
                Capabilities
              </div>
              <div className="flex flex-wrap gap-1">
                {selectedAgentData.capabilities.map((capability, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {capability}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Special notes for different agents */}
            {selectedAgent === 'ceo' && (
              <div className="text-xs text-muted-foreground space-y-1">
                <p className="flex items-center gap-1">
                  <Users className="h-3 w-3" />
                  <strong>Team Leader:</strong> Can coordinate with all other agents
                </p>
                <p className="flex items-center gap-1">
                  <MessageSquare className="h-3 w-3" />
                  <strong>Team Board:</strong> Can write messages for other agents to see
                </p>
              </div>
            )}

            {selectedAgent === 'frontend' && (
              <div className="text-xs text-muted-foreground">
                <p><strong>Specializes in:</strong> Building user interfaces with React/Next.js, managing component state, and creating responsive designs.</p>
              </div>
            )}

            {selectedAgent === 'backend' && (
              <div className="text-xs text-muted-foreground">
                <p><strong>Specializes in:</strong> Creating APIs, designing databases, implementing authentication, and server-side business logic.</p>
              </div>
            )}

            {selectedAgent === 'design' && (
              <div className="text-xs text-muted-foreground">
                <p><strong>Specializes in:</strong> Creating beautiful, user-friendly interfaces, establishing design systems, and ensuring visual consistency.</p>
              </div>
            )}

            {selectedAgent === 'testing' && (
              <div className="text-xs text-muted-foreground">
                <p><strong>Specializes in:</strong> Writing comprehensive tests, setting up CI/CD pipelines, and ensuring code quality.</p>
              </div>
            )}

            {selectedAgent === 'devops' && (
              <div className="text-xs text-muted-foreground">
                <p><strong>Specializes in:</strong> Managing infrastructure, automating deployments, implementing monitoring, and ensuring security.</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Testing Reminder */}
      {selectedAgent === 'ceo' && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-4">
            <div className="text-xs text-green-700 space-y-1">
              <p><strong>💡 Testing Tip:</strong> Try asking the CEO to write a message to the team board!</p>
              <p>Example: &quot;Please write to the team board that we&apos;re starting Phase 1 development&quot;</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}