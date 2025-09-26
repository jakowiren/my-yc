'use client'

import { useState } from 'react'
import { Startup } from '@/lib/types/supabase'
import { MessageSquare, Trash2, Calendar } from 'lucide-react'
import Link from 'next/link'

interface StartupCardProps {
  startup: Startup
  onDelete: (id: string) => void
}

export function StartupCard({ startup, onDelete }: StartupCardProps) {
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault() // Prevent navigation when clicking delete

    if (window.confirm('Are you sure you want to delete this startup conversation?')) {
      setIsDeleting(true)
      try {
        await onDelete(startup.id)
      } catch (error) {
        console.error('Failed to delete startup:', error)
        setIsDeleting(false)
      }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Link href={`/chat/${startup.id}`} className="block group">
      <div className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-all duration-200 group-hover:border-white/20 relative">
        {/* Delete button */}
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Delete startup"
        >
          <Trash2 size={14} className="text-red-400 hover:text-red-300" />
        </button>

        {/* Content */}
        <div className="pr-8"> {/* Add padding to avoid delete button */}
          <h3 className="text-white font-medium text-sm mb-2 line-clamp-2">
            {startup.title || 'Untitled Startup'}
          </h3>

          <div className="flex items-center justify-between text-xs text-white/50">
            <div className="flex items-center space-x-2">
              <MessageSquare size={12} />
              <span>Chat with Jason</span>
            </div>

            <div className="flex items-center space-x-1">
              <Calendar size={12} />
              <span>{formatDate(startup.created_at)}</span>
            </div>
          </div>

          {/* Status indicator */}
          <div className="mt-2">
            <span className={`inline-block px-2 py-1 text-xs rounded-full ${
              startup.status === 'active'
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
            }`}>
              {startup.status === 'active' ? 'Active' : 'Archived'}
            </span>
          </div>
        </div>
      </div>
    </Link>
  )
}