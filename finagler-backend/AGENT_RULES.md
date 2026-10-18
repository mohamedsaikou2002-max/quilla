# Rules for the coding agent (read before changing anything)

## Architecture (do not change)
Browser -> this backend (127.0.0.1:8000) -> LM Studio (127.0.0.1:1234/v1)
- Local abliterated model in LM Studio = the reasoner. It writes the final answer.
- Corpus excerpts (ChromaDB) are injected into the system prompt.
- No cloud AI provider or cloud API key is used.

## Hard rules
1. app/config.py is the only file that reads environment variables.
2. app/providers/local_llm.py is the only file that imports openai.
4. app/main.py contains routes only. No provider logic, no prompts beyond SYSTEM_PROMPT.
5. The frontend never sees any API key. No VITE_ / NEXT_PUBLIC_ key variables.
6. Do not add cloud AI providers or API-key integrations without an explicit request.
7. Do not rename, move, or restructure files or folders. Do not add frameworks.
8. One change per task. Run pytest after every change; all tests must pass.
9. New integrations (e.g. IBM Quantum / Qiskit) get their own file in app/providers/
   and their own route module, following the same pattern. Do not touch existing providers.
10. app/corpus/store.py is the only file that imports chromadb; app/corpus/loader.py is the only file that imports pypdf.
11. Embeddings are produced only by local_llm.embed(). Corpus modules never import openai.
12. Retrieval and context formatting live in app/corpus/retriever.py. main.py only calls them.
13. Corpus failures must never break /chat; they are reported in corpus_error.
14. Do not change chunking or embedding settings without re-running ingest (python -m app.corpus.ingest).
15. Never modify, move, convert, or delete files inside the corpus directory.
