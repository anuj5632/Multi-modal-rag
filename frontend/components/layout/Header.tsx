'use client'

import { useState, useEffect } from 'react'
import { useSettings } from '@/lib/store'
import { Moon, Sun, Settings } from 'lucide-react'

interface HeaderProps {
  onSettingsClick?: () => void
  isConnected?: boolean
}

export function Header({ onSettingsClick, isConnected = true }: HeaderProps) {
  const { darkMode, updateSettings } = useSettings()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    const html = document.documentElement
    if (darkMode) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }, [darkMode, mounted])

  const toggleTheme = () => {
    updateSettings({ darkMode: !darkMode })
  }

  if (!mounted) return null

  return (
    <header className="glass sticky top-0 z-40 border-b">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <span className="text-sm font-bold text-white">RAG</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight text-foreground">
              Knowledge Assistant
            </h1>
            <p className="text-xs text-muted-foreground">
              {isConnected ? (
                <span className="flex items-center gap-1">
                  <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
                  Connected
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <span className="inline-block h-2 w-2 rounded-full bg-red-500" />
                  Disconnected
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="rounded-lg p-2 hover:bg-muted transition-colors"
            aria-label="Toggle theme"
          >
            {darkMode ? (
              <Sun className="h-5 w-5 text-muted-foreground" />
            ) : (
              <Moon className="h-5 w-5 text-muted-foreground" />
            )}
          </button>

          <button
            onClick={onSettingsClick}
            className="rounded-lg p-2 hover:bg-muted transition-colors"
            aria-label="Settings"
          >
            <Settings className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>
      </div>
    </header>
  )
}
