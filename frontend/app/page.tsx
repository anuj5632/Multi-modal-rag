'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/layout/Header'
import { Sidebar } from '@/components/layout/Sidebar'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ChatInput } from '@/components/chat/ChatInput'
import { SettingsModal } from '@/components/settings/SettingsModal'
import { useChat } from '@/hooks/useChat'
import { useUpload } from '@/hooks/useUpload'
import { useSettings } from '@/lib/store'
import { api } from '@/lib/api'

export default function Home() {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [isConnected, setIsConnected] = useState(true)
  const { messages, loading, error, sendMessage, clearChat } = useChat()
  const { uploadFile } = useUpload()
  const settings = useSettings()

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.getHealth()
        setIsConnected(true)
      } catch {
        setIsConnected(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const handleFileUpload = async (file: File) => {
    await uploadFile(file)
  }

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      {/* Header */}
      <Header
        onSettingsClick={() => setSettingsOpen(true)}
        isConnected={isConnected}
      />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar onNewChat={clearChat} />

        {/* Chat area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <ChatWindow messages={messages} loading={loading} />

          {/* Error display */}
          {error && (
            <div className="border-t border-border bg-destructive/10 px-4 py-3 sm:px-6">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {/* Chat input */}
          <ChatInput
            onSend={sendMessage}
            onFileUpload={handleFileUpload}
            disabled={loading || !isConnected}
            showExamples={messages.length === 0}
          />
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </div>
  )
}
