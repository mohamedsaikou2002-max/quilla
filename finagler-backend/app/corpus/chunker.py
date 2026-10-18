"""Paragraph-aware chunking with overlap. Blank lines are the split points,
so keep each equation block ($$ ... $$) free of blank lines inside it."""


def chunk_text(text: str, size: int = 3000, overlap: int = 400) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    cur = ""
    for p in paras:
        if len(cur) + len(p) + 2 <= size:
            cur = f"{cur}\n\n{p}" if cur else p
            continue
        if cur:
            chunks.append(cur)
        while len(p) > size:  # single paragraph larger than a chunk
            chunks.append(p[:size])
            p = p[size:]
        cur = p
    if cur:
        chunks.append(cur)

    out = []
    for i, c in enumerate(chunks):
        out.append(chunks[i - 1][-overlap:] + "\n\n" + c if i and overlap else c)
    return out
