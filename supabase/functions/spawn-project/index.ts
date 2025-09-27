import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseServiceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const modalEndpointUrl = Deno.env.get('MODAL_ENDPOINT_URL') || 'https://your-modal-app.modal.run/spawn'

interface SpawnProjectRequest {
  startup_id: string
}

interface ModalSpawnRequest {
  project_id: string
  config: {
    title: string
    description: string
    design_doc: any
    user_id: string
  }
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

    // Update startup status to spawning
    const { error: updateError } = await supabaseAdmin
      .from('startups')
      .update({
        project_status: 'spawning',
        spawned_at: new Date().toISOString(),
        error_details: null
      })
      .eq('id', startup_id)

    if (updateError) {
      console.error('Failed to update startup status:', updateError)
      return new Response(
        JSON.stringify({ error: 'Failed to update startup status' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Generate unique project ID for Modal (startup UUID + timestamp)
    const modalProjectId = `${startup_id.slice(0, 8)}-${Date.now()}`

    // Prepare payload for Modal
    const modalPayload: ModalSpawnRequest = {
      project_id: modalProjectId,
      config: {
        title: startup.design_doc.title,
        description: startup.design_doc.executive_summary,
        design_doc: startup.design_doc,
        user_id: user.id
      }
    }

    console.log(`🤖 Calling Modal with project ID: ${modalProjectId}`)

    // Call Modal spawn endpoint
    try {
      const modalResponse = await fetch(modalEndpointUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(modalPayload)
      })

      if (!modalResponse.ok) {
        const modalError = await modalResponse.text()
        throw new Error(`Modal API error: ${modalResponse.status} - ${modalError}`)
      }

      const modalResult = await modalResponse.json()
      console.log(`✅ Modal spawn successful:`, modalResult)

      // Update startup with Modal project ID and GitHub URL
      const updateData: any = {
        modal_project_id: modalProjectId,
        project_status: modalResult.success ? 'completed' : 'error'
      }

      // Add GitHub URL if Modal agent was successful
      if (modalResult.success && modalResult.repo_url) {
        updateData.github_url = modalResult.repo_url
      }

      // Add error details if Modal agent failed
      if (!modalResult.success && modalResult.error) {
        updateData.error_details = modalResult.error
      }

      await supabaseAdmin
        .from('startups')
        .update(updateData)
        .eq('id', startup_id)

      return new Response(
        JSON.stringify({
          success: true,
          message: modalResult.success
            ? 'Project created successfully!'
            : 'Project spawning initiated',
          startup_id: startup_id,
          modal_project_id: modalProjectId,
          project_status: modalResult.success ? 'completed' : 'running',
          github_url: modalResult.repo_url || null,
          repo_name: modalResult.repo_name || null
        }),
        {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )

    } catch (modalError) {
      console.error('Modal spawn error:', modalError)

      // Update startup status to error
      await supabaseAdmin
        .from('startups')
        .update({
          project_status: 'error',
          error_details: `Modal spawn failed: ${modalError.message}`
        })
        .eq('id', startup_id)

      return new Response(
        JSON.stringify({
          success: false,
          error: 'Failed to spawn project in Modal',
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