# Architecture Overview

This system is designed as an internal developer productivity platform rather than a chatbot.

## Design Principles

- Grounded answers only (no hallucination)
- Code-aware, not keyword-based
- Metadata-preserving ingestion
- Incremental scalability (local → managed infra)

---

## High-Level Flow

1. A repository is ingested and split into logical code chunks
2. Each chunk is converted into a semantic embedding
3. Embeddings are stored in a vector database along with metadata
4. User questions are embedded and matched against stored chunks
5. Relevant code context is retrieved and passed to the language model
6. The model generates a grounded answer referencing real files

---

## Key Components

### Ingestion Layer
- Walks the repository
- Splits files into meaningful chunks
- Preserves file path, language, and line ranges

### Retrieval Layer
- Performs semantic similarity search
- Ranks and filters relevant code chunks

### Answer Generation
- Uses retrieved code as context
- Produces explanations, references, and insights
- Streams responses to the frontend

---

## Non-Goals

- Not a code editor
- Not a replacement for IDE tooling
- Not a generic chatbot
