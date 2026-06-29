'use client'

import { Message } from '@/lib/types'
import { FileText, X } from 'lucide-react'
import { motion } from 'framer-motion'

interface RightPanelProps {
  isOpen?: boolean
  onClose?: () => void
  lastMessage?: Message
}

export function RightPanel({
  isOpen = false,
  onClose,
  lastMessage,
}: RightPanelProps) {
  if (!isOpen) return null

  const hasSources = lastMessage?.sources && lastMessage.sources.length > 0

  return (
    <>
      {/* Backdrop for mobile */}
      <div
        onClick={onClose}
        className="fixed inset-0 z-40 bg-black/50 md:hidden"
      />

      {/* Right Panel */}
      <motion.aside
        initial={{ x: 320 }}
        animate={{ x: 0 }}
        exit={{ x: 320 }}
        className="fixed right-0 top-0 bottom-0 z-50 w-80 border-l border-border bg-card md:relative md:border-l md:border-border md:bg-background md:z-0 md:static"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border p-4">
            <h3 className="font-semibold text-foreground">Details</h3>
            <button
              onClick={onClose}
              className="rounded-lg p-1 hover:bg-muted transition-colors md:hidden"
              aria-label="Close panel"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {hasSources ? (
              <>
                {/* Sources section */}
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                    Sources
                  </h4>
                  <div className="space-y-2">
                    {lastMessage?.sources?.map((source, idx) => (
                      <div
                        key={idx}
                        className="rounded-lg bg-muted/50 p-3 space-y-2"
                      >
                        <div className="flex items-start gap-2">
                          <div className="mt-0.5 rounded-lg bg-primary/10 p-1.5">
                            <FileText className="h-3.5 w-3.5 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-foreground truncate">
                              {source.document_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Page {source.page}
                            </p>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {Math.round(source.confidence * 100)}% match
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Message stats */}
                <div className="rounded-lg bg-muted/50 p-3 space-y-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Stats
                  </h4>
                  <div className="space-y-1 text-xs text-muted-foreground">
                    <p>
                      Sources:{' '}
                      <span className="text-foreground font-medium">
                        {lastMessage?.sources?.length}
                      </span>
                    </p>
                    <p>
                      Response length:{' '}
                      <span className="text-foreground font-medium">
                        {lastMessage?.content.length} chars
                      </span>
                    </p>
                    <p>
                      Generated:{' '}
                      <span className="text-foreground font-medium">
                        {lastMessage?.timestamp.toLocaleTimeString()}
                      </span>
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <FileText className="h-12 w-12 text-muted-foreground/30 mb-3" />
                <p className="text-sm text-muted-foreground">
                  No sources available. Ask a question to see source citations.
                </p>
              </div>
            )}
          </div>
        </div>
      </motion.aside>
    </>
  )
}
