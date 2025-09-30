/**
 * Modal endpoints configuration
 * Uses environment variables with safe fallbacks to current hardcoded URLs
 */

// Legacy CEO endpoints (deprecated - use WORKSPACE_ENDPOINTS instead)
export const MODAL_ENDPOINTS = {
  /**
   * CEO chat streaming endpoint (DEPRECATED)
   * Environment: NEXT_PUBLIC_CEO_CHAT_ENDPOINT
   */
  CEO_CHAT: process.env.NEXT_PUBLIC_CEO_CHAT_ENDPOINT ||
           'https://jakowiren--chat-stream.modal.run',

  /**
   * CEO initialization endpoint (DEPRECATED)
   * Environment: NEXT_PUBLIC_CEO_INIT_ENDPOINT
   */
  CEO_INIT: process.env.NEXT_PUBLIC_CEO_INIT_ENDPOINT ||
           'https://jakowiren--my-yc-ceo-initialize.modal.run',

  /**
   * Health check endpoint for CEO services (DEPRECATED)
   * Environment: NEXT_PUBLIC_CEO_HEALTH_ENDPOINT
   */
  CEO_HEALTH: process.env.NEXT_PUBLIC_CEO_HEALTH_ENDPOINT ||
             'https://jakowiren--my-yc-ceo-chat.modal.run'
} as const

// New workspace endpoints (one container per startup, multiple agents)
export const WORKSPACE_ENDPOINTS = {
  /**
   * Workspace initialization endpoint
   * Environment: NEXT_PUBLIC_WORKSPACE_INIT_ENDPOINT
   */
  WORKSPACE_INIT: process.env.NEXT_PUBLIC_WORKSPACE_INIT_ENDPOINT ||
                 'https://jakowiren--my-yc-startup-workspaces-initialize.modal.run',

  /**
   * Agent invocation endpoint (non-streaming)
   * Environment: NEXT_PUBLIC_WORKSPACE_AGENT_ENDPOINT
   */
  AGENT_INVOKE: process.env.NEXT_PUBLIC_WORKSPACE_AGENT_ENDPOINT ||
               'https://jakowiren--my-yc-startup-workspaces-agent-invoke.modal.run',

  /**
   * Agent streaming endpoint
   * Environment: NEXT_PUBLIC_WORKSPACE_AGENT_STREAM_ENDPOINT
   */
  AGENT_STREAM: process.env.NEXT_PUBLIC_WORKSPACE_AGENT_STREAM_ENDPOINT ||
               'https://jakowiren--my-yc-startup-workspaces-agent-stream.modal.run',

  /**
   * Workspace status endpoint
   * Environment: NEXT_PUBLIC_WORKSPACE_STATUS_ENDPOINT
   */
  WORKSPACE_STATUS: process.env.NEXT_PUBLIC_WORKSPACE_STATUS_ENDPOINT ||
                   'https://jakowiren--my-yc-startup-workspaces-workspace-status.modal.run',

  /**
   * Team message board endpoint
   * Environment: NEXT_PUBLIC_WORKSPACE_TEAM_BOARD_ENDPOINT
   */
  TEAM_BOARD: process.env.NEXT_PUBLIC_WORKSPACE_TEAM_BOARD_ENDPOINT ||
             'https://jakowiren--my-yc-startup-workspaces-team-board.modal.run',

  /**
   * Health check endpoint for workspace services
   * Environment: NEXT_PUBLIC_WORKSPACE_HEALTH_ENDPOINT
   */
  WORKSPACE_HEALTH: process.env.NEXT_PUBLIC_WORKSPACE_HEALTH_ENDPOINT ||
                   'https://jakowiren--my-yc-startup-workspaces-health.modal.run'
} as const

/**
 * Validate that all endpoints are accessible URLs
 */
export function validateEndpoints(): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  // Check legacy endpoints
  for (const [key, url] of Object.entries(MODAL_ENDPOINTS)) {
    try {
      new URL(url)
    } catch (e) {
      errors.push(`Invalid URL for legacy ${key}: ${url}`)
    }
  }

  // Check workspace endpoints
  for (const [key, url] of Object.entries(WORKSPACE_ENDPOINTS)) {
    try {
      new URL(url)
    } catch (e) {
      errors.push(`Invalid URL for workspace ${key}: ${url}`)
    }
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * Get endpoint with optional path suffix (legacy)
 */
export function getEndpoint(endpoint: keyof typeof MODAL_ENDPOINTS, path?: string): string {
  const baseUrl = MODAL_ENDPOINTS[endpoint]
  return path ? `${baseUrl}${path}` : baseUrl
}

/**
 * Get workspace endpoint with optional path suffix
 */
export function getWorkspaceEndpoint(endpoint: keyof typeof WORKSPACE_ENDPOINTS, path?: string): string {
  const baseUrl = WORKSPACE_ENDPOINTS[endpoint]
  return path ? `${baseUrl}${path}` : baseUrl
}