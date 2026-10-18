"""Index everything in CORPUS_DIR. Re-running is safe: each file is replaced, not duplicated.
CLI: python -m app.corpus.ingest"""
import hashlib
from pathlib import Path

from app.config import get_settings
from app.corpus.chunker import chunk_text
from app.corpus.loader import SUPPORTED, load_file
from app.corpus.store import collection
from app.providers import local_llm


def ingest_dir() -> dict:
    root = Path(get_settings().corpus_dir)
    col = collection()
    stats = {"files": 0, "chunks": 0, "skipped": []}
    if not root.exists():
        return stats

    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in SUPPORTED or not path.is_file():
            continue
        rel = str(path.relative_to(root))
        try:
            docs, metas = [], []
            for text, page in load_file(path):
                for n, chunk in enumerate(chunk_text(text)):
                    docs.append(chunk)
                    metas.append({"source": rel, "page": page or 0, "chunk": n})
            if not docs:
                continue
            embeddings = local_llm.embed(docs, kind="document")
        except Exception as e:
            stats["skipped"].append({"file": rel, "error": str(e)})
            continue

        col.delete(where={"source": rel})
        ids = [
            hashlib.sha1(f"{rel}|{m['page']}|{m['chunk']}".encode()).hexdigest()
            for m in metas
        ]
        col.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
        stats["files"] += 1
        stats["chunks"] += len(docs)
    return stats


if __name__ == "__main__":
    print(ingest_dir())
