import { useState, useCallback } from 'react'
import { useChat as useChatStore } from '@/lib/store'
import { useSettings } from '@/lib/store'
import { api } from '@/lib/api'
import { Message } from '@/lib/types'

export function useChat() {
  const store = useChatStore()
  const settings = useSettings()
  const [isStreaming, setIsStreaming] = useState(false)

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return

      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content,
        timestamp: new Date(),
      }
      store.addMessage(userMessage)
      store.setLoading(true)
      store.setError(null)

      try {
        setIsStreaming(true)
        const response = await api.sendMessage(
          content,
          settings.topK,
          settings.temperature,
        )

        // Add assistant message
        const assistantMessage: Message = {
          id: Date.now().toString() + '1',
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          timestamp: new Date(),
        }
        store.addMessage(assistantMessage)
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Failed to get response'
        store.setError(errorMessage)
        console.error('[v0] Chat error:', error)
      } finally {
        setIsStreaming(false)
        store.setLoading(false)
      }
    },
    [store, settings],
  )

  const clearChat = useCallback(() => {
    store.clearMessages()
    store.setError(null)
  }, [store])

  return {
    messages: store.messages,
    loading: store.loading || isStreaming,
    error: store.error,
    sendMessage,
    clearChat,
  }
}
