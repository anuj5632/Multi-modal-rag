from fastapi import APIRouter
from pydantic import BaseModel

from app.retrieval.retriever import(
    retrieve_context
)
from app.llm.generator import generator

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class QuestionRequest(BaseModel):
    question : str
    top_k: int = 5
    temperature: float = 0.7

@router.post("")
def ask_question(request: QuestionRequest):
    retrieved_chunks = retrieve_context(
        request.question,
        top_k=request.top_k,
    )

    answer = generator.generate_answer(
        request.question,
        retrieved_chunks,
        temperature=request.temperature,
    )

    return{
        "question" : request.question,
        "answer": answer,
        "sources":[
            {
                "document_id": chunk.get("document_id", "unknown"),
                "document_name": chunk.get("document_name", "Document"),
                "page" : chunk["page"],
                "confidence": round(
                    chunk["score"],
                    4
                ),
                "text": chunk.get("text", ""),
            }

            for chunk in retrieved_chunks
        ]
    }
   
