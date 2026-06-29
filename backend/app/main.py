from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router

app = FastAPI(
    title = "Multimodal RAG",
    version = "1.0"
)

app.include_router(upload_router)
app.include_router(chat_router)

@app.get("/")
def health():
    return {
        "status" : "ok"
    }