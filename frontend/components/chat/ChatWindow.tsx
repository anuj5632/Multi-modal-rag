'use client'

import { useEffect, useRef } from 'react'
import { Message } from '@/lib/types'
import { MessageBubble } from './MessageBubble'
import { LoadingBubble } from './LoadingBubble'
import { EmptyState } from '@/components/states/EmptyState'

interface ChatWindowProps {
  messages: Message[]
  loading?: boolean
}

export function ChatWindow({ messages, loading }: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current
      setTimeout(() => {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }, 0)
    }
  }, [messages, loading])

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto space-y-6 p-4 sm:p-6"
    >
      {messages.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {loading && <LoadingBubble />}
        </>
      )}
    </div>
  )
}
