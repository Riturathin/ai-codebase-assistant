from dotenv import load_dotenv

load_dotenv()

import os
import shutil
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from git import Repo
from pydantic import BaseModel

from .db.vector_store import VectorStore
from .ingest.loader import FileLoader
from .query.answer_generator import AnswerGenerator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_loader = FileLoader()


# ------------------------
# Request Models
# ------------------------


class QueryRequest(BaseModel):
    repo_id: str
    question: str


class IngestRequest(BaseModel):
    repo_path: str
    repo_id: str


# ------------------------
# QUERY ENDPOINT
# ------------------------


@app.post("/query")
async def query_repo(request: QueryRequest):
    try:
        vector_store = VectorStore(collection_name=request.repo_id)

        # 🔥 Retrieve relevant chunks first
        retrieved_chunks = vector_store.query(request.question)

        answer_generator = AnswerGenerator()

        return StreamingResponse(
            answer_generator.stream_answer(request.question, retrieved_chunks),
            media_type="text/plain",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------
# INGEST ENDPOINT
# ------------------------


@app.post("/ingest")
def ingest_repository(request: IngestRequest):
    temp_dir = None

    try:
        repo_path = request.repo_path
        repo_id = request.repo_id

        if repo_path.startswith("http"):
            temp_dir = tempfile.mkdtemp()
            Repo.clone_from(repo_path, temp_dir)
            repo_path = temp_dir

        if not os.path.exists(repo_path):
            raise HTTPException(status_code=400, detail="Repository path not found.")

        vector_store = VectorStore(collection_name=repo_id)

        chunks = file_loader.load_repository(repo_path)
        vector_store.add_chunks(chunks)

        return {
            "repo_id": repo_id,
            "total_files": len(set(c["file_path"] for c in chunks)),
            "total_chunks": len(chunks),
            "stored_embeddings": vector_store.count(),
        }

    finally:
        if temp_dir:
            shutil.rmtree(temp_dir)
