import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/lib/auth-context'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'my-yc | AI-Powered Startup Incubator',
  description: 'Transform ideas into reality with autonomous AI agents. Be the YC of your own startup portfolio.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="bg-slate-950">
      <body className={`${inter.className} bg-slate-950`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}