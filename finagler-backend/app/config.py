"""All configuration lives here. Nothing else reads os.environ."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    lmstudio_base_url: str
    lmstudio_model: str
    allowed_origins: list[str]
    corpus_dir: str
    chroma_dir: str
    embed_model: str
    embed_doc_prefix: str
    embed_query_prefix: str
    top_k: int

def get_settings() -> Settings:
    return Settings(
        lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
        lmstudio_model=os.getenv("LMSTUDIO_MODEL", ""),
        allowed_origins=[
            o.strip()
            for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ],
        corpus_dir=os.getenv("CORPUS_DIR", "corpus/raw"),
        chroma_dir=os.getenv("CHROMA_DIR", "data/chroma"),
        embed_model=os.getenv("EMBED_MODEL", "").strip(),
        embed_doc_prefix=os.getenv("EMBED_DOC_PREFIX", ""),
        embed_query_prefix=os.getenv("EMBED_QUERY_PREFIX", ""),
        top_k=int(os.getenv("TOP_K", "6")),
    )
