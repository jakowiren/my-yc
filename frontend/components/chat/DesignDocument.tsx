'use client'

import { StartupDesignDoc } from "@/lib/ai/design-doc-template"
import { Button } from "@/components/ui/button"
import { CheckCircle, Rocket, ExternalLink, Clock } from "lucide-react"
import { ProjectStatus } from "@/lib/types/supabase"

interface DesignDocumentProps {
  designDoc: StartupDesignDoc
  projectStatus: ProjectStatus
  githubUrl?: string | null
  onStartProject: () => void
  isStarting?: boolean
}

export function DesignDocument({
  designDoc,
  projectStatus,
  githubUrl,
  onStartProject,
  isStarting = false
}: DesignDocumentProps) {

  const getStatusDisplay = () => {
    switch (projectStatus) {
      case 'design_ready':
        return {
          icon: <CheckCircle className="w-4 h-4 text-green-400" />,
          text: "Design Complete",
          color: "text-green-400"
        }
      case 'workspace_initializing':
        return {
          icon: <Clock className="w-4 h-4 text-yellow-400 animate-spin" />,
          text: "Initializing Workspace...",
          color: "text-yellow-400"
        }
      case 'workspace_ready':
        return {
          icon: <Rocket className="w-4 h-4 text-blue-400" />,
          text: "Workspace Ready - Chat with AI Team",
          color: "text-blue-400"
        }
      case 'project_creating':
        return {
          icon: <Clock className="w-4 h-4 text-yellow-400 animate-spin" />,
          text: "Creating GitHub Project...",
          color: "text-yellow-400"
        }
      case 'completed':
        return {
          icon: <CheckCircle className="w-4 h-4 text-green-400" />,
          text: "Project Created Successfully",
          color: "text-green-400"
        }
      case 'error':
        return {
          icon: <div className="w-4 h-4 bg-red-400 rounded-full" />,
          text: "Error Occurred",
          color: "text-red-400"
        }
      default:
        return {
          icon: <Clock className="w-4 h-4 text-gray-400" />,
          text: "In Design",
          color: "text-gray-400"
        }
    }
  }

  const status = getStatusDisplay()
  const canStartWorkspace = projectStatus === 'design_ready'
  const showWorkspaceStatus = ['workspace_initializing', 'workspace_ready', 'project_creating', 'completed'].includes(projectStatus)

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white mb-2">{designDoc.title}</h3>
          <div className="flex items-center space-x-2">
            {status.icon}
            <span className={`text-sm ${status.color}`}>{status.text}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          {githubUrl && (
            <Button
              variant="outline"
              size="sm"
              asChild
              className="border-white/20 text-white hover:bg-white/10"
            >
              <a href={githubUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-3 h-3 mr-1" />
                View Repo
              </a>
            </Button>
          )}

          {canStartWorkspace && (
            <Button
              onClick={onStartProject}
              disabled={isStarting}
              className="bg-blue-600 hover:bg-blue-700 text-white"
              size="sm"
            >
              <Rocket className="w-3 h-3 mr-1" />
              {isStarting ? 'Initializing...' : 'Start Workspace'}
            </Button>
          )}
        </div>
      </div>

      {/* Executive Summary */}
      <div>
        <h4 className="text-sm font-medium text-white/80 mb-2">Executive Summary</h4>
        <p className="text-white/70 text-sm">{designDoc.executive_summary}</p>
      </div>

      {/* Problem & Solution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-medium text-white/80 mb-2">Problem Statement</h4>
          <p className="text-white/70 text-sm">{designDoc.problem_statement}</p>
        </div>
        <div>
          <h4 className="text-sm font-medium text-white/80 mb-2">Value Proposition</h4>
          <p className="text-white/70 text-sm">{designDoc.value_proposition}</p>
        </div>
      </div>

      {/* Target Market */}
      <div>
        <h4 className="text-sm font-medium text-white/80 mb-2">Target Market & User Persona</h4>
        <div className="space-y-2">
          <p className="text-white/70 text-sm"><strong>Market:</strong> {designDoc.target_market}</p>
          <p className="text-white/70 text-sm"><strong>User:</strong> {designDoc.user_persona}</p>
        </div>
      </div>

      {/* MVP Features */}
      <div>
        <h4 className="text-sm font-medium text-white/80 mb-2">MVP Features</h4>
        <ul className="space-y-1">
          {designDoc.mvp_features.map((feature, index) => (
            <li key={index} className="text-white/70 text-sm flex items-start">
              <span className="text-white/40 mr-2">•</span>
              {feature}
            </li>
          ))}
        </ul>
      </div>

      {/* Tech Stack */}
      <div>
        <h4 className="text-sm font-medium text-white/80 mb-2">Technical Stack</h4>
        <div className="flex flex-wrap gap-2">
          {designDoc.tech_stack.map((tech, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-white/10 text-white/70 rounded text-xs"
            >
              {tech}
            </span>
          ))}
        </div>
      </div>

      {/* Success Metrics */}
      <div>
        <h4 className="text-sm font-medium text-white/80 mb-2">Success Metrics</h4>
        <ul className="space-y-1">
          {designDoc.success_metrics.map((metric, index) => (
            <li key={index} className="text-white/70 text-sm flex items-start">
              <span className="text-white/40 mr-2">•</span>
              {metric}
            </li>
          ))}
        </ul>
      </div>

      {/* Next Steps */}
      <div>
        <h4 className="text-sm font-medium text-white/80 mb-2">Immediate Next Steps</h4>
        <ul className="space-y-1">
          {designDoc.immediate_next_steps.map((step, index) => (
            <li key={index} className="text-white/70 text-sm flex items-start">
              <span className="text-white/40 mr-2">•</span>
              {step}
            </li>
          ))}
        </ul>
      </div>


      {/* Metadata */}
      <div className="flex items-center justify-between pt-4 border-t border-white/10">
        <div className="flex space-x-4 text-xs text-white/50">
          {designDoc.category && (
            <span>Category: {designDoc.category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
          )}
          {designDoc.complexity_level && (
            <span>Complexity: {designDoc.complexity_level}</span>
          )}
          {designDoc.estimated_dev_time && (
            <span>Est. Time: {designDoc.estimated_dev_time}</span>
          )}
        </div>
      </div>
    </div>
  )
}