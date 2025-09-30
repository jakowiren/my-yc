import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

function extractRepoName(repoUrl: string | null): string | null {
  if (!repoUrl) return null
  const match = repoUrl.match(/github\.com\/[^\/]+\/([^\/]+)/)
  return match ? match[1] : null
}

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseServiceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
// Use new workspace initialization endpoint
const modalInitializeUrl = 'https://jakowiren--workspace-initialize.modal.run'

interface SpawnProjectRequest {
  startup_id: string
}

interface CEOInitializeRequest {
  startup_id: string
  design_doc: any
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Parse request body
    const { startup_id }: SpawnProjectRequest = await req.json()

    if (!startup_id) {
      return new Response(
        JSON.stringify({ error: 'startup_id is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`🚀 Spawning project for startup: ${startup_id}`)

    // Get authorization token
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Authorization header required' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const token = authHeader.replace('Bearer ', '')

    // Create Supabase client with service role for admin access
    const supabaseAdmin = createClient(supabaseUrl, supabaseServiceRoleKey)

    // Verify user authentication
    const { data: { user }, error: authError } = await supabaseAdmin.auth.getUser(token)
    if (authError || !user) {
      console.error('Authentication error:', authError)
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`✅ User authenticated: ${user.id}`)

    // Load startup and verify ownership
    const { data: startup, error: startupError } = await supabaseAdmin
      .from('startups')
      .select('*')
      .eq('id', startup_id)
      .eq('user_id', user.id)
      .single()

    if (startupError || !startup) {
      console.error('Startup not found or access denied:', startupError)
      return new Response(
        JSON.stringify({ error: 'Startup not found or access denied' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check if design document exists
    if (!startup.design_doc) {
      return new Response(
        JSON.stringify({ error: 'Design document not found. Complete the design with Jason first.' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check if project is already spawning/running
    if (['spawning', 'running', 'completed'].includes(startup.project_status)) {
      return new Response(
        JSON.stringify({
          error: `Project is already ${startup.project_status}`,
          github_url: startup.github_url
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`📋 Design document found for: ${startup.design_doc.title}`)

    // Update startup status to workspace_initializing
    const { error: updateError } = await supabaseAdmin
      .from('startups')
      .update({
        project_status: 'workspace_initializing',
        spawned_at: new Date().toISOString(),
        error_details: null,
        updated_at: new Date().toISOString()
      })
      .eq('id', startup_id)

    if (updateError) {
      console.error('Failed to update startup status:', updateError)
      return new Response(
        JSON.stringify({ error: 'Failed to update startup status' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Prepare payload for CEO initialization
    const ceoPayload: CEOInitializeRequest = {
      startup_id: startup_id,
      design_doc: startup.design_doc
    }

    console.log(`🚀 Initializing workspace for startup: ${startup_id}`)

    // Call Modal function to initialize CEO
    try {
      console.log(`🔗 Calling workspace initialization function: ${modalInitializeUrl}`)

      // Modal functions expect parameters as URL query params or form data
      const modalResponse = await fetch(modalInitializeUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          startup_id: ceoPayload.startup_id,
          design_doc: ceoPayload.design_doc
        })
      })

      if (!modalResponse.ok) {
        const modalError = await modalResponse.text()
        throw new Error(`Modal workspace initialization error: ${modalResponse.status} - ${modalError}`)
      }

      const ceoResult = await modalResponse.json()
      console.log(`✅ Workspace initialization result:`, ceoResult)

      // Update startup with workspace info using actual schema columns
      const updateData: any = {
        project_status: ceoResult.success ? 'workspace_ready' : 'error',
        container_endpoint: 'https://jakowiren--workspace-agent-stream.modal.run',
        ceo_status: ceoResult.success ? 'ready' : 'error',
        workspace_path: ceoResult.workspace_path || `/workspace/${startup_id}`,
        workspace_version: '2.0',
        workspace_created_at: new Date().toISOString(),
        workspace_last_updated: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      // GitHub repo will be created later by CEO agent during conversation
      // No longer expect immediate repo creation during workspace initialization

      // Add error details if workspace initialization failed
      if (!ceoResult.success && ceoResult.error) {
        updateData.error_details = ceoResult.error
      }

      await supabaseAdmin
        .from('startups')
        .update(updateData)
        .eq('id', startup_id)

      // Log workspace creation activity
      if (ceoResult.success) {
        await supabaseAdmin
          .from('workspace_activities')
          .insert({
            startup_id: startup_id,
            activity_type: 'workspace_created',
            activity_data: {
              workspace_path: `/workspace/${startup_id}`,
              repo_url: ceoResult.repo_url,
              team_plan: ceoResult.team_plan,
              startup_name: startup.design_doc?.title || 'Unknown Startup'
            }
          })
      }

      return new Response(
        JSON.stringify({
          success: true,
          message: ceoResult.success
            ? 'Workspace initialized successfully! You can now chat with the CEO to create your project.'
            : 'Workspace initialization in progress',
          startup_id: startup_id,
          container_endpoint: 'https://jakowiren--workspace-agent-stream.modal.run',
          project_status: updateData.project_status,
          github_url: null,  // Will be set when CEO creates repo during conversation
          repo_name: null,   // Will be set when CEO creates repo during conversation
          ceo_status: updateData.ceo_status,
          workspace_path: updateData.workspace_path,
          available_agents: ceoResult.available_agents || ['ceo', 'frontend', 'backend', 'design', 'testing']
        }),
        {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )

    } catch (modalError) {
      console.error('Modal workspace initialization error:', modalError)

      // Update startup status to error
      await supabaseAdmin
        .from('startups')
        .update({
          project_status: 'error',
          ceo_status: 'error',
          error_details: `Workspace initialization failed: ${modalError.message}`,
          last_activity: new Date().toISOString()
        })
        .eq('id', startup_id)

      return new Response(
        JSON.stringify({
          success: false,
          error: 'Failed to initialize workspace in Modal',
          details: modalError.message
        }),
        {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

  } catch (error) {
    console.error('Edge function error:', error)
    return new Response(
      JSON.stringify({
        success: false,
        error: 'Internal server error',
        details: error.message
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})