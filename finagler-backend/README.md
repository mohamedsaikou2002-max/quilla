# Finagler Backend

Local FastAPI service. Chat responses come from the configured LM Studio model, with optional retrieval from the local corpus. This backend does not use cloud AI providers or cloud API keys.

## Setup

Use Python 3.12 and open a terminal in this folder. Create and activate the environment, then install the dependencies:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` if needed. Configure the local LM Studio endpoint and model identifiers. Keep `.env` private and out of version control.

## Start

Run this one-line command from this folder:

```powershell
.\run.bat
```

The API listens at `http://127.0.0.1:8000`.

## Troubleshooting

- **Python executable missing or access denied:** install Python 3.12 from [python.org](https://www.python.org/downloads/), then create a fresh `.venv312` with `py -3.12 -m venv .venv312` before installing requirements.
- **LM Studio unavailable:** start the local server at `http://127.0.0.1:1234/v1`, load the chat model, and configure `LMSTUDIO_MODEL` in `.env`.
- **Corpus search or ingestion fails:** verify `CORPUS_DIR` points to the existing corpus folder, `EMBED_MODEL` names a loaded embedding model, and LM Studio serves that embedding model. Then run `python -m app.corpus.ingest` from this folder.
