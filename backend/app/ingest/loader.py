import os
from typing import Dict, List

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
}

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".css",
    ".html",
}


class FileLoader:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def load_repository(self, repo_path: str) -> List[Dict]:
        files = self._read_files(repo_path)
        return self._chunk_files(files)

    def _read_files(self, repo_path: str) -> List[Dict]:
        file_objects = []

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

            for file in files:
                _, ext = os.path.splitext(file)

                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    file_objects.append(
                        {
                            "file_path": os.path.relpath(full_path, repo_path),
                            "content": content,
                        }
                    )

                except Exception:
                    continue

        return file_objects

    def _chunk_files(self, files: List[Dict]) -> List[Dict]:
        chunks = []

        for file in files:
            content = file["content"]
            file_path = file["file_path"]

            start = 0

            while start < len(content):
                end = start + self.chunk_size

                chunk_text = content[start:end]

                chunks.append(
                    {
                        "file_path": file_path,
                        "content": chunk_text,
                        "start_line": content[:start].count("\n") + 1,
                        "end_line": content[:end].count("\n") + 1,
                    }
                )

                start += self.chunk_size - self.overlap

        return chunks
