/**
 * Server-side Supabase client utilities
 */

import { createClient } from '@supabase/supabase-js'

// Singleton Supabase client for server-side operations
let supabaseInstance: ReturnType<typeof createClient> | null = null

export function getSupabaseServerClient() {
  if (!supabaseInstance) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY

    if (!url || !key) {
      throw new Error('Missing Supabase configuration')
    }

    supabaseInstance = createClient(url, key)
  }

  return supabaseInstance
}
