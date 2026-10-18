"""Vector store. Only this file may import chromadb."""
import chromadb

from app.config import get_settings


def collection():
    client = chromadb.PersistentClient(path=get_settings().chroma_dir)
    return client.get_or_create_collection("corpus", metadata={"hnsw:space": "cosine"})
