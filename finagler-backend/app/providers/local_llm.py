"""Local models (LM Studio): chat + embeddings. Only this file may import openai."""
from openai import OpenAI

from app.config import get_settings


class LocalLLMUnavailable(Exception):
    pass


def _client() -> OpenAI:
    return OpenAI(base_url=get_settings().lmstudio_base_url, api_key="lm-studio")


def answer(system: str, user: str) -> str:
    s = get_settings()
    try:
        client = _client()
        model = s.lmstudio_model
        if not model:
            models = client.models.list().data
            if not models:
                raise LocalLLMUnavailable("No model loaded in LM Studio")
            model = models[0].id
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return r.choices[0].message.content or ""
    except LocalLLMUnavailable:
        raise
    except Exception as e:
        raise LocalLLMUnavailable(
            f"Could not reach LM Studio at {s.lmstudio_base_url}: {e}"
        ) from e


def embed(texts: list[str], kind: str = "document") -> list[list[float]]:
    """kind is 'document' or 'query' (selects the optional prefix)."""
    s = get_settings()
    if not s.embed_model:
        raise LocalLLMUnavailable("EMBED_MODEL is not set")
    prefix = s.embed_doc_prefix if kind == "document" else s.embed_query_prefix
    try:
        client = _client()
        out: list[list[float]] = []
        for i in range(0, len(texts), 32):
            batch = [prefix + t for t in texts[i : i + 32]]
            r = client.embeddings.create(model=s.embed_model, input=batch)
            out.extend(d.embedding for d in sorted(r.data, key=lambda d: d.index))
        return out
    except Exception as e:
        raise LocalLLMUnavailable(
            f"Embedding failed (is the embedding model loaded in LM Studio?): {e}"
        ) from e
