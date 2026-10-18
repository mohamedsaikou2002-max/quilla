"""Query the corpus and format excerpts for the local model."""
from dataclasses import dataclass

from app.config import get_settings
from app.corpus.store import collection
from app.providers import local_llm


@dataclass
class Hit:
    text: str
    source: str
    page: int
    distance: float

    @property
    def label(self) -> str:
        return f"{self.source}, p.{self.page}" if self.page else self.source


def retrieve(query: str, k: int | None = None) -> list[Hit]:
    col = collection()
    total = col.count()
    if total == 0:
        return []
    q = local_llm.embed([query], kind="query")[0]
    r = col.query(
        query_embeddings=[q],
        n_results=min(k or get_settings().top_k, total),
        include=["documents", "metadatas", "distances"],
    )
    return [
        Hit(text=d, source=m["source"], page=m["page"], distance=dist)
        for d, m, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])
    ]


def format_context(hits: list[Hit]) -> str:
    blocks = [f"[C{i}] ({h.label})\n{h.text}" for i, h in enumerate(hits, start=1)]
    return (
        "CORPUS EXCERPTS (authoritative source material; cite as [C1], [C2]... "
        "when you use them):\n\n" + "\n\n".join(blocks)
    )
