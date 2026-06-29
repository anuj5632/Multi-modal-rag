'use client'

import { AlertCircle, RotateCcw } from 'lucide-react'
import { motion } from 'framer-motion'

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  showRetry?: boolean
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  onRetry,
  showRetry = true,
}: ErrorStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center min-h-[400px] px-4 py-12"
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 border border-destructive/20">
        <AlertCircle className="h-8 w-8 text-destructive" />
      </div>

      <h2 className="mt-6 text-2xl font-bold text-foreground">{title}</h2>

      <p className="mt-2 text-center text-muted-foreground max-w-md">{message}</p>

      {showRetry && onRetry && (
        <button
          onClick={onRetry}
          className="mt-6 flex items-center gap-2 rounded-lg bg-destructive/10 border border-destructive/30 px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/20 transition-colors"
        >
          <RotateCcw className="h-4 w-4" />
          Try Again
        </button>
      )}
    </motion.div>
  )
}
