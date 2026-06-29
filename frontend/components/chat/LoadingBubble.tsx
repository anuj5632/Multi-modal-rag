'use client'

import { motion } from 'framer-motion'

export function LoadingBubble() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex justify-start gap-3"
    >
      <div className="mt-1 flex-shrink-0">
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
          <span className="text-xs font-bold text-white">AI</span>
        </div>
      </div>

      <div className="flex-1">
        <div className="rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Thinking</span>
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.span
                  key={i}
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{
                    duration: 1.5,
                    delay: i * 0.2,
                    repeat: Infinity,
                  }}
                  className="inline-block h-2 w-2 rounded-full bg-muted-foreground"
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
