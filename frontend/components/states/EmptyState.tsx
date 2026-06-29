'use client'

import { EXAMPLE_QUERIES } from '@/lib/constants'
import { BookOpen } from 'lucide-react'
import { motion } from 'framer-motion'

interface EmptyStateProps {
  onExampleClick?: (query: string) => void
}

export function EmptyState({ onExampleClick }: EmptyStateProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="flex flex-col items-center justify-center min-h-screen px-4 py-12"
    >
      <motion.div
        variants={itemVariants}
        className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-500/10 to-purple-600/10 border border-primary/20"
      >
        <BookOpen className="h-10 w-10 text-primary" />
      </motion.div>

      <motion.h1 variants={itemVariants} className="mt-6 text-3xl font-bold">
        Welcome to Knowledge Assistant
      </motion.h1>

      <motion.p
        variants={itemVariants}
        className="mt-2 text-center text-muted-foreground max-w-md"
      >
        Upload your documents to get started. Ask questions and get instant
        answers powered by AI.
      </motion.p>

      <motion.div
        variants={itemVariants}
        className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md"
      >
        {EXAMPLE_QUERIES.map((query, idx) => (
          <motion.button
            key={idx}
            variants={itemVariants}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onExampleClick?.(query)}
            className="rounded-lg border border-border bg-card hover:bg-muted p-4 text-sm text-left transition-colors"
          >
            <p className="font-medium text-foreground text-xs mb-1">Example</p>
            <p className="text-xs text-muted-foreground">{query}</p>
          </motion.button>
        ))}
      </motion.div>

      <motion.div
        variants={itemVariants}
        className="mt-12 text-center text-xs text-muted-foreground"
      >
        <p>📄 Upload PDFs, Word documents, and images</p>
        <p className="mt-2">🔍 Semantic search across all content</p>
        <p className="mt-2">🤖 AI-powered answers with source citations</p>
      </motion.div>
    </motion.div>
  )
}
