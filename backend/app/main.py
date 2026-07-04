import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router

app = FastAPI(
    title = "Multimodal RAG",
    version = "1.0"
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_DIR = "extracted_images"
os.makedirs(IMAGE_DIR, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=IMAGE_DIR), name="images")

app.include_router(upload_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "status" : "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }