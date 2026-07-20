# What Would Jesus Do?

A privacy-conscious, source-grounded Bible reflection app. Users describe a situation, the backend retrieves relevant passages from the public-domain World English Bible, and an optional language model turns those passages into a short, cautious reflection. Scripture quotations always come from the local corpus, never from the language model.

The interface is bilingual. Polish is the default and users can switch to English at any time. Polish quotations use the Updated Gdansk Bible under CC BY-ND 4.0; English quotations use the public-domain World English Bible.

## Stack

- Vue 3 + TypeScript + Vite
- FastAPI + Pydantic
- Local hybrid retrieval (BM25-style lexical score plus deterministic semantic hashing)
- Optional Hugging Face chat-completion generation
- 66-book World English Bible (WEB), public domain

The default development mode requires no API key. It returns an extractive reflection based on the highest-ranked passages. Set `HF_TOKEN` and `HF_MODEL` to enable generated prose.

## Run locally

Backend (Python 3.11+):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to FastAPI on port 8000.

## Configuration

Copy `.env.example` to `.env` or export the values before starting FastAPI.

| Variable | Default | Purpose |
| --- | --- | --- |
| `HF_TOKEN` | empty | Enables Hugging Face inference |
| `HF_MODEL` | `Qwen/Qwen3-4B-Instruct-2507` | Chat model ID |
| `HF_BASE_URL` | Hugging Face router | OpenAI-compatible endpoint |
| `ALLOWED_ORIGINS` | localhost Vite URLs | Comma-separated CORS origins |
| `MAX_SITUATION_LENGTH` | `3000` | Input limit |

The application does not persist user situations. Avoid enabling request-body logging at the proxy or hosting-provider layer. A remote inference provider may have its own retention policy.

## Bible data and retrieval

The committed English and Polish corpora were generated from eBible.org's official `engwebp_usfx.zip` and `polubg_usfx.zip` archives. Regenerate either with:

```bash
python backend/scripts/import_usfx.py path/to/engwebp_usfx.xml backend/app/data/web_verses.json
```

Retrieval uses multilingual Sentence Transformers embeddings together with BM25 lexical ranking. It ranks individual verses, filters low-confidence results, and avoids automatically quoting unrelated neighboring verses. The default model is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; set `EMBEDDING_MODEL=BAAI/bge-m3` for a GPU-backed deployment. Build or refresh the local semantic indexes with:

```bash
cd backend
uv run python scripts/build_indexes.py
```

## Verification

```bash
cd backend && pytest
cd frontend && npm run test && npm run build
```

## Product boundary

The result is described as an AI-generated, Bible-grounded reflection—not a certain declaration of what Jesus would do. Emergency, self-harm, and abuse-related language receives an immediate safety message, and the app explicitly does not replace emergency, medical, legal, mental-health, or pastoral help.
