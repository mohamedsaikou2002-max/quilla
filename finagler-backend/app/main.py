"""Routes only. No provider logic here: call providers, return results."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings
from app.corpus import ingest, retriever
from app.corpus.store import collection
from app.providers import local_llm

SYSTEM_PROMPT = (
    "You are Finagler, a helpful problem-solving assistant. "
    "Treat corpus excerpts as reference material and distinguish them from your own explanation. "
    "Do not claim to have searched the live web."
)

app = FastAPI(title="Finagler Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    use_corpus: bool = True


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = []
    corpus_error: str | None = None


class SearchRequest(BaseModel):
    query: str
    k: int | None = None


@app.get("/health")
def health():
    s = get_settings()
    return {
        "status": "ok",
        "lmstudio_url": s.lmstudio_base_url,
        "embed_model_configured": bool(s.embed_model),
    }


@app.post("/corpus/ingest")
def corpus_ingest():
    return ingest.ingest_dir()


@app.get("/corpus/stats")
def corpus_stats():
    return {"chunks": collection().count()}


@app.post("/corpus/search")
def corpus_search(body: SearchRequest):
    try:
        hits = retriever.retrieve(body.query, body.k)
    except local_llm.LocalLLMUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    return [
        {"source": h.label, "distance": round(h.distance, 4), "text": h.text} for h in hits
    ]


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    hits, corpus_error = [], None
    if body.use_corpus:
        try:
            hits = retriever.retrieve(body.message)
        except Exception as e:  # corpus problems must never block chat
            corpus_error = str(e)

    system = SYSTEM_PROMPT
    if hits:
        system += "\n\n" + retriever.format_context(hits)

    try:
        reply = local_llm.answer(system, body.message)
    except local_llm.LocalLLMUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))

    return ChatResponse(
        reply=reply,
        sources=[f"C{i}: {h.label}" for i, h in enumerate(hits, start=1)],
        corpus_error=corpus_error,
    )
