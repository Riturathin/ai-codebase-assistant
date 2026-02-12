import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import os


class VectorStore:
    def __init__(self):
        # Persistent local storage
        self.client = chromadb.Client(
            settings=chromadb.Settings(
                persist_directory="./chroma_db",
                is_persistent=True,
            )
        )

        # OpenAI embedding function
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small",
        )

        self.collection = self.client.get_or_create_collection(
            name="codebase_chunks",
            embedding_function=self.embedding_function,
        )

    def add_chunks(self, chunks: List[Dict], batch_size: int = 100):
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]

            documents = []
            metadatas = []
            ids = []

            for chunk in batch:
                documents.append(chunk["content"])
                metadatas.append(
                    {
                        "file_path": chunk["file_path"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                    }
                )
                ids.append(f"{chunk['file_path']}:{chunk['start_line']}")

            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )


    def count(self):
        return self.collection.count()
    
    def query(self, query_text: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        formatted_results = []

        for doc, meta in zip(documents, metadatas):
            formatted_results.append(
                {
                    "content": doc,
                    "file_path": meta["file_path"],
                    "start_line": meta["start_line"],
                    "end_line": meta["end_line"],
                }
            )

        return formatted_results

