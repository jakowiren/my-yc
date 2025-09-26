'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { supabase } from '@/lib/supabase'
import { Startup } from '@/lib/types/supabase'
import { StartupCard } from './StartupCard'
import { Loader2 } from 'lucide-react'

export function StartupsList() {
  const { user } = useAuth()
  const [startups, setStartups] = useState<Startup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load user's startups
  useEffect(() => {
    if (!user) {
      setStartups([])
      setLoading(false)
      return
    }

    loadStartups()
  }, [user])

  const loadStartups = async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)

      const { data, error: fetchError } = await supabase
        .from('startups')
        .select('*')
        .eq('user_id', user.id)
        .neq('status', 'deleted') // Exclude soft-deleted startups
        .order('created_at', { ascending: false })

      if (fetchError) {
        throw new Error(fetchError.message)
      }

      setStartups(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load startups')
      console.error('Error loading startups:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteStartup = async (startupId: string) => {
    try {
      // Soft delete the startup
      const { error } = await supabase
        .from('startups')
        .update({ status: 'deleted' })
        .eq('id', startupId)

      if (error) {
        throw new Error(error.message)
      }

      // Remove from local state
      setStartups(prev => prev.filter(startup => startup.id !== startupId))
    } catch (err) {
      console.error('Error deleting startup:', err)
      throw err // Re-throw so the component can handle it
    }
  }

  if (!user) {
    return (
      <div className="text-center py-8">
        <p className="text-white/60 text-sm">Log in to see your startups</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-white/60" />
        <span className="ml-2 text-white/60 text-sm">Loading your startups...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-400 text-sm mb-2">Failed to load startups</p>
        <button
          onClick={loadStartups}
          className="text-white/60 hover:text-white text-xs underline"
        >
          Try again
        </button>
      </div>
    )
  }

  if (startups.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-white/40 text-sm mb-2">No startups yet</p>
        <p className="text-white/30 text-xs">Start a conversation with Jason to create your first startup</p>
      </div>
    )
  }

  return (
    <div>
      {/* Startup count */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-white/60 text-xs">
          {startups.length} of 5 startups
        </span>
        {startups.length >= 5 && (
          <span className="text-orange-400 text-xs">Limit reached</span>
        )}
      </div>

      {/* Startups grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {startups.map((startup) => (
          <StartupCard
            key={startup.id}
            startup={startup}
            onDelete={handleDeleteStartup}
          />
        ))}
      </div>
    </div>
  )
}