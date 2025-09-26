'use client'

import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from 'next/link'

export default function SignInPage() {
  const { user, loading, signInWithProvider } = useAuth()
  const router = useRouter()

  // Redirect to home if already signed in
  useEffect(() => {
    if (!loading && user) {
      router.push('/')
    }
  }, [user, loading, router])

  const handleSignIn = async (provider: 'google' | 'github') => {
    await signInWithProvider(provider)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 animate-spin rounded-full border-2 border-white/30 border-t-white mx-auto mb-4"></div>
          <p className="text-white">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      {/* Sign In Card */}
      <div className="w-full max-w-sm px-6">
        <div className="bg-black border border-white/10 rounded-lg p-6">
          {/* Header */}
          <div className="text-center mb-6">
            <Link href="/">
              <h1 className="text-lg font-light text-white mb-2">my-yc</h1>
            </Link>
            <p className="text-white/50 text-sm">Sign in</p>
          </div>

          {/* Auth Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => handleSignIn('google')}
              className="w-full text-white/70 hover:text-white border border-white/10 hover:border-white/20 rounded px-3 py-2 text-sm transition-colors"
            >
              Google
            </button>

            <button
              onClick={() => handleSignIn('github')}
              className="w-full text-white/70 hover:text-white border border-white/10 hover:border-white/20 rounded px-3 py-2 text-sm transition-colors"
            >
              GitHub
            </button>
          </div>

          {/* Footer */}
          <div className="text-center mt-6">
            <Link href="/" className="text-white/40 hover:text-white/70 text-xs">
              ← Back
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}