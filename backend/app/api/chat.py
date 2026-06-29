from torch import chunk

from fastapi import APIRouter
from pydantic import BaseModel

from app.retrieval.retriever import(
    retrieve_context
)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class QuestionRequest(BaseModel):
    question : str

@router.post("")
def ask_question(request: QuestionRequest):
    retrieved_chunks = generate_answer(
        request.question
    )

    answer = generate.generate_answer(
        request.question,
        retrieved_chunks
    )

    return{
        "question" : request.question,
        "answer": answer,
        "sources":[
            {
                "page" : chunk["page"],
                "score": round(
                    chunk["score"],
                    4
                )
            }

            for chunk in retrieved_chunks
        ]
    }
   
