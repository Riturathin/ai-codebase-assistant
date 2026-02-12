from typing import List, Dict


def chunk_file(
    file_object: Dict,
    max_lines: int = 80,
) -> List[Dict]:
    """
    Split a file into chunks of max_lines.
    Preserve line numbers and metadata.
    """

    content = file_object["content"]
    file_path = file_object["file_path"]

    lines = content.split("\n")
    chunks = []

    for i in range(0, len(lines), max_lines):
        chunk_lines = lines[i : i + max_lines]

        chunk_content = "\n".join(chunk_lines)

        chunk = {
            "file_path": file_path,
            "content": chunk_content,
            "start_line": i + 1,
            "end_line": i + len(chunk_lines),
        }

        chunks.append(chunk)

    return chunks


def chunk_repository(
    file_objects: List[Dict],
    max_lines: int = 80,
) -> List[Dict]:
    """
    Chunk all files in the repository.
    """

    all_chunks = []

    for file_object in file_objects:
        file_chunks = chunk_file(file_object, max_lines=max_lines)
        all_chunks.extend(file_chunks)

    return all_chunks
