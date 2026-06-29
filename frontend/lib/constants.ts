export const SUPPORTED_FORMATS = ['pdf', 'docx', 'png', 'jpg', 'jpeg']
export const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

export const MODELS = [
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'claude-sonnet', label: 'Claude Sonnet' },
]

export const UPLOAD_STEPS = [
  'Extracting text',
  'Chunking',
  'Embedding',
  'Indexing',
]

export const EXAMPLE_QUERIES = [
  'What are the key findings?',
  'Summarize the main points',
  'What is the risk assessment?',
  'Extract financial data',
]
