'use client'

import { Source } from '@/lib/types'
import { FileText, Image as ImageIcon } from 'lucide-react'

interface SourceCardProps {
  source: Source
  onClick?: () => void
}

export function SourceCard({ source, onClick }: SourceCardProps) {
  const confidencePercentage = Math.round(source.confidence * 100)
  const confidenceColor =
    confidencePercentage >= 80
      ? 'text-green-500'
      : confidencePercentage >= 60
        ? 'text-yellow-500'
        : 'text-orange-500'

  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-lg bg-muted/50 p-3 hover:bg-muted transition-colors group"
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 rounded-lg bg-primary/10 p-2">
          <FileText className="h-4 w-4 text-primary" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm text-foreground truncate">
            {source.document_name}
          </p>
          <div className="flex items-center gap-2 mt-1.5 text-xs text-muted-foreground">
            <span>Page {source.page}</span>
            <span className="inline-flex items-center gap-1">
              <span className={confidenceColor}>●</span>
              <span>{confidencePercentage}% match</span>
            </span>
          </div>
        </div>
      </div>

      <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
        {source.text}
      </p>
    </button>
  )
}
