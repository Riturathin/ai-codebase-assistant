import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI
from app.ingest.loader import load_repository
from app.ingest.chunker import chunk_repository
from app.db.vector_store import VectorStore
from app.query.answer_generator import AnswerGenerator


app = FastAPI(title="AI Codebase Assistant Backend")
answer_generator = None


vector_store = None


@app.on_event("startup")
def startup_event():
    global vector_store, answer_generator
    vector_store = VectorStore()
    answer_generator = AnswerGenerator()



@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_repository(repo_path: str):
    files = load_repository(repo_path)
    chunks = chunk_repository(files)

    vector_store.add_chunks(chunks)

    return {
        "total_files": len(files),
        "total_chunks": len(chunks),
        "stored_embeddings": vector_store.count(),
    }
@app.post("/query")
def query_repository(question: str):
    retrieved = vector_store.query(question)

    answer = answer_generator.generate_answer(question, retrieved)

    return {
        "question": question,
        "answer": answer,
        "sources": retrieved,
    }

