import { useState, useCallback, useEffect } from 'react'
import { useUpload as useUploadStore } from '@/lib/store'
import { api } from '@/lib/api'
import { SUPPORTED_FORMATS, MAX_FILE_SIZE } from '@/lib/constants'

let documentsLoaded = false

export function useUpload() {
  const store = useUploadStore()
  const [validationError, setValidationError] = useState<string | null>(null)

  const loadDocuments = useCallback(async (force = false) => {
    if (documentsLoaded && !force) return

    try {
      const docs = await api.getDocuments()
      store.setDocuments(docs)
      documentsLoaded = true
    } catch (error) {
      const isCanceled =
        typeof error === 'object' &&
        error !== null &&
        'code' in error &&
        (error as { code?: string }).code === 'ERR_CANCELED'

      if (isCanceled) return

      console.error('[v0] Failed to load documents:', error)
    }
  }, [store])

  const validateFile = (file: File): string | null => {
    const extension = file.name.split('.').pop()?.toLowerCase() || ''

    if (!SUPPORTED_FORMATS.includes(extension)) {
      return `Unsupported format. Supported: ${SUPPORTED_FORMATS.join(', ')}`
    }

    if (file.size > MAX_FILE_SIZE) {
      return `File too large. Maximum: ${MAX_FILE_SIZE / 1024 / 1024}MB`
    }

    return null
  }

  const uploadFile = useCallback(
    async (file: File) => {
      const error = validateFile(file)
      if (error) {
        setValidationError(error)
        store.setUploadError(error)
        return false
      }

      setValidationError(null)
      store.setUploading(true)
      store.setUploadError(null)

      try {
        const response = await api.uploadDocument(file)

        // Prefer backend document metadata so delete/list stays in sync.
        if (response.document) {
          store.addDocument(response.document)
          documentsLoaded = true
        } else {
          await loadDocuments()
        }

        return true
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Upload failed'
        store.setUploadError(errorMessage)
        setValidationError(errorMessage)
        console.error('[v0] Upload error:', error)
        return false
      } finally {
        store.setUploading(false)
        store.setUploadProgress(0)
      }
    },
    [loadDocuments, store],
  )

  const removeDocument = useCallback(
    async (documentId: string) => {
      try {
        await api.deleteDocument(documentId)
        store.removeDocument(documentId)
      } catch (error) {
        console.error('[v0] Delete error:', error)
        store.setUploadError(
          error instanceof Error ? error.message : 'Delete failed',
        )
      }
    },
    [store],
  )

  // Listen for upload progress events
  useEffect(() => {
    const handleProgress = (event: Event) => {
      const customEvent = event as CustomEvent
      store.setUploadProgress(customEvent.detail.percentCompleted)
    }

    window.addEventListener('upload-progress', handleProgress)
    return () => {
      window.removeEventListener('upload-progress', handleProgress)
    }
  }, [store])

  useEffect(() => {
    if (store.documents.length === 0) {
      void loadDocuments()
    }
  }, [loadDocuments, store.documents.length])

  return {
    documents: store.documents,
    uploading: store.uploading,
    uploadProgress: store.uploadProgress,
    error: store.uploadError || validationError,
    uploadFile,
    removeDocument,
    setDocuments: store.setDocuments,
  }
}
