from dotenv import load_dotenv

load_dotenv()

import os
import re
import shutil
import tempfile
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Query
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


@app.get("/file")
def get_file(repo_id: str, file_path: str):
    try:
        vector_store = VectorStore(collection_name=repo_id)

        content = vector_store.get_file_content(file_path)

        if not content:
            raise HTTPException(status_code=404, detail="File not found")

        return {"content": content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------
# QUERY ENDPOINT
# ------------------------


def split_questions(text: str):
    """
    Splits numbered or multi-line questions into individual questions.
    """
    # Split by numbered format: 1. 2. 3.
    numbered = re.split(r"\n?\s*\d+\.\s*", text)

    # Remove empty strings
    questions = [q.strip() for q in numbered if q.strip()]

    if len(questions) > 1:
        return questions

    # Fallback: split by newline
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines


@app.post("/query")
async def query_repo(request: QueryRequest):
    try:
        vector_store = VectorStore(collection_name=request.repo_id)
        answer_generator = AnswerGenerator()

        questions = split_questions(request.question)

        is_multi = len(questions) > 1

        def stream():
            for idx, q in enumerate(questions, 1):
                retrieved_chunks = vector_store.query(q)

                # Only format header if truly multi-question
                if is_multi:
                    yield f"\n##Q## {idx}. {q}\n"

                for chunk in answer_generator.stream_answer(q, retrieved_chunks):
                    yield chunk

                if is_multi:
                    yield "\n\n"

        return StreamingResponse(stream(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------
# INGEST ENDPOINT
# ------------------------


@app.post("/ingest")
def ingest_repository(request: IngestRequest):
    try:
        repo_path = request.repo_path
        repo_id = request.repo_id

        # Create persistent repo directory
        repos_root = os.path.join(os.getcwd(), "temp_repos")
        os.makedirs(repos_root, exist_ok=True)

        repo_dir = os.path.join(repos_root, repo_id)

        # If repo_path is GitHub URL → clone persistently
        if repo_path.startswith("http"):
            if not os.path.exists(repo_dir):
                Repo.clone_from(repo_path, repo_dir)
            repo_path = repo_dir
        else:
            # Local path
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
