import os
import re
from typing import Dict, List

import chromadb
from openai import OpenAI

CHROMA_PATH = "./chroma_db"
COLLECTION_PREFIX = "repo_"


class VectorStore:
    def __init__(self, collection_name: str):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.openai_client = OpenAI()

        safe_name = self._sanitize_collection_name(collection_name)
        full_collection_name = f"{COLLECTION_PREFIX}{safe_name}"

        self.collection = self.client.get_or_create_collection(
            name=full_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _sanitize_collection_name(self, name: str) -> str:
        name = name.lower()
        name = re.sub(r"[^a-z0-9_-]", "_", name)
        return name

    # ------------------------
    # Generate Embeddings
    # ------------------------

    def _embed(self, texts: List[str]) -> List[List[float]]:
        response = self.openai_client.embeddings.create(model="text-embedding-3-small", input=texts)
        return [item.embedding for item in response.data]

    # ------------------------
    # Add Chunks
    # ------------------------

    def add_chunks(self, chunks: List[Dict], batch_size: int = 100):
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]

            documents = []
            metadatas = []
            ids = []

            for chunk in batch:
                chunk_id = f"{chunk['file_path']}:{chunk['start_line']}"

                documents.append(chunk["content"])
                metadatas.append(
                    {
                        "file_path": chunk["file_path"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                    }
                )
                ids.append(chunk_id)

            # ✅ Delete existing IDs to prevent duplication errors
            try:
                self.collection.delete(ids=ids)
            except Exception:
                pass  # Ignore if IDs don't exist

            embeddings = self._embed(documents)

            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )

            total_chunks = len(chunks)

    # ------------------------
    # Count
    # ------------------------

    def count(self):
        return self.collection.count()

    # ------------------------
    # Query
    # ------------------------

    def query(self, query_text: str, n_results: int = 8, score_threshold: float = 0.5):
        """
        Returns filtered relevant chunks based on similarity threshold.
        """

        query_embedding = self._embed([query_text])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted_results = []

        formatted_results = []

        for doc, meta, distance in zip(documents, metadatas, distances):
            print("Raw distance:", distance, "File:", meta["file_path"])

            formatted_results.append(
                {
                    "content": doc,
                    "file_path": meta["file_path"],
                    "start_line": meta["start_line"],
                    "end_line": meta["end_line"],
                    "distance": distance,
                }
            )

        return formatted_results

    # ------------------------
    # Getting Entire file content
    # ------------------------

    def get_file_content(self, file_path: str):
        results = self.collection.get(
            where={"file_path": file_path}, include=["documents", "metadatas"]
        )

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        # Pair and sort by start_line
        file_chunks = sorted(zip(documents, metadatas), key=lambda x: x[1]["start_line"])

        content = "\n".join(chunk[0] for chunk in file_chunks)

        return content

    # ------------------------
    # Delete Entire Repo Collection
    # ------------------------

    def delete_collection(self):
        self.client.delete_collection(self.collection.name)
