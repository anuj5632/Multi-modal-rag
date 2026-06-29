import axios, { AxiosInstance } from 'axios'
import {
  ChatResponse,
  Document,
  HealthResponse,
  UploadResponse,
} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
})

export const api = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/health')
    return response.data
  },

  // Get documents
  async getDocuments(): Promise<Document[]> {
    const response = await apiClient.get<Document[]>('/documents')
    return response.data
  },

  // Upload document
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total,
          )
          // Emit progress event
          window.dispatchEvent(
            new CustomEvent('upload-progress', {
              detail: { percentCompleted },
            }),
          )
        }
      },
    })
    return response.data
  },

  // Delete document
  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`)
  },

  // Chat
  async sendMessage(
    question: string,
    topK: number = 5,
    temperature: number = 0.7,
  ): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/chat', {
      question,
      top_k: topK,
      temperature,
    })
    return response.data
  },
}

export default api
