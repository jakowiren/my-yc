import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/lib/auth-context'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'My YC',
  description: 'Transform ideas into reality with autonomous AI agents. Be the YC of your own startup portfolio.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="bg-black">
      <body className={`${inter.className} bg-black`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}