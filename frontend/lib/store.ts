import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Message, Settings, Document } from './types'

// Chat Store
interface ChatState {
  messages: Message[]
  loading: boolean
  error: string | null
  addMessage: (message: Message) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useChat = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  error: null,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  clearMessages: () => set({ messages: [] }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

// Upload Store
interface UploadState {
  documents: Document[]
  uploading: boolean
  uploadProgress: number
  uploadError: string | null
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  removeDocument: (id: string) => void
  setUploading: (uploading: boolean) => void
  setUploadProgress: (progress: number) => void
  setUploadError: (error: string | null) => void
}

export const useUpload = create<UploadState>((set) => ({
  documents: [],
  uploading: false,
  uploadProgress: 0,
  uploadError: null,
  setDocuments: (documents) => set({ documents }),
  addDocument: (document) =>
    set((state) => ({ documents: [...state.documents, document] })),
  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((d) => d.id !== id),
    })),
  setUploading: (uploading) => set({ uploading }),
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  setUploadError: (error) => set({ uploadError: error }),
}))

// Settings Store with persistence
interface SettingsState extends Settings {
  updateSettings: (partial: Partial<Settings>) => void
}

export const useSettings = create<SettingsState>(
  persist(
    (set) => ({
      darkMode: true,
      model: 'gemini-2.5-flash',
      topK: 5,
      temperature: 0.7,
      updateSettings: (partial) => set((state) => ({ ...state, ...partial })),
    }),
    {
      name: 'rag-settings',
    },
  ),
)
