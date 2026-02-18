# Backend Service

Steps to restart

1.source .venv/bin/activate : to get inside the virtual env 2. python -m uvicorn app.main:app --reload to restart the server 3. if there is an issue do a clean rm -rf .venv 4. reinstall

FastAPI-based service responsible for:

- Codebase ingestion
- Embedding generation
- Vector search
- Grounded answer generation
- Streaming responses

Implementation will evolve incrementally.
