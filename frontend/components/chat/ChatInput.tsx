'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Upload } from 'lucide-react'
import { EXAMPLE_QUERIES } from '@/lib/constants'

interface ChatInputProps {
  onSend?: (message: string) => void
  onFileUpload?: (file: File) => void
  disabled?: boolean
  showExamples?: boolean
}

export function ChatInput({
  onSend,
  onFileUpload,
  disabled = false,
  showExamples = true,
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }, [message])

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend?.(message)
      setMessage('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.currentTarget.files?.[0]
    if (file) {
      onFileUpload?.(file)
      e.currentTarget.value = ''
    }
  }

  const handleExampleClick = (query: string) => {
    onSend?.(query)
  }

  return (
    <div className="w-full space-y-3 p-4 sm:p-6">
      {/* Examples (shown when empty) */}
      {showExamples && message === '' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
          {EXAMPLE_QUERIES.map((query, idx) => (
            <button
              key={idx}
              onClick={() => handleExampleClick(query)}
              className="text-left rounded-lg border border-border bg-muted/30 p-2 text-xs hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
            >
              {query}
            </button>
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="flex gap-2">
        <div className="flex-1 flex gap-2 items-end rounded-lg glass border border-border bg-card p-3">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            disabled={disabled}
            className="flex-1 resize-none bg-transparent text-foreground placeholder-muted-foreground outline-none text-sm"
            rows={1}
          />

          {/* File upload button */}
          <label className="cursor-pointer rounded-lg p-2 hover:bg-muted transition-colors">
            <input
              type="file"
              accept=".pdf,.docx,.png,.jpg,.jpeg"
              onChange={handleFileSelect}
              disabled={disabled}
              className="hidden"
              aria-label="Upload file"
            />
            <Upload className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
          </label>
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 p-3 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all"
          aria-label="Send message"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>

      <p className="text-xs text-center text-muted-foreground">
        Press Shift+Enter for new line
      </p>
    </div>
  )
}
