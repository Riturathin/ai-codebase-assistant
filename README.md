# AI-Powered Codebase Assistant

An internal developer productivity tool that enables natural language exploration of large codebases.

This system allows engineers to ask questions like:
- Where is authentication handled?
- Which components use this API?
- Explain this file
- Identify potential performance bottlenecks

The assistant understands real repositories by ingesting source code, generating semantic embeddings, and answering questions using retrieval-augmented generation (RAG).

---

## Why this project exists

Modern engineering teams operate on large, long-lived codebases where:
- onboarding is slow
- ownership is distributed
- documentation is often outdated

This project is **internal AI tooling** to improve developer velocity, debugging efficiency, and architectural understanding.

---

## Core Capabilities

- Semantic understanding of real codebases
- Natural language question answering grounded in source code
- File-aware and metadata-aware responses
- Streaming answers for fast developer feedback

---

## High-Level Architecture

- **Frontend**: React-based chat interface with streaming responses and syntax highlighting
- **Backend**: Python + FastAPI service for ingestion, retrieval, and answer generation
- **AI Layer**: Embeddings + vector search over code chunks
- **Storage**: Local vector database (initially)

See `docs/architecture.md` for details.

---

## Status

🚧 Work in progress — building step by step with production-quality design decisions.

## Current Capabilities

- Repository ingestion (local path)
- Code chunking with metadata preservation
- OpenAI embeddings with batching
- Persistent Chroma vector store
- Semantic retrieval
- Grounded LLM-based answers with file citations

