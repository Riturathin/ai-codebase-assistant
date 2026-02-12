import os
from typing import List, Dict


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


def load_repository(repo_path: str) -> List[Dict]:
    """
    Walk a repository and return a list of file objects.

    Each file object contains:
    - file_path
    - content
    - size (bytes)
    """
    file_objects = []

    for root, dirs, files in os.walk(repo_path):
        # Filter ignored directories in-place
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
                        "size": len(content),
                    }
                )

            except Exception:
                # Skip unreadable files
                continue

    return file_objects
