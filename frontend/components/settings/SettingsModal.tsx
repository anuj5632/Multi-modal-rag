'use client'

import { useSettings } from '@/lib/store'
import { X } from 'lucide-react'
import { motion } from 'framer-motion'
import { MODELS } from '@/lib/constants'

interface SettingsModalProps {
  isOpen?: boolean
  onClose?: () => void
}

export function SettingsModal({ isOpen = false, onClose }: SettingsModalProps) {
  const { model, topK, temperature, updateSettings } = useSettings()

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="relative z-10 w-full max-w-md rounded-lg bg-card border border-border shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border p-6">
          <h2 className="text-lg font-semibold text-foreground">Settings</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 hover:bg-muted transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-6 p-6">
          {/* Model Selection */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              AI Model
            </label>
            <select
              value={model}
              onChange={(e) => updateSettings({ model: e.target.value })}
              className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {MODELS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {/* Top K Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-foreground">
                Retrieval Results (Top K)
              </label>
              <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded">
                {topK}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="20"
              value={topK}
              onChange={(e) => updateSettings({ topK: parseInt(e.target.value) })}
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <p className="text-xs text-muted-foreground mt-1">
              More results = more comprehensive but slower
            </p>
          </div>

          {/* Temperature Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-foreground">
                Creativity (Temperature)
              </label>
              <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded">
                {temperature.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={temperature}
              onChange={(e) =>
                updateSettings({ temperature: parseFloat(e.target.value) })
              }
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Lower = focused, Higher = creative
            </p>
          </div>

          {/* Info */}
          <div className="rounded-lg bg-muted/50 border border-border p-3 text-xs text-muted-foreground">
            <p className="font-medium text-foreground mb-1">About Settings</p>
            <p>
              Adjust these parameters to control how the AI retrieves and
              generates answers. Settings are saved locally.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 border-t border-border p-6">
          <button
            onClick={onClose}
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            Done
          </button>
        </div>
      </motion.div>
    </div>
  )
}
