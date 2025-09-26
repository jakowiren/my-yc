"use client"

import { useAuth } from '@/lib/auth-context'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface LoginModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function LoginModal({ open, onOpenChange }: LoginModalProps) {
  const { signInWithProvider } = useAuth()

  const handleSignIn = async (provider: 'google' | 'github') => {
    await signInWithProvider(provider)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-full max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-lg font-light text-center">Sign in to continue</DialogTitle>
          <DialogDescription className="text-center">
            You need to be signed in to chat with Jason
          </DialogDescription>
        </DialogHeader>

        {/* Auth Buttons */}
        <div className="space-y-3 mt-4">
          <button
            onClick={() => handleSignIn('google')}
            className="w-full text-white/70 hover:text-white border border-white/10 hover:border-white/20 rounded px-3 py-2 text-sm transition-colors"
          >
            Sign in with Google
          </button>

          <button
            onClick={() => handleSignIn('github')}
            className="w-full text-white/70 hover:text-white border border-white/10 hover:border-white/20 rounded px-3 py-2 text-sm transition-colors"
          >
            Sign in with GitHub
          </button>
        </div>
      </DialogContent>
    </Dialog>
  )
}