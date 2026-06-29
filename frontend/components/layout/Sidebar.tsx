'use client'

import { useState } from 'react'
import { useUpload } from '@/hooks/useUpload'
import { useChat } from '@/hooks/useChat'
import { FileUp, Trash2, Menu, X } from 'lucide-react'
import { UploadZone } from '@/components/upload/UploadZone'
import { motion } from 'framer-motion'

interface SidebarProps {
  onNewChat?: () => void
}

export function Sidebar({ onNewChat }: SidebarProps) {
  const { documents, removeDocument } = useUpload()
  const { messages, clearChat } = useChat()
  const [isOpen, setIsOpen] = useState(false)

  const handleNewChat = () => {
    clearChat()
    onNewChat?.()
  }

  const handleDeleteDocument = async (id: string) => {
    await removeDocument(id)
  }

  const sidebarContent = (
    <>
      {/* Upload Section */}
      <div className="space-y-3 p-4">
        <button
          onClick={handleNewChat}
          className="w-full rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-2 text-sm font-medium text-white hover:shadow-lg transition-shadow"
        >
          + New Chat
        </button>
      </div>

      <div className="border-t border-border">
        {/* Upload Zone */}
        <div className="space-y-3 p-4">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Upload
          </h3>
          <UploadZone compact />
        </div>

        {/* Documents List */}
        {documents.length > 0 && (
          <div className="border-t border-border p-4 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Indexed Documents
            </h3>
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {documents.map((doc, index) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="group flex items-start justify-between rounded-lg bg-muted/50 p-2 text-xs hover:bg-muted transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-foreground truncate">
                      {doc.filename}
                    </p>
                    <p className="text-muted-foreground text-xs mt-0.5">
                      {doc.pages} pages • {doc.chunks} chunks
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="ml-2 rounded p-1 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                    aria-label="Delete document"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Chat History */}
        {messages.length > 0 && (
          <div className="border-t border-border p-4 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Recent Conversations
            </h3>
            <div className="space-y-2 max-h-[200px] overflow-y-auto">
              {messages
                .filter((m) => m.role === 'user')
                .slice(-5)
                .reverse()
                .map((msg) => (
                  <button
                    key={msg.id}
                    className="w-full text-left text-xs p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors truncate"
                  >
                    {msg.content}
                  </button>
                ))}
            </div>
          </div>
        )}
      </div>
    </>
  )

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed bottom-4 left-4 z-50 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 p-3 text-white shadow-lg"
        aria-label="Toggle sidebar"
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-64 flex-col border-r border-border bg-card">
        {sidebarContent}
      </aside>

      {/* Mobile drawer */}
      {isOpen && (
        <motion.div
          initial={{ x: -256 }}
          animate={{ x: 0 }}
          exit={{ x: -256 }}
          className="fixed inset-0 z-40 md:hidden"
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setIsOpen(false)}
          />
          <aside className="relative w-64 h-full bg-card border-r border-border overflow-y-auto flex flex-col">
            {sidebarContent}
          </aside>
        </motion.div>
      )}
    </>
  )
}
