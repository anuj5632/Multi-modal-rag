// API Types
export interface HealthResponse {
  status: string
}

export interface Document {
  id: string
  filename: string
  pages: number
  chunks: number
  images: number
  upload_time: string
  status: 'indexed' | 'processing' | 'error'
}

export interface UploadResponse {
  message: string
  pages: number
  chunks: number
  images: number
}

export interface Source {
  document_id: string
  document_name: string
  page: number
  confidence: number
  text: string
}

export interface ChatResponse {
  question: string
  answer: string
  sources: Source[]
}

// UI Types
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: Date
}

export interface UploadFile {
  id: string
  file: File
  progress: number
  status: 'uploading' | 'processing' | 'success' | 'error'
  error?: string
}

export interface Settings {
  darkMode: boolean
  model: string
  topK: number
  temperature: number
}
