"use client"

import { ChatMessage } from '@/lib/hooks/use-startup'

interface ChatMessageProps {
  message: ChatMessage
}

export function ChatMessageComponent({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-white/10 text-white ml-auto'
              : 'bg-white/5 text-white/90 border border-white/10'
          }`}
        >
          {!isUser && (
            <div className="text-xs text-white/60 mb-1 font-medium">Jason</div>
          )}
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        </div>
        <div className={`text-xs text-white/40 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  )
}