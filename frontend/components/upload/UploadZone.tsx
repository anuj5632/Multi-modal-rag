'use client'

import { useState, useRef } from 'react'
import { useUpload } from '@/hooks/useUpload'
import { FileUp, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { SUPPORTED_FORMATS } from '@/lib/constants'

interface UploadZoneProps {
  compact?: boolean
}

export function UploadZone({ compact = false }: UploadZoneProps) {
  const { uploadFile, uploading, error } = useUpload()
  const [isDragActive, setIsDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true)
    } else if (e.type === 'dragleave') {
      setIsDragActive(false)
    }
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      await uploadFile(files[0])
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (files && files[0]) {
      await uploadFile(files[0])
      e.currentTarget.value = ''
    }
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  if (compact) {
    return (
      <div className="space-y-2">
        <label
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-3 cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-primary'
          }`}
        >
          <FileUp className="h-4 w-4 text-muted-foreground" />
          <p className="text-xs text-center text-muted-foreground mt-1">
            Drag & drop or click
          </p>
          <input
            ref={inputRef}
            type="file"
            accept={SUPPORTED_FORMATS.map((f) => `.${f}`).join(',')}
            onChange={handleFileSelect}
            disabled={uploading}
            className="hidden"
          />
        </label>

        {uploading && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="h-1 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse" />
            Uploading...
          </div>
        )}

        {error && (
          <div className="flex items-start gap-2 text-xs text-destructive">
            <AlertCircle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="w-full space-y-4">
      <motion.label
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
        animate={{
          scale: isDragActive ? 1.02 : 1,
          borderColor: isDragActive ? '#3b82f6' : undefined,
        }}
        className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary'
        }`}
      >
        <FileUp className="h-12 w-12 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold text-foreground">
          Upload Your Documents
        </h3>
        <p className="mt-2 text-center text-sm text-muted-foreground">
          Drag and drop your files here, or click to select
        </p>
        <p className="mt-3 text-xs text-muted-foreground">
          Supported formats: {SUPPORTED_FORMATS.join(', ').toUpperCase()}
        </p>
        <input
          ref={inputRef}
          type="file"
          accept={SUPPORTED_FORMATS.map((f) => `.${f}`).join(',')}
          onChange={handleFileSelect}
          disabled={uploading}
          className="hidden"
        />
      </motion.label>

      {uploading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-lg bg-muted/50 p-4"
        >
          <p className="text-sm font-medium text-foreground mb-2">Uploading...</p>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 30 }}
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
            />
          </div>
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start gap-3 rounded-lg bg-destructive/10 border border-destructive/30 p-3"
        >
          <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-sm text-destructive">Upload Error</p>
            <p className="text-xs text-destructive/80 mt-1">{error}</p>
          </div>
        </motion.div>
      )}
    </div>
  )
}
