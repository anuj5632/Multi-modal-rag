#  Multi-Modal RAG Assistant

> Enterprise AI Search Across Documents, Images, Audio & Structured Data

A production-inspired **Multi-Modal Retrieval-Augmented Generation (RAG)** system that enables users to upload documents and interact with them using natural language. The platform combines semantic search, vector databases, and Large Language Models to deliver grounded responses with source citations.

This project currently supports **PDF-based semantic search** and is designed to evolve into a fully multimodal knowledge assistant with support for images, audio, and structured data.

---

##  Features

### Current Features

-  PDF Upload & Processing
-  Semantic Search using BGE Embeddings
-  Intelligent Text Chunking
-  PDF Image Extraction
-  Qdrant Vector Database Integration
-  Gemini 2.5 Flash for Answer Generation
-  Source Citations with Confidence Scores
-  Document Management APIs
-  Document Deletion & Vector Cleanup
-  Modern React/Next.js Frontend

### Upcoming Features

-  Image Retrieval using CLIP
-  Audio Processing with Whisper
-  Structured Data Retrieval (CSV, Excel)
-  Hybrid Search (Dense + BM25)
-  Redis Semantic Cache
-  RAG Evaluation Dashboard (RAGAS)
-  Multi-Workspace Support

---

##  System Architecture

```text
                    ┌────────────────────┐
                    │ React/Next Frontend │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ FastAPI Backend    │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
  PDF Processing       Embedding Layer      LLM Generation
(PyMuPDF, Chunking)      (BGE Models)       (Gemini 2.5 Flash)
          │                   │
          └───────────┬───────┘
                      ▼
              ┌───────────────┐
              │ Qdrant Vector │
              │   Database    │
              └───────────────┘
```

---

##  Tech Stack

### Backend

- FastAPI
- PyMuPDF (fitz)
- Sentence Transformers
- Google Gemini API
- Qdrant
- Python Dotenv
- LangChain Text Splitters

### Frontend

- React / Next.js
- TailwindCSS
- Framer Motion
- Axios
- Lucide React
- React Markdown

### AI & Vector Search

- BGE Small / BGE-M3 Embeddings
- Gemini 2.5 Flash
- Qdrant Vector Database

---

##  Project Structure

```text
multi-modal-rag/

├── backend/
│
│   ├── app/
│   │
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   └── chat.py
│   │   │
│   │   ├── embeddings/
│   │   │   └── text_embedding.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── pdf_loader.py
│   │   │   ├── chunker.py
│   │   │   └── image_extractor.py
│   │   │
│   │   ├── llm/
│   │   │   └── generator.py
│   │   │
│   │   ├── retrieval/
│   │   │   └── retriever.py
│   │   │
│   │   ├── vectorstore/
│   │   │   └── qdrant_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│
└── README.md
```

---

##  Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/multi-modal-rag.git

cd multi-modal-rag
```

---

## Backend Setup

### Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Configure Environment Variables

Create:

```text
backend/.env
```

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## Run Qdrant

Using Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Dashboard:

```text
http://localhost:6333/dashboard
```

---

## Start Backend

```bash
cd backend

uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Frontend Setup

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

---

## 📡 API Endpoints

---

### Health Check

```http
GET /
```

Response:

```json
{
    "status": "running"
}
```

---

### Upload PDF

```http
POST /upload
```

Request:

```text
Content-Type:
multipart/form-data

file: annual_report.pdf
```

Response:

```json
{
    "message": "PDF uploaded successfully",
    "pages": 35,
    "chunks": 84,
    "images": 12,
    "document": {
        "id": "uuid",
        "filename": "annual_report.pdf",
        "status": "indexed"
    }
}
```

---

### List Documents

```http
GET /documents
```

Response:

```json
[
    {
        "id": "uuid",
        "filename": "annual_report.pdf",
        "pages": 35,
        "chunks": 84,
        "images": 12
    }
]
```

---

### Delete Document

```http
DELETE /documents/{document_id}
```

Response:

```json
{
    "message": "Document deleted"
}
```

---

### Chat with Documents

```http
POST /chat
```

Request:

```json
{
    "question": "What caused profit decline?"
}
```

Response:

```json
{
    "question": "What caused profit decline?",
    "answer": "Profits declined because operating expenses increased by 15%.",
    "sources": [
        {
            "page": 7,
            "score": 0.91
        }
    ]
}
```

---

##  RAG Pipeline

```text
PDF Upload
    │
    ▼
Text Extraction (PyMuPDF)
    │
    ▼
Chunk Creation
    │
    ▼
BGE Embeddings
    │
    ▼
Qdrant Storage
    │
    ▼
User Query
    │
    ▼
Semantic Retrieval
    │
    ▼
Gemini Generation
    │
    ▼
Grounded Response + Citations
```

---

##  Future Roadmap

### Version 2

- CLIP Image Embeddings
- Image Retrieval
- Gemini Vision Integration

### Version 3

- Whisper Audio Processing
- Audio Citations
- Meeting Transcript Search

### Version 4

- Hybrid Search (BM25 + Dense)
- Reranking
- Redis Semantic Cache
- RAGAS Evaluation Dashboard

### Version 5

- Multi-Workspace Support
- User Authentication
- Enterprise Deployment

---

##  Contributing

Contributions, issues, and feature requests are welcome.

```bash
Fork the repository

Create a feature branch

Commit your changes

Open a Pull Request
```

---

##  License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Anuj Chandrakar**

- B.Tech CSE, Shri Ramdeobaba College of Engineering and Management
- Backend Developer | Machine Learning Enthusiast | AI Engineer Aspirant

GitHub:

```text
https://github.com/anuj5632
```


---

⭐ If you found this project useful, consider giving it a star.
