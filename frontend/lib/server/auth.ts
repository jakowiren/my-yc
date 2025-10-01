/**
 * Server-side authentication utilities
 */

import { NextRequest } from 'next/server'
import { getSupabaseServerClient } from './supabase'

export interface AuthenticatedUser {
  id: string
  email?: string
}

/**
 * Verify user authentication from Bearer token
 * @throws Error if authentication fails
 */
export async function verifyAuth(req: NextRequest): Promise<AuthenticatedUser> {
  const authHeader = req.headers.get('authorization')

  if (!authHeader?.startsWith('Bearer ')) {
    throw new Error('Missing or invalid authorization header')
  }

  const token = authHeader.split(' ')[1]
  const supabase = getSupabaseServerClient()

  const { data: { user }, error } = await supabase.auth.getUser(token)

  if (error || !user) {
    throw new Error('Unauthorized')
  }

  return {
    id: user.id,
    email: user.email,
  }
}
